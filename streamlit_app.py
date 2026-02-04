import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.3", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 35px !important; margin-bottom: 15px;
    }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 嚴格執行：header=1 代表從 Row 2 開始讀取標題
        df = pd.read_csv(url, header=1)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"數據連線失敗: {e}")
        return None

df_main = fetch_data("1428367761")

# --- 1. 查詢框架 ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="輸入公豬耳號 (例如: D1397)...", label_visibility="collapsed").strip()

if df_main is not None and search_id:
    # 鎖定搜尋欄位
    target_id_col = 'Tag ID'
    
    if target_id_col in df_main.columns:
        res = df_main[df_main[target_id_col].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            # --- 第一部分：育種資訊 (精確對應 V:AD 範圍) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            
            # 嚴格定義 V:AD 範圍內的 9 個欄位
            v_to_ad_cols = [
                'Grade', 'Breed', 'Tag ID', 'Index Score', 
                'Strategy', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt'
            ]
            
            # 僅選取 V:AD 範圍內存在的欄位，確保不漏掉任何一個
            df_v_ad = res[[c for c in v_to_ad_cols if c in df_main.columns]].copy()
            
            # 數值整數化（無小數點）
            for col in df_v_ad.select_dtypes(include=['number']).columns:
                df_v_ad[col] = df_v_ad[col].astype(int)
            
            st.table(df_v_ad)

            # --- 第二部分：六週採精分析 (BY:CG) ---
            st.markdown("## II. 最近六週採精分析 (LAST 6 WEEKS PERFORMANCE)")
            
            metrics_config = {
                "3. Usage Frequency (Times)": "Usage",
                "4. Sperm Vitality (Avg)": "Vitality",
                "5. Sperm Concentration (Avg)": "Concentration",
                "6. Impurities (%)": "Impurities",
                "7. History Volume (ml)": "Volume"
            }
            weeks = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
            
            for label, key in metrics_config.items():
                base_info = [c for c in ['Breed', 'Gen', 'Tag ID'] if c in df_main.columns]
                week_cols = [c for w in weeks for c in df_main.columns if w in c and key in c]
                
                if week_cols:
                    st.markdown(f"**{label}**")
                    df_trend = res[base_info + week_cols].copy()
                    for col in df_trend.select_dtypes(include=['number']).columns:
                        df_trend[col] = df_trend[col].astype(int)
                    st.table(df_trend)
        else:
            st.error(f"查無耳號: {search_id}")
    else:
        st.error(f"標頭錯誤：在 Row 2 找不到 '{target_id_col}' 欄位。")
else:
    st.info("💡 請輸入公豬耳號。")
