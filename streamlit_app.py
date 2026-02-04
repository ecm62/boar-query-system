import streamlit as st
import pandas as pd

# --- 專業管理介面設定 (Bilingual UI) ---
st.set_page_config(page_title="GLA Boar System v5", layout="wide")

# CSS 注入：解決遮擋、字體大小與置中對齊
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .block-container { padding-top: 2rem; }
    
    /* 標題優化：增加頂部間距防止遮擋 */
    h2 { 
        font-size: 18px !important; 
        color: #1E3A8A; 
        font-weight: bold; 
        border-left: 5px solid #1E3A8A; 
        padding: 10px 0 10px 15px; 
        margin-top: 30px !important; 
        margin-bottom: 15px;
    }
    
    /* 強制表格內容與標頭全部置中 */
    .stTable td, .stTable th {
        text-align: center !important;
        vertical-align: middle !important;
    }
    
    /* 指標卡片美化 */
    .stMetric { 
        background-color: #F8FAFC; 
        border: 1px solid #CBD5E1; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
        # 根據要求：數值處理為整數（無小數點）
        return df.fillna(0)
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

# 讀取數據 (分頁：BOAR)
df_main = fetch_data("1428367761")

# --- 1. 查詢框架 (Search Framework) ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="Enter Boar ID (e.g. D1397)...", label_visibility="collapsed").strip()

if df_main is not None and search_id:
    # 定義 ID 欄位
    id_col = next((c for c in df_main.columns if 'tag id' in c.lower() or 'boar id' in c.lower()), None)
    
    if id_col:
        # 精確匹配
        res = df_main[df_main[id_col].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            row = res.iloc[0]

            # --- 第一部分：育種資訊 (V:AE) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            breeding_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt', 'Data Source']
            
            # 確保數據類型為整數並置中顯示
            display_breeding = res[[c for c in breeding_cols if c in res.columns]].copy()
            # 將數值欄位轉為整數格式
            for col in display_breeding.select_dtypes(include=['number']).columns:
                display_breeding[col] = display_breeding[col].astype(int)
            
            st.table(display_breeding)

            # --- 第二部分：六週採精表現 (BY:CG) ---
            st.markdown("## II. 最近六週採精分析 (LAST 6 WEEKS PERFORMANCE)")
            st.caption("包含：📈 使用頻率、⚡ 精子活力、💧 精子濃度、⚠️ 雜質率、🥛 歷史產精量")
            
            # 定義六週指標與關鍵字
            metrics = {
                "Usage Frequency": "Usage",
                "Sperm Vitality": "Vitality",
                "Sperm Concentration": "Concentration",
                "Impurities (%)": "Impurities",
                "History Volume (ml)": "Volume"
            }
            weeks = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
            
            for label, key in metrics.items():
                target_cols = ['Breed', 'Gen', 'Tag ID']
                # 尋找對應週次的欄位
                week_cols = [c for w in weeks for c in df_main.columns if w in c and key.lower() in c.lower()]
                
                if week_cols:
                    st.markdown(f"**{label} 趨勢**")
                    temp_df = res[target_cols + week_cols].copy()
                    # 數值格式化
                    for col in temp_df.select_dtypes(include=['number']).columns:
                        temp_df[col] = temp_df[col].astype(int)
                    st.table(temp_df)
        else:
            st.error(f"未找到耳號: {search_id}")
    else:
        st.error("數據源中缺少 'Tag ID' 欄位。")
else:
    st.info("💡 請輸入公豬耳號以啟動數據分析。")
