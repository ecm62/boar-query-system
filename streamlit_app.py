import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.4", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 35px !important; margin-bottom: 15px;
    }
    /* 全表格數據置中 */
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 依據要求從 Row 2 開始讀取 (header=1)
        df = pd.read_csv(url, header=1)
        # 清理標題：移除換行與多餘空格
        df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

df_main = fetch_data("1428367761")

# --- 查詢框架 ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="輸入公豬耳號 (例如: D1397)...", label_visibility="collapsed").strip()

if df_main is not None and search_id:
    # 定義 ID 搜尋欄位
    target_id_col = 'Tag ID'
    
    if target_id_col in df_main.columns:
        res = df_main[df_main[target_id_col].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            # --- 第一部分：育種資訊 (精確對應 V:AD) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            
            # 建立映射表：確保程式能對應到截圖中可能變異的名稱
            # 依序為: Grade, Breed, Tag ID, Index Score, Strategy (策略), Avg TSO, Mated, CR %, Avg Birth Wt
            mapping = {
                'Grade': 'Grade',
                'Breed': 'Breed',
                'Tag ID': 'Tag ID',
                'Index Score': 'Index Score',
                'Strategy': 'Strategy (策略)', 
                'Avg TSO': 'Avg TSO',
                'Mated': 'Mated',
                'CR %': 'CR %',
                'Avg Birth Wt': 'Avg Birth Wt'
            }
            
            # 找出實際存在的欄位
            actual_cols = []
            for display_name, csv_name in mapping.items():
                found = [c for c in df_main.columns if csv_name.lower() in c.lower()]
                if found: actual_cols.append(found[0])

            if actual_cols:
                df_v_ad = res[actual_cols].copy()
                # 數據整數化 (解決截圖中 17.0000 的問題)
                for col in df_v_ad.select_dtypes(include=['number']).columns:
                    df_v_ad[col] = df_v_ad[col].astype(int)
                st.table(df_v_ad)
            else:
                st.error("無法匹配 V:AD 範圍內的欄位。")

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
                week_cols = [c for w in weeks for c in df_main.columns if w in c and key.lower() in c.lower()]
                
                if week_cols:
                    st.markdown(f"**{label}**")
                    df_trend = res[base_info + week_cols].copy()
                    for col in df_trend.select_dtypes(include=['number']).columns:
                        df_trend[col] = df_trend[col].astype(int)
                    st.table(df_trend)
        else:
            st.error(f"查無耳號: {search_id}")
    else:
        st.error(f"標頭錯誤：找不到 '{target_id_col}'。")
else:
    st.info("💡 請輸入公豬耳號。")
