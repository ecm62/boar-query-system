import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 專業化介面設定 ---
st.set_page_config(page_title="GLA Boar System", layout="wide")

# CSS 優化：縮小字體、緊湊排版，符合商業報表風格
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    h2 { font-size: 18px !important; color: #1E3A8A; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-bottom: 10px; }
    .stTable { font-size: 12px !important; }
    .stDataFrame { font-size: 12px !important; }
    .stMetric { background-color: #F8FAFC; border: 1px solid #CBD5E1; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    # Google Sheets 連結與分頁 ID
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        # 直接讀取全表
        df = pd.read_csv(url)
        # 強制轉換日期欄位，確保排序功能正常
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

# --- 第一層：查詢框架 (Search Framework) ---
df = load_data()

st.markdown("## SEARCH / CARIAN (查詢)")
search_id = st.text_input("輸入公豬耳號 (Enter Boar ID):", placeholder="例如: L10020...").strip()

if df is not None and search_id:
    # 根據耳號過濾數據
    result = df[df['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]
    
    if not result.empty:
        # 排序：確保最新的一筆在最上面
        result = result.sort_values(by='Date', ascending=False)
        latest_row = result.iloc[0]
        
        # --- 第二層：I. Grading Indicators (V:AD 範圍) ---
        st.markdown("## I. GRADING INDICATORS / PENUNJUK GRED")
        
        # 提取 V 到 AD 欄位 (索引 21 到 30)
        grade_cols = list(df.columns[21:30])
        
        # 儀表板核心指標
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("CURRENT GRADE (等級)", str(latest_row.get('Grade', 'N/A')))
        with m2:
            st.metric("BREED (品種)", str(latest_row.get('Breed', 'N/A')))
        with m3:
            st.metric("LAST RECORD (最新紀錄)", latest_row['Date'].strftime('%Y-%m-%d') if pd.notnull(latest_row['Date']) else "N/A")

        # 呈現 V:AD 詳細數據表
        st.table(latest_row[grade_cols].to_frame().T)

        st.markdown("---")

        # --- 第三層：使用頻率與紀錄 (BY:CE 範圍) ---
        # 1. 計算過去 4 週的使用頻率
        four_weeks_limit = datetime.now() - timedelta(weeks=4)
        recent_activity = result[result['Date'] >= four_weeks_limit]
        usage_freq = len(recent_activity)

        st.markdown(f"## USAGE FREQUENCY (4 WEEKS): :red[{usage_freq} TIMES / 次]")
        
        # 2. 顯示活動紀錄 (BY:CE)
        st.markdown("## II. ACTIVITY LOG / REKOD AKTIVITI")
        
        # 提取 BY 到 CE 欄位 (索引 76 到 83)
        history_cols = list(df.columns[76:83])
        if not recent_activity.empty:
            # 呈現表格，並隱藏序號列
            st.dataframe(recent_activity[history_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("過去 4 週內無使用紀錄。")

    else:
        st.error("找不到該公豬編號，請重新確認。")
else:
    if not search_id:
        st.info("系統就緒，請在上方輸入公豬耳號。")
