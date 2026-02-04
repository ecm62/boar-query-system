import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v6.1", layout="wide")

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
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # header=None 以處理粘連數據
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

df_raw = fetch_data("1428367761")

if df_raw is not None:
    # 取得標題列 (Row 2, 索引 1)
    header_row = df_raw.iloc[1].fillna('').astype(str).tolist()
    header_row = [c.strip().replace('\n', ' ') for c in header_row]

    st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
    search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

    if search_id:
        try:
            # 1. 定位 Tag ID 欄位
            tag_idx = next(i for i, c in enumerate(header_row) if 'tag id' in c.lower())
            
            data_rows = df_raw.iloc[2:] 
            res = data_rows[data_rows[tag_idx].astype(str).str.fullmatch(search_id, case=False, na=False)]
            
            if not res.empty:
                # --- 第一部分：育種資訊 (精確搜尋標題) ---
                st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
                
                # 定義目標欄位名稱
                v_ad_targets = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt']
                v_ad_indices = []
                for target in v_ad_targets:
                    # 彈性匹配，解決粘連問題
                    idx = next((i for i, c in enumerate(header_row) if target.lower() in c.lower()), None)
                    if idx is not None: v_ad_indices.append(idx)

                df_v_ad = res.iloc[:, v_ad_indices].copy()
                df_v_ad.columns = v_ad_targets[:len(v_ad_indices)]
                
                # 數據整數化
                for col in df_v_ad.columns:
                    df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                    if df_v_ad[col].dtype in ['float64', 'int64']:
                        df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
                st.table(df_v_ad)

                # --- 第二部分：最近六週採精整合分析 ---
                st.markdown("## II. 最近六週採精整合分析 (INTEGRATED REPORT)")
                
                # 取得基礎資訊
                breed_idx = next(i for i, c in enumerate(header_row) if 'breed' in c.lower())
                st.info(f"🧬 **Breed:** {res.iloc[0, breed_idx]} | 🏷️ **Tag ID:** {res.iloc[0, tag_idx]}")

                # 動態搜尋各指標起始點 (W06)
                metrics_keys = [
                    ("📈 3. Usage Frequency (Times)", "usage"),
                    ("⚡ 4. Sperm Vitality (Avg)", "vitality"),
                    ("💧 5. Sperm Concentration (Avg)", "concentration"),
                    ("⚠️ 6. Impurities (%)", "impurities"),
                    ("🥛 7. History Volume (ml)", "volume")
                ]
                
                weeks_label = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
                combined_data = []

                for label, key in metrics_keys:
                    # 尋找該指標 W06 的欄位索引
                    try:
                        start_idx = next(i for i, c in enumerate(header_row) if 'w06' in c.lower() and key in c.lower())
                        vals = res.iloc[0, start_idx:start_idx + 6].tolist()
                        combined_data.append([label] + vals)
                    except StopIteration:
                        combined_data.append([label] + ["N/A"]*6)

                df_final = pd.DataFrame(combined_data, columns=['Performance Metric / 週次指標'] + weeks_label)
                
                # 最終數據清理與整數化
                for col in weeks_label:
                    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(df_final[col])
                    df_final[col] = df_final[col].apply(lambda x: int(float(x)) if isinstance(x, (int, float, str)) and str(x).replace('.','').isdigit() else x)

                st.table(df_final)
                        
            else:
                st.error(f"查無耳號: {search_id}")
        except Exception as e:
            st.error(f"定位失敗: {e}")
else:
    st.info("💡 請輸入公豬耳號。")
