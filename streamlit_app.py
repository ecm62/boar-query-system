import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.7", layout="wide")

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
        # 維持 header=None 的物理讀取模式，避免標題重複報錯
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

df_raw = fetch_data("1428367761")

# --- 1. 查詢框架 ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

if df_raw is not None and search_id:
    try:
        data_rows = df_raw.iloc[2:] # 數據從 Row 3 開始 (索引 2)
        # 搜尋索引 23 (X 欄，Tag ID)
        res = data_rows[data_rows[23].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            # --- 第一部分：育種資訊 (保留設定：V:AD, 索引 21:30) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            df_v_ad = res.iloc[:, 21:30].copy() 
            df_v_ad.columns = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt']
            
            for col in df_v_ad.columns:
                df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                if df_v_ad[col].dtype in ['float64', 'int64']:
                    df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
            st.table(df_v_ad)

            # --- 第二部分：六週採精分析 (BY1:CG 範圍，索引 76 開始) ---
            st.markdown("## II. 最近六週採精分析 (LAST 6 WEEKS PERFORMANCE)")
            
            # 定義顯示週次與基礎資訊 (Breed: 索引 22, Tag ID: 索引 23)
            base_cols = [22, 23]
            base_names = ['Breed', 'Tag ID']
            weeks_header = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']

            # 定義 5 個標的對應的起始物理索引位置 (假設 BY 之後每 6 欄為一個標的)
            # 依據 Excel 規律：BY 欄是索引 76
            metrics_setup = [
                ("📈 3. Usage Frequency (Times)", 76),
                ("⚡ 4. Sperm Vitality (Avg)", 82),
                ("💧 5. Sperm Concentration (Avg)", 88),
                ("⚠️ 6. Impurities (%)", 94),
                ("🥛 7. History Volume (ml)", 100)
            ]

            for label, start_idx in metrics_setup:
                st.markdown(f"**{label}**")
                # 抓取：基礎資訊 + 該標的的連續 6 欄數據
                target_range = list(base_cols) + list(range(start_idx, start_idx + 6))
                
                # 檢查索引是否超出範圍
                target_range = [i for i in target_range if i < len(df_raw.columns)]
                
                df_metric = res.iloc[:, target_range].copy()
                
                # 重新設定表頭
                df_metric.columns = base_names + weeks_header[:len(df_metric.columns)-2]

                # 數值整數化
                for col in df_metric.columns:
                    df_metric[col] = pd.to_numeric(df_metric[col], errors='ignore')
                    if df_metric[col].dtype in ['float64', 'int64']:
                        df_metric[col] = df_metric[col].fillna(0).astype(int)
                
                st.table(df_metric)
                    
        else:
            st.error(f"查無耳號: {search_id}")
    except Exception as e:
        st.error(f"解析錯誤: {e}")
else:
    st.info("💡 請輸入公豬耳號。")
