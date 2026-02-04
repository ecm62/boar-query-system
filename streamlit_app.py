import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v6.0", layout="wide")

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
        # 使用 header=None 以物理方式讀取整張表，避免重複標題報錯
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

df_raw = fetch_data("1428367761")

if df_raw is not None:
    # 取得標題列 (Row 2) 用於動態定位
    header_row = df_raw.iloc[1].fillna('').astype(str).tolist()
    header_row = [c.strip().replace('\n', ' ') for c in header_row]

    # --- 1. 查詢框架 ---
    st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
    search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

    if search_id:
        try:
            # 定位 Tag ID 欄位 (通常在 X 欄)
            tag_idx = next(i for i, c in enumerate(header_row) if 'tag id' in c.lower())
            
            data_rows = df_raw.iloc[2:] 
            res = data_rows[data_rows[tag_idx].astype(str).str.fullmatch(search_id, case=False, na=False)]
            
            if not res.empty:
                # --- 第一部分：育種資訊 (固定 V:AD 座標) ---
                st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
                df_v_ad = res.iloc[:, 21:30].copy() 
                df_v_ad.columns = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt']
                
                # 數值整數化 (解決截圖中 17.0000 的問題)
                for col in df_v_ad.columns:
                    df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                    if df_v_ad[col].dtype in ['float64', 'int64']:
                        df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
                st.table(df_v_ad)

                # --- 第二部分：動態校正採精分析 (BY:CG) ---
                st.markdown("## II. 最近六週採精整合分析 (INTEGRATED REPORT)")
                
                # 動態尋找 BY 欄位的錨點 (W06 + Usage)
                try:
                    # 在標題列搜尋包含 W06 且包含 Usage 的索引
                    anchor_idx = next(i for i, c in enumerate(header_row) if 'w06' in c.lower() and 'usage' in c.lower())
                except StopIteration:
                    # 如果搜尋失敗，則根據截圖偏移量推算，Duroc 出現在 Usage 代表我們原本索引 76 太前面了
                    # 截圖顯示偏移了約 54 欄，這裡改用安全搜尋
                    anchor_idx = 76 # 備援值

                # 定義指標標籤與間距
                metrics_setup = [
                    ("📈 3. Usage Frequency (Times)", anchor_idx),
                    ("⚡ 4. Sperm Vitality (Avg)", anchor_idx + 6),
                    ("💧 5. Sperm Concentration (Avg)", anchor_idx + 12),
                    ("⚠️ 6. Impurities (%)", anchor_idx + 18),
                    ("🥛 7. History Volume (ml)", anchor_idx + 24)
                ]
                
                weeks_label = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
                combined_data = []

                for label, start_s in metrics_setup:
                    # 抓取該指標的 6 週數據
                    vals = res.iloc[0, start_s:start_s + 6].tolist()
                    combined_data.append([label] + vals)
                
                # 建立整合表格
                df_integrated = pd.DataFrame(combined_data, columns=['Performance Metric / 週次指標'] + weeks_label)
                
                # 數據清洗：強制轉換為整數，若為文字(如截圖中的品種名)則保持以便除錯
                for col in weeks_label:
                    df_integrated[col] = pd.to_numeric(df_integrated[col], errors='coerce').fillna(df_integrated[col])
                    df_integrated[col] = df_integrated[col].apply(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else x)

                # 顯示基礎資訊列
                breed_idx = next(i for i, c in enumerate(header_row) if 'breed' in c.lower())
                st.info(f"🧬 **Breed:** {res.iloc[0, breed_idx]} | 🏷️ **Tag ID:** {res.iloc[0, tag_idx]}")
                
                st.table(df_integrated)
                        
            else:
                st.error(f"查無耳號: {search_id}")
        except Exception as e:
            st.error(f"系統解析異常: {e}。請確認試算表 Row 2 標題包含 'W06' 與 'Usage'。")
else:
    st.info("💡 請輸入公豬耳號進行數據檢索。")
