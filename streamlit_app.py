import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 專業化介面設定 ---
st.set_page_config(page_title="GLA Boar Performance Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    h2 { font-size: 18px !important; color: #1E3A8A; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-top: 20px; }
    .stTable { font-size: 12px !important; }
    .stMetric { background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 10px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

def load_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        # 修正欄位名稱，移除可能的空白或換行符號
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"連線失敗 (GID: {gid}): {e}")
        return None

# 1. 載入資料 (Boar info: 1251336110, Boar: 1428367761)
df_info = load_data("1251336110") # Boar info 分頁
df_history = load_data("1428367761") # Boar (歷史紀錄) 分頁

# --- TOP: 查詢框架 ---
st.markdown("## 🔍 SEARCH BOAR / CARI BOAR")
search_id = st.text_input("輸入公豬耳號 (Enter Boar ID):", placeholder="例如: L10020...").strip()

if (df_info is not None and df_history is not None) and search_id:
    # 統一轉換日期格式
    if 'Date' in df_history.columns:
        df_history['Date'] = pd.to_datetime(df_history['Date'], errors='coerce')
    
    # 篩選資料
    info_res = df_info[df_info['Tag ID'].astype(str).str.contains(search_id, na=False, case=False)]
    hist_res = df_history[df_history['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]

    if not info_res.empty:
        # 取得最新一筆歷史紀錄
        latest_hist = hist_res.sort_values(by='Date', ascending=False).iloc[0] if not hist_res.empty else None
        info_row = info_res.iloc[0]

        # --- 第一部分：核心狀態 (第一行) ---
        st.markdown("## I. CORE STATUS / STATUS TERAS")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Boar ID", str(info_row.get('Tag ID', 'N/A')))
        with m2:
            st.metric("CURRENT GRADE", str(info_row.get('Grade', 'N/A')))
        with m3:
            st.metric("BREED", str(info_row.get('Breed', 'N/A')))
        with m4:
            last_date = latest_hist['Date'].strftime('%Y-%m-%d') if latest_hist is not None and pd.notnull(latest_hist['Date']) else "N/A"
            st.metric("LAST RECORD", last_date)

        # --- 第二部分：Boar Info 詳細資料 (B:J 範圍) ---
        st.markdown("## II. BREEDING METRICS / METRIK PEMBIAKAN (B:J)")
        # 嚴格對應您要求的欄位：Grade, Breed, Tag ID, Index Score, Avg TSO, Mated, CR %, Avg Birth Wt, Strategy
        target_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt', 'Strategy']
        # 檢查欄位是否存在於資料中，避免 Error
        display_info = info_row[[c for c in target_cols if c in info_row.index]].to_frame().T
        st.table(display_info)

        # --- 第三部分：使用頻率與精蟲資訊 (最新四周) ---
        st.markdown("---")
        st.markdown("## III. 4-WEEK USAGE & SEMEN ANALYSIS / ANALISIS SPERMA")
        
        # 這裡從 Boar info 分頁提取您指定的統計數據 (假設這些統計已在該分頁計算好)
        freq_cols = ['Breed', 'Gen', 'Tag ID', 'W05', 'W04', 'W03', 'W02', 'W01']
        
        # 核心效能指標 (從 info 分頁提取)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("📈 3. Usage Frequency", str(info_row.get('W01', '0')))
        with c2:
            st.metric("💧 5. Sperm Conc.", str(info_row.get('Avg TSO', 'N/A')))
        with c3:
            # 假設 Impurities 與 Volume 存在於您的 Info 表中，若無則顯示 N/A
            st.metric("⚠️ 6. Impurities (%)", str(info_row.get('Impurities', 'N/A')))
        with m4:
            st.metric("🥛 7. History Volume", str(info_row.get('Volume', 'N/A')))

        # 顯示週次歷史表格
        st.markdown("### Weekly Usage History / Sejarah Penggunaan Mingguan")
        weekly_display = info_row[[c for c in freq_cols if c in info_row.index]].to_frame().T
        st.table(weekly_display)

    else:
        st.error("找不到該公豬編號 (Boar ID Not Found)")
else:
    if not search_id:
        st.info("請輸入公豬耳號以顯示育種與作業分析報告。")
