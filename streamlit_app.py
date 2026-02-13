import streamlit as st
import pandas as pd

# --- 系統配置 ---
st.set_page_config(page_title="GLA Boar System v7.5", layout="wide")

def fetch_data(sheet_id, gid, header_row=0):
    # 使用標準 export 格式增加相容性
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url, header=header_row)
        # 清除空格
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        if "401" in str(e):
            st.error(f"❌ 存取遭拒 (401): 請將 Google Sheet 的共用權限改為『知道連結的任何人都能檢視』。\nSheet ID: {sheet_id}")
        else:
            st.error(f"❌ 連線錯誤: {e}")
        return None

# --- 數據源定義 ---
# 表 I: 公豬分級表現 (新網址)
GRADE_SHEET_ID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
GRADE_GID = "0"

# 表 II: 採精紀錄 (舊網址)
SEMEN_SHEET_ID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
SEMEN_GID = "1428367761"

# --- 搜尋介面 ---
st.markdown("## 🔍 SEARCH BOAR ID")
search_input = st.text_input("", placeholder="輸入公豬編號 (如: 1401)...", label_visibility="collapsed").strip()

if search_input:
    # --- 第一部分：輸出公豬分級表現 ---
    st.markdown("## 📊 I. BOAR GRADE PERFORMANCE")
    df_grade = fetch_data(GRADE_SHEET_ID, GRADE_GID, header_row=0)
    
    if df_grade is not None:
        # 強制將 Tag ID 轉為字串進行搜尋，避免 1401 (數值) 比對不到 "1401" (字串)
        res_grade = df_grade[df_grade['Tag ID'].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_grade.empty:
            # 確保只顯示您需要的 A:J 欄位關鍵資訊
            target_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %']
            available_cols = [c for c in target_cols if c in df_grade.columns]
            st.table(res_grade[available_cols].head(1))
        else:
            st.warning("分級表中查無此編號。")

    st.markdown("---") # 分隔線

    # --- 第二部分：輸出最近十次採精紀錄 ---
    st.markdown("## 📋 II. RECENT 10 EXTRACTIONS")
    df_semen = fetch_data(SEMEN_SHEET_ID, SEMEN_GID, header_row=0)
    
    if df_semen is not None:
        # 採精紀錄表搜尋邏輯 (假設 ID 在第 3 欄)
        res_semen = df_semen[df_semen.iloc[:, 2].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_semen.empty:
            df_display = res_semen.iloc[:, 0:11].copy()
            df_display.columns = [
                'Date', 'Breed', 'ID', 'Vol(ml)', 'Odor', 'Color', 
                'Vitality', 'Concentration', 'Impurities', 'Diluted Vol', 'Note'
            ]
            # 日期排序
            df_display['Date'] = pd.to_datetime(df_display['Date'], errors='coerce')
            df_display = df_display.sort_values(by='Date', ascending=False).head(10)
            df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
            st.table(df_display)
        else:
            st.warning("採精紀錄中查無此編號。")
else:
    st.info("💡 請輸入公豬編號。")
