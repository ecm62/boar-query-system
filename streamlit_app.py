import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v7.0", layout="wide")

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
        # header=None 以物理索引操作，避免標題粘連報錯
        df = pd.read_csv(url, header=None)
        # 移除所有數據中可能的隱藏空格
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"數據加載失敗: {e}")
        return None

# 讀取數據 (分頁 GID: 1428367761)
df_raw = fetch_data("1428367761")

if df_raw is not None:
    st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
    search_id = st.text_input("", placeholder="輸入耳號 (例如: D1401)...", label_visibility="collapsed").strip()

    if search_id:
        try:
            # 數據從 Row 3 開始 (索引 2)
            data_rows = df_raw.iloc[2:].copy()
            
            # --- 第一部分：育種資訊 (維持固定 V:AD 座標，索引 21-29) ---
            # 搜尋耳號欄位：鎖定索引 23 (物理 X 欄，對應第一表 Tag ID)
            res_info = data_rows[data_rows[23].astype(str).str.fullmatch(search_id, case=False, na=False)]
            
            if not res_info.empty:
                st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
                df_v_ad = res_info.iloc[[0], 21:30].copy() 
                df_v_ad.columns = [
                    'Grade', 'Breed', 'Tag ID', 'Index Score', 
                    'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt'
                ]
                
                # 數據整數化處理
                for col in df_v_ad.columns:
                    df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                    if df_v_ad[col].dtype in ['float64', 'int64']:
                        df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
                st.table(df_v_ad)
            
            # --- 第二部分：最近 10 次採精結果 (A:K 範圍) ---
            # 搜尋耳號欄位：鎖定索引 2 (物理 C 欄，Boar Ear Tag)
            res_semen = data_rows[data_rows[2].astype(str).str.fullmatch(search_id, case=False, na=False)]
            
            if not res_semen.empty:
                st.markdown("## II. 最近 10 次採精紀錄 (LAST 10 EXTRACTIONS)")
                
                # 選取 A:K 範圍 (索引 0 到 10)
                df_a_k = res_semen.iloc[:, 0:11].copy()
                df_a_k.columns = [
                    'Date', 'Breed', 'Boar Ear Tag', 
                    'Volume Collected (ml)', 'Odor (Bau)', 'Color (Warna)', 
                    'Vitality (Aktiviti)', 'Concentration (x100m)', 
                    'Morphology Impurities (%)', 'Volume After Dilution (ml)', 'Other Record'
                ]
                
                # 日期排序：確保 Date 欄位 (索引 0) 為時間格式
                df_a_k['Date'] = pd.to_datetime(df_a_k['Date'], errors='coerce')
                df_a_k = df_a_k.sort_values(by='Date', ascending=False).head(10)
                
                # 格式化日期顯示
                df_a_k['Date'] = df_a_k['Date'].dt.strftime('%Y-%m-%d')
                
                # 數值精簡化 (濃度與雜質保留必要格式，其餘整數化)
                for col in df_a_k.columns:
                    if col not in ['Date', 'Breed', 'Boar Ear Tag', 'Odor (Bau)', 'Color (Warna)', 'Other Record']:
                        df_a_k[col] = pd.to_numeric(df_a_k[col], errors='coerce').fillna(0)
                        # 若無小數則轉整數
                        df_a_k[col] = df_a_k[col].apply(lambda x: int(x) if x == int(x) else round(x, 2))

                st.table(df_a_k)
            else:
                st.warning(f"在採精紀錄 (A:K) 中查無耳號: {search_id}")
                
            if res_info.empty and res_semen.empty:
                st.error(f"系統查無此公豬耳號之任何數據。")

        except Exception as e:
            st.error(f"解析錯誤: {e}")
else:
    st.info("💡 請輸入公豬耳號。")
