import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 設定網頁標題
st.set_page_config(page_title="GLA 公豬查詢系統", layout="wide")

def load_data():
    # 您的試算表資訊
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        # 讀取資料並忽略空白行
        df = pd.read_csv(url).dropna(how='all')
        # 轉換日期格式
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"資料讀取失敗: {e}")
        return None

st.title("🐗 公豬分級與配種查詢系統")
st.markdown("---")

df = load_data()

if df is not None:
    # 修正：使用正確的欄位名稱 "Boar Ear Tag"
    search_id = st.sidebar.text_input("輸入公豬耳號 (Boar Ear Tag)", "").strip()
    
    # 計算最近一個月 (30天) 的時間點
    last_month = datetime.now() - timedelta(days=30)

    # 搜尋過濾
    if search_id:
        result = df[df['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]
    else:
        result = df

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 公豬狀態概要")
        if search_id and not result.empty:
            # 取得該豬隻最新的一筆資料
            latest_record = result.sort_values(by='Date', ascending=False).iloc[0]
            st.metric("公豬耳號", latest_record['Boar Ear Tag'])
            st.info(f"品種：{latest_record['Breed']}")
            # 顯示活力指標
            vitality = latest_record.get('aktiviti\nVitality', '無資料')
            st.warning(f"最新活力評分：{vitality}")
        else:
            st.info("請在左側輸入耳號進行查詢")

    with col2:
        st.subheader("📅 最近一個月配種/採精紀錄")
        # 篩選最近 30 天數據
        recent_mating = result[result['Date'] >= last_month].sort_values(by='Date', ascending=False)
        
        if not recent_mating.empty:
            # 顯示對工人有意義的資訊
            display_df = recent_mating[['Date', 'Boar Ear Tag', 'aktiviti\nVitality', 'penumpuan, Concentration\n(x100 million/ml)']]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.write("此公豬最近 30 天內無記錄。")

    st.markdown("---")
    st.subheader("📋 原始數據預覽 (BOAR 分頁)")
    st.write("顯示最新的 50 筆紀錄：")
    st.dataframe(df.sort_values(by='Date', ascending=False).head(50), use_container_width=True)

else:
    st.warning("無法載入資料，請確認試算表權限設定。")
