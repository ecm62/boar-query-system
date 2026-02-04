import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.2", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 35px !important; margin-bottom: 15px;
    }
    /* 全表格置中對齊 */
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 根據您的要求：直接指定 header=1 (對應 Excel 的 Row 2)
        df = pd.read_csv(url, header=1)
        
        # 僅進行基礎清洗，不改變名稱結構，確保對應您試算表中的精確標題
        df.columns = [str(c).strip() for c in df.columns]
        
        return df.fillna(0)
    except Exception as e:
        st.error(f"數據連線失敗: {e}")
        return None

# 讀取數據 (分頁 GID: 1428367761)
df_main = fetch_data("1428367761")

# --- 查詢框架 ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="輸入公豬耳號 (例如: D1397)...", label_visibility="collapsed").strip()

if df_main is not None and search_id:
    # 直接指定搜尋欄位為 'Tag ID'
    target_id_col = 'Tag ID'
    
    if target_id_col in df_main.columns:
        # 執行精確篩選
        res = df_main[df_main[target_id_col].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            # --- 第一部分：育種資訊 (對應 V:AE 內容) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            # 依據您的需求清單：Grade, Breed, Tag ID, Index Score, Strategy, Avg TSO, Mated, CR %, Avg Birth Wt, Data Source
            breeding_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt', 'Data Source']
            
            # 過濾確保只顯示存在的欄位，並強制轉整數
            final_breeding = res[[c for c in breeding_cols if c in df_main.columns]].copy()
            for col in final_breeding.select_dtypes(include=['number']).columns:
                final_breeding[col] = final_breeding[col].astype(int)
            
            st.table(final_breeding)

            # --- 第二部分：六週採精表現 (對應 BY:CG 內容) ---
            st.markdown("## II. 最近六週採精分析 (LAST 6 WEEKS PERFORMANCE)")
            
            # 依據關鍵字精確提取六週趨勢
            metrics_config = {
                "3. Usage Frequency (Times)": "Usage",
                "4. Sperm Vitality (Avg)": "Vitality",
                "5. Sperm Concentration (Avg)": "Concentration",
                "6. Impurities (%)": "Impurities",
                "7. History Volume (ml)": "Volume"
            }
            weeks = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
            
            for label, key in metrics_config.items():
                # 提取 Breed, Gen, Tag ID 做為前綴
                base_info = [c for c in ['Breed', 'Gen', 'Tag ID'] if c in df_main.columns]
                # 提取對應週次欄位
                week_cols = [c for w in weeks for c in df_main.columns if w in c and key in c]
                
                if week_cols:
                    st.markdown(f"**{label}**")
                    df_trend = res[base_info + week_cols].copy()
                    # 數值整數化
                    for col in df_trend.select_dtypes(include=['number']).columns:
                        df_trend[col] = df_trend[col].astype(int)
                    st.table(df_trend)
        else:
            st.error(f"未能在 'Tag ID' 欄位中找到耳號: {search_id}")
    else:
        st.error(f"錯誤：在 Row 2 標頭中找不到名為 'Tag ID' 的欄位。目前可用的欄位有：{list(df_main.columns)[:20]}...")
else:
    st.info("💡 請輸入公豬耳號開始查詢。")
