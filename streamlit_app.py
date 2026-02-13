import streamlit as st
import pandas as pd

# --- 系統配置 ---
st.set_page_config(page_title="GLA Boar System v7.4", layout="wide")

@st.cache_data(ttl=300)
def fetch_data(sheet_id, gid, header_row=0):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 指定 header=header_row 確保欄位名稱正確讀取
        df = pd.read_csv(url, header=header_row)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"數據抓取失敗: {e}")
        return None

# --- 數據源定義 ---
# 表 I: 公豬分級表現 (新網址)
GRADE_SHEET_ID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
GRADE_GID = "0"

# 表 II: 採精紀錄 (舊網址)
SEMEN_SHEET_ID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
SEMEN_GID = "1428367761"

# --- 搜尋介面 ---
st.markdown("## 🔍 SEARCH BOAR ID / 搜尋公豬編號")
search_input = st.text_input("", placeholder="輸入編號 (例如: 1401)...", label_visibility="collapsed").strip()

if search_input:
    # --- 步驟 1: 處理公豬分級表現 ---
    df_grade_raw = fetch_data(GRADE_SHEET_ID, GRADE_GID, header_row=0)
    
    if df_grade_raw is not None:
        # 確保 Tag ID 是字串且不含空值，進行模糊搜尋
        # 這裡針對您提供的 A:J 欄位結構
        res_grade = df_grade_raw[df_grade_raw['Tag ID'].astype(str).str.contains(search_input, case=False, na=False)]
        
        st.markdown("## 📊 I. BOAR GRADE PERFORMANCE / 公豬分級表現")
        if not res_grade.empty:
            # 僅選擇 A:J 範圍內的重要指標進行輸出
            # 根據您的定義：Grade, Breed, Tag ID, Index Score, Strategy, Avg TSO, Mated, CR% 等
            target_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %']
            # 過濾掉不存在的欄位避免報錯
            available_cols = [c for c in target_cols if c in res_grade.columns]
            st.table(res_grade[available_cols].head(1))
        else:
            st.warning(f"在分級表 (GRADE) 中找不到編號 '{search_input}'")

    # --- 步驟 2: 處理最近十次採精紀錄 ---
    df_semen_raw = fetch_data(SEMEN_SHEET_ID, SEMEN_GID, header_row=0)
    
    if df_semen_raw is not None:
        # 採精表的 ID 欄位在不同版本中可能叫 'Boar ID' 或 'No. Tag'，請確認
        # 這裡沿用位置索引搜尋以確保相容性 (假設 ID 在第 3 欄，索引 2)
        res_semen = df_semen_raw[df_semen_raw.iloc[:, 2].astype(str).str.contains(search_input, case=False, na=False)]
        
        st.markdown("## 📋 II. RECENT 10 EXTRACTIONS / 最近十次採精紀錄")
        if not res_semen.empty:
            # 整理採精紀錄顯示內容
            df_display = res_semen.iloc[:, 0:11].copy()
            df_display.columns = [
                'Date', 'Breed', 'Boar ID', 'Vol(ml)', 'Odor', 'Color', 
                'Vitality', 'Concentration', 'Impurities', 'Diluted Vol', 'Record'
            ]
            # 轉換日期並排序
            df_display['Date'] = pd.to_datetime(df_display['Date'], errors='coerce')
            df_display = df_display.sort_values(by='Date', ascending=False).head(10)
            df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
            st.table(df_display)
        else:
            st.warning(f"在採精紀錄 (SEMEN) 中找不到編號 '{search_input}'")
else:
    st.info("💡 請輸入公豬編號以調閱完整數據。")
