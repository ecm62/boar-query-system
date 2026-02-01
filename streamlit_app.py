import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 專業化 UI 設定 ---
st.set_page_config(page_title="GLA Boar Intelligence", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    h2 { font-size: 16px !important; color: #1E3A8A; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-bottom: 5px; margin-top: 15px; }
    .stTable { font-size: 11px !important; }
    .stMetric { background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 8px; }
    div[data-testid="stExpander"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600) # 快取 10 分鐘，減少重複請求導致的 400 錯誤
def fetch_google_sheet(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    # 使用更穩定的匯出連結格式
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        # 移除欄位名稱的空白與換行
        df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"連線失敗 (GID: {gid})。請確認試算表權限已開啟「知道連結的人均可檢視」。錯誤: {e}")
        return None

# 1. 載入分頁數據
df_info = fetch_google_sheet("1251336110") # Boar info
df_history = fetch_google_sheet("1428367761") # BOAR (歷史紀錄)

# --- 頂部：查詢框架 ---
st.markdown("## 🔍 SEARCH BOAR / CARI BOAR")
search_id = st.text_input("", placeholder="輸入耳號 (e.g. L10020)...", label_visibility="collapsed").strip()

if (df_info is not None and df_history is not None) and search_id:
    # 資料處理：日期轉換
    if 'Date' in df_history.columns:
        df_history['Date'] = pd.to_datetime(df_history['Date'], errors='coerce')
    
    # 篩選數據 (不分大小寫)
    # 假設 Boar info 使用 'Tag ID'，BOAR 分頁使用 'Boar Ear Tag'
    info_match = df_info[df_info['Tag ID'].astype(str).str.contains(search_id, na=False, case=False)]
    hist_match = df_history[df_history['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]

    if not info_match.empty:
        info_data = info_match.iloc[0]
        latest_hist = hist_match.sort_values(by='Date', ascending=False).iloc[0] if not hist_match.empty else None

        # --- 第一行：核心狀態指標 ---
        st.markdown("## I. CORE STATUS / STATUS TERAS")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Boar ID", str(info_data.get('Tag ID', 'N/A')))
        with c2:
            st.metric("CURRENT GRADE", str(info_data.get('Grade', 'N/A')))
        with c3:
            st.metric("BREED", str(info_data.get('Breed', 'N/A')))
        with c4:
            last_date = latest_hist['Date'].strftime('%Y-%m-%d') if latest_hist is not None and pd.notnull(latest_hist['Date']) else "N/A"
            st.metric("LAST RECORD", last_date)

        # --- 第二行：育種詳細資料 (B:J 範圍) ---
        st.markdown("## II. BOAR INFO: BREEDING METRICS (B:J)")
        # 嚴格對應要求的 9 個欄位
        breeding_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt', 'Strategy']
        # 建立展示用的 DataFrame
        display_breeding = info_data[[c for c in breeding_cols if c in info_data.index]].to_frame().T
        st.table(display_breeding)

        # --- 第三行：四周頻率與精蟲資訊 ---
        st.markdown("---")
        st.markdown("## III. 4-WEEK USAGE & SEMEN ANALYSIS")
        
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.metric("📈 3. Usage Frequency", str(info_data.get('W01', '0')))
        with f2:
            st.metric("💧 5. Sperm Conc. (Avg)", str(info_data.get('Avg TSO', 'N/A')))
        with f3:
            st.metric("⚠️ 6. Impurities (%)", str(info_data.get('Impurities', 'N/A')))
        with f4:
            st.metric("🥛 7. History Volume", str(info_data.get('Volume', 'N/A')))

        # 顯示週次歷史表格 (Breed, Gen, Tag ID, W05-W01)
        st.markdown("### Weekly Usage Trend (W05 - W01)")
        week_cols = ['Breed', 'Gen', 'Tag ID', 'W05', 'W04', 'W03', 'W02', 'W01']
        display_weeks = info_data[[c for c in week_cols if c in info_data.index]].to_frame().T
        st.table(display_weeks)

    else:
        st.error(f"找不到 ID: {search_id}。請檢查 Boar info 分頁中的 Tag ID 是否正確。")
else:
    if not search_id:
        st.info("💡
