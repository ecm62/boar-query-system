import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 設定網頁標題與風格
st.set_page_config(page_title="S.P.T.S Boar Management", layout="wide")

def load_data():
    # Google Sheets CSV 導出連結 (自動指向 BOAR 分頁)
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        df = pd.read_csv(url)
        # 確保日期格式正確，若欄位名稱不同請修改此處
        if 'Mating Date' in df.columns:
            df['Mating Date'] = pd.to_datetime(df['Mating Date'])
        return df
    except Exception as e:
        st.error(f"資料讀取失敗: {e}")
        return None

# --- 頁面呈現 ---
st.title("🐗 公豬分級與配種查詢系統")
st.markdown("---")

df = load_data()

if df is not None:
    # 側邊欄：快速搜尋與過濾
    search_id = st.sidebar.text_input("輸入公豬 ID (Boar ID)", "").upper()
    
    # 計算時間範圍 (最近 30 天)
    today = datetime.now()
    last_month = today - timedelta(days=30)

    # 數據處理：公豬分級與配種資訊
    # 假設欄位包含：'Boar ID', 'Grade', 'Mating Date', 'Sow ID'
    
    if search_id:
        result = df[df['Boar ID'].str.contains(search_id, na=False)]
    else:
        result = df

    # 分割顯示畫面
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 公豬狀態概要")
        if search_id and not result.empty:
            current_boar = result.iloc[0]
            st.metric("當前公豬", current_boar['Boar ID'])
            # 假設有分級欄位名為 'Grade'
            grade = current_boar.get('Grade', 'N/A')
            st.warning(f"公豬評級：{grade}")
        else:
            st.info("請在左側輸入編號進行精準查詢")

    with col2:
        st.subheader("📅 最近一個月配種記錄")
        if 'Mating Date' in result.columns:
            recent_mating = result[result['Mating Date'] >= last_month].sort_values(by='Mating Date', ascending=False)
            if not recent_mating.empty:
                st.dataframe(recent_mating, use_container_width=True)
            else:
                st.write("此公豬最近 30 天內無配種記錄。")
        else:
            st.error("找不到 'Mating Date' 欄位，請檢查試算表標頭。")

    st.markdown("---")
    st.subheader("📁 全場公豬清單")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("請檢查 Google Sheets 是否已開啟共用連結權限。")