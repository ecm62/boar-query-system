import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v6.5", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 30px !important; margin-bottom: 15px;
    }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    # 使用 gviz API 以原始格式讀取
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # header=None 以物理索引操作，避免標題粘連報錯
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"數據加載失敗: {e}")
        return None

# 讀取 BOAR 分頁 (GID: 1428367761)
df_raw = fetch_data("1428367761")

if df_raw is not None:
    st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
    search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

    if search_id:
        try:
            # 數據從 Row 3 開始 (索引 2)
            data_rows = df_raw.iloc[2:].copy()
            
            # 搜尋耳號欄位：鎖定索引 23 (物理 X 欄)
            res = data_rows[data_rows[23].astype(str).str.fullmatch(search_id, case=False, na=False)]
            
            if not res.empty:
                # --- 第一部分：表一恢復 (V:AD 座標 21-29) ---
                st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
                df_v_ad = res.iloc[:, 21:30].copy() 
                df_v_ad.columns = [
                    'Grade', 'Breed', 'Tag ID', 'Index Score', 
                    'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt'
                ]
                
                # 數據清理與無小數點顯示
                for col in df_v_ad.columns:
                    df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                    if df_v_ad[col].dtype in ['float64', 'int64']:
                        df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
                st.table(df_v_ad)

                # --- 第二部分：表二整併優化 (座標起點 79) ---
                st.markdown("## II. 最近六週採精整合分析 (INTEGRATED REPORT)")
                
                # 顯示基礎資訊
                st.info(f"🧬 **Breed:** {res.iloc[0, 22]} | 🏷️ **Tag ID:** {res.iloc[0, 23]}")

                # 數據起點精確校正：CB 欄 (索引 79)
                anchor_idx = 79 
                
                metrics_setup = [
                    ("📈 3. Usage Frequency (Times)", anchor_idx),
                    ("⚡ 4. Sperm Vitality (Avg)", anchor_idx + 6),
                    ("💧 5. Sperm Concentration (Avg)", anchor_idx + 12),
                    ("⚠️ 6. Impurities (%)", anchor_idx + 18),
                    ("🥛 7. History Volume (ml)", anchor_idx + 24)
                ]
                
                weeks_label = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
                combined_data = []

                for label, s_idx in metrics_setup:
                    # 抓取 6 欄數據並將其轉為數值
                    row_vals = res.iloc[0, s_idx:s_idx + 6].tolist()
                    combined_data.append([label] + row_vals)
                
                df_final = pd.DataFrame(combined_data, columns=['Performance Metric / 週次指標'] + weeks_label)
                
                # 數值整數化與處理非數值內容
                for col in weeks_label:
                    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
                    df_final[col] = df_final[col].astype(int)

                st.table(df_final)
                        
            else:
                st.error(f"查無耳號: {search_id}")
        except Exception as e:
            st.error(f"解析錯誤: {e}")
else:
    st.info("💡 請輸入公豬耳號。")
