import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 專業管理介面設定 (Bilingual UI) ---
st.set_page_config(page_title="GLA Boar System v4", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    h2 { font-size: 16px !important; color: #1E3A8A; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;}
    .stMetric { background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 8px; border-radius: 4px; }
    .stTable { font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 強制從第 2 行開始讀取標頭，解決 Unnamed 錯誤
        df = pd.read_csv(url)
        # 清理欄位名稱中的空格與換行
        df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"連線失敗 GID {gid}: {e}")
        return None

# 讀取兩個分頁
df_info = fetch_data("1251336110")   # Boar info
df_history = fetch_data("1428367761") # BOAR (History)

# --- 1. 查詢框架 (Search Framework) ---
st.markdown("## 🔍 SEARCH BOAR / CARI BOAR")
search_id = st.text_input("", placeholder="Enter Boar ID (e.g. D1397)...", label_visibility="collapsed").strip()

if (df_info is not None and df_history is not None) and search_id:
    # 彈性匹配欄位名稱：解決 KeyError 'Tag ID'
    def find_col(df, keywords):
        for c in df.columns:
            if any(k.lower() in c.lower() for k in keywords): return c
        return None

    tag_col_info = find_col(df_info, ['Tag ID', 'Boar ID', 'Ear Tag'])
    tag_col_hist = find_col(df_history, ['Boar Ear Tag', 'Boar ID', 'Tag ID'])
    
    # 執行搜尋
    if tag_col_info:
        info_res = df_info[df_info[tag_col_info].astype(str).str.contains(search_id, na=False, case=False)]
    else:
        st.error("Error: Could not find ID column in 'Boar info' tab.")
        st.stop()

    if not info_res.empty:
        info_row = info_res.iloc[0]
        
        # 處理日期排序
        date_col = find_col(df_history, ['Date', 'Tarikh'])
        hist_res = pd.DataFrame()
        if tag_col_hist:
            hist_res = df_history[df_history[tag_col_hist].astype(str).str.contains(search_id, na=False, case=False)]
            if date_col and not hist_res.empty:
                hist_res[date_col] = pd.to_datetime(hist_res[date_col], errors='coerce')
                hist_res = hist_res.sort_values(by=date_col, ascending=False)

        # --- 第一排：核心四格指標 ---
        st.markdown("## I. CORE STATUS / STATUS TERAS")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Boar ID", str(info_row.get(tag_col_info, 'N/A')))
        with m2: st.metric("CURRENT GRADE", str(info_row.get('Grade', 'N/A')))
        with m3: st.metric("BREED", str(info_row.get('Breed', 'N/A')))
        with m4: 
            last_date = hist_res[date_col].iloc[0].strftime('%Y-%m-%d') if not hist_res.empty and date_col else "N/A"
            st.metric("LAST RECORD", last_date)

        # --- 第二排：Boar Info (B:J 範圍) ---
        st.markdown("## II. BREEDING METRICS (B:J)")
        # 您要求的 9 個欄位
        target_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt', 'Strategy']
        # 建立動態表格，只顯示存在的欄位
        display_breeding = info_row[[c for c in target_cols if c in info_row.index]].to_frame().T
        st.table(display_breeding)

        # --- 第三排：四周頻率與精蟲資訊 ---
        st.markdown("---")
        st.markdown("## III. 4-WEEK PERFORMANCE & USAGE")
        
        f1, f2, f3, f4 = st.columns(4)
        with f1: st.metric("📈 3. Usage Frequency", str(info_row.get('W01', '0')))
        with f2: st.metric("💧 5. Sperm Conc. (Avg)", str(info_row.get('Avg TSO', 'N/A')))
        with f3: st.metric("⚠️ 6. Impurities (%)", str(info_row.get('Impurities', 'N/A')))
        with f4: st.metric("🥛 7. History Volume", str(info_row.get('Volume', 'N/A')))

        # 顯示四周趨勢 (Breed, Gen, Tag ID, W05-W01)
        st.markdown("### Weekly Trend (W05 - W01)")
        trend_cols = ['Breed', 'Gen', 'Tag ID', 'W05', 'W04', 'W03', 'W02', 'W01']
        display_trend = info_row[[c for c in trend_cols if c in info_row.index]].to_frame().T
        st.table(display_trend)

    else:
        st.error(f"ID '{search_id}' not found in 'Boar info'.")
else:
    st.info("💡 Please enter a Boar ID to begin analysis.")
