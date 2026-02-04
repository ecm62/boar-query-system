import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.9", layout="wide")

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
        # 使用 header=None 讀取，以處理粘連的原始數據
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

df_raw = fetch_data("1428367761")

if df_raw is not None:
    # --- 取得標題行 (Row 2, 索引 1) 並清理 ---
    header_row = df_raw.iloc[1].fillna('').astype(str).tolist()
    header_row = [c.strip().replace('\n', ' ') for c in header_row]

    # --- 1. 查詢框架 ---
    st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
    search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

    if search_id:
        try:
            # 找到 Tag ID 的正確物理索引 (搜尋名稱包含 'Tag ID')
            tag_idx = next(i for i, c in enumerate(header_row) if 'tag id' in c.lower())
            
            data_rows = df_raw.iloc[2:] 
            res = data_rows[data_rows[tag_idx].astype(str).str.fullmatch(search_id, case=False, na=False)]
            
            if not res.empty:
                # --- 第一部分：育種資訊 (保留設定：V:AD) ---
                st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
                # 抓取索引 21 到 29 (物理座標 V 到 AD)
                df_v_ad = res.iloc[:, 21:30].copy() 
                df_v_ad.columns = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt']
                
                for col in df_v_ad.columns:
                    df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                    if df_v_ad[col].dtype in ['float64', 'int64']:
                        df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
                st.table(df_v_ad)

                # --- 第二部分：動態校正後的採精整合報表 ---
                st.markdown("## II. 最近六週採精整合分析 (INTEGRATED REPORT)")
                
                # 自動搜尋 BY 欄位 (Usage Frequency W06) 的起始索引
                try:
                    start_anchor = next(i for i, c in enumerate(header_row) if 'w06' in c.lower() and 'usage' in c.lower())
                except StopIteration:
                    start_anchor = 76 # 若搜尋不到則退回原設值，但通常會搜尋到
                
                # 建立指標映射與間距 (每組指標間隔 6 欄)
                metrics_setup = [
                    ("📈 3. Usage Frequency (Times)", start_anchor),
                    ("⚡ 4. Sperm Vitality (Avg)", start_anchor + 6),
                    ("💧 5. Sperm Concentration (Avg)", start_anchor + 12),
                    ("⚠️ 6. Impurities (%)", start_anchor + 18),
                    ("🥛 7. History Volume (ml)", start_anchor + 24)
                ]
                
                weeks_label = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
                combined_data = []

                for label, s_idx in metrics_setup:
                    # 抓取該標的的 6 欄數據並清理
                    raw_values = res.iloc[0, s_idx:s_idx + 6].tolist()
                    combined_data.append([label] + raw_values)
                
                # 轉換為整合表格
                df_final = pd.DataFrame(combined_data, columns=['Performance Metric / 週次指標'] + weeks_label)
                
                # 數據清洗：解決截圖中的文字偏移問題
                for col in weeks_label:
                    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(df_final[col])
                    df_final[col] = df_final[col].apply(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else x)

                # 顯示 Breed 與 Tag ID 的基礎資訊
                breed_idx = next(i for i, c in enumerate(header_row) if 'breed' in c.lower())
                st.info(f"🧬 **Breed:** {res.iloc[0, breed_idx]} | 🏷️ **Tag ID:** {res.iloc[0, tag_idx]}")
                
                st.table(df_final)
                        
            else:
                st.error(f"查無耳號: {search_id}")
        except Exception as e:
            st.error(f"欄位定位失敗: {e}。請檢查試算表標題結構。")
else:
    st.info("💡 請輸入公豬耳號。")
