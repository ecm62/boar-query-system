import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.8", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 30px !important; margin-bottom: 15px;
    }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    /* 加強指標名稱的辨識度 */
    .metric-label { font-weight: bold; color: #334155; text-align: left !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 維持物理讀取模式
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
        data_rows = df_raw.iloc[2:] 
        res = data_rows[data_rows[23].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            # --- 第一部分：育種資訊 (保留設定：V:AD) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            df_v_ad = res.iloc[:, 21:30].copy() 
            df_v_ad.columns = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt']
            
            for col in df_v_ad.columns:
                df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                if df_v_ad[col].dtype in ['float64', 'int64']:
                    df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
            st.table(df_v_ad)

            # --- 第二部分：優化後的六週整合報表 (BY:CG) ---
            st.markdown("## II. 最近六週採精整合分析 (LAST 6 WEEKS INTEGRATED REPORT)")
            
            # 取得基礎資訊
            breed_val = res.iloc[0, 22]
            tag_val = res.iloc[0, 23]
            
            # 建立表頭資訊
            st.info(f"🧬 **Breed:** {breed_val} | 🏷️ **Tag ID:** {tag_val}")

            # 定義 5 個標的與對應起始索引 (BY 索引為 76)
            metrics_setup = [
                ("📈 3. Usage Frequency (Times)", 76),
                ("⚡ 4. Sperm Vitality (Avg)", 82),
                ("💧 5. Sperm Concentration (Avg)", 88),
                ("⚠️ 6. Impurities (%)", 94),
                ("🥛 7. History Volume (ml)", 100)
            ]
            
            weeks_label = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
            
            # 建立整合 DataFrame
            combined_data = []
            for label, start_idx in metrics_setup:
                # 抓取該標的的 6 欄數據
                row_data = res.iloc[0, start_idx:start_idx + 6].tolist()
                combined_data.append([label] + row_data)
            
            # 轉換為 DataFrame 顯示
            df_final = pd.DataFrame(combined_data, columns=['Performance Metric / 週次指標'] + weeks_label)
            
            # 數值整數化
            for col in weeks_label:
                df_final[col] = pd.to_numeric(df_final[col], errors='ignore')
                # 若是數字則轉整數，若是文字(如 '.') 則保持原樣
                df_final[col] = df_final[col].apply(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else x)

            # 輸出整合表格
            st.table(df_final)
                    
        else:
            st.error(f"查無耳號: {search_id}")
    except Exception as e:
        st.error(f"解析錯誤: {e}")
else:
    st.info("💡 請輸入公豬耳號。")
