import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System", layout="wide")

# CSS 優化：精簡化間距與字體大小，移除冗餘白邊
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h2 { font-size: 18px !important; color: #1E3A8A; border-bottom: 2px solid #E5E7EB; padding-bottom: 5px; margin-top: 10px; }
    .stMetric { background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 5px; border-radius: 4px; }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold; }
    [data-testid="stTable"] { font-size: 12px !important; }
    [data-testid="stDataFrame"] { font-size: 12px !important; }
    .stTextInput>div>div>input { background-color: #F1F5F9; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    # 資料來源與範圍定義
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        # 讀取全表
        df = pd.read_csv(url)
        # 日期轉換 (假設日期欄位名稱為 Date)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"System Link Error: {e}")
        return None

# --- TOP: 查詢框架 (Search Framework) ---
df = load_data()

with st.container():
    st.markdown("### 🔍 SEARCH BOAR / CARI BOAR")
    search_id = st.text_input("", placeholder="Enter Boar Ear Tag (e.g., L10020)...", label_visibility="collapsed").strip()

if df is not None and search_id:
    # 篩選特定公豬數據
    result = df[df['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]
    
    if not result.empty:
        # 取得最新一筆資料
        latest_row = result.sort_values(by='Date', ascending=False).iloc[0]
        
        # --- MIDDLE: I. Grading Indicators ---
        st.markdown("## I. GRADING INDICATORS / PENUNJUK GRED")
        
        # V:AD 範圍 (索引 21 到 30)
        grade_cols = df.columns[21:30]
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("CURRENT GRADE", str(latest_row.get('Grade', 'N/A')))
        with m2:
            st.metric("BREED", str(latest_row.get('Breed', 'N/A')))
        with m3:
            st.metric("VITALITY", str(latest_row.get('aktiviti\nVitality', 'N/A')))
        with m4:
            st.metric("CONCENTRATION", str(latest_row.get('penumpuan, Concentration\n(x100 million/ml)', 'N/A')))

        # 顯示 V:AD 詳細表格
        st.table(latest_row[grade_cols].to_frame().T)

        # --- BOTTOM: 使用頻率與紀錄 ---
        # 1. 計算頻率 (Frequency)
        four_weeks_limit = datetime.now() - timedelta(weeks=4)
        recent_activity = result[result['Date'] >= four_weeks_limit]
        usage_frequency = len(recent_activity)

        st.markdown(f"## USAGE FREQUENCY (PAST 4 WEEKS): **{usage_frequency} TIMES**")
        
        # 2. 活動紀錄紀錄 (BY:CE) - 動態標題取自 BZ2:CE2 邏輯
        # 排除標題列後，直接呈現內容
        st.markdown("## ACTIVITY LOG / REKOD AKTIVITI")
        
        # 顯示 BY:CE 範圍 (索引 76 到 83)
        history_cols = df.columns[76:83]
        if not recent_activity.empty:
            # 隱藏 index，讓畫面更乾淨
            st.dataframe(recent_activity[history_cols].sort_values(by='Date', ascending=False), 
                         use_container_width=True, hide_index=True)
        else:
            st.warning("No activity records in the past 4 weeks. / Tiada rekod aktiviti dalam 4 minggu.")

    else:
        st.error("BOAR ID NOT FOUND / ID BOAR TIDAK DIJUMPA")
else:
    st.info("System Ready. Please input Boar Ear Tag above.")
