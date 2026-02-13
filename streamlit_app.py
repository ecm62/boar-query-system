import streamlit as st
import pandas as pd

st.set_page_config(page_title="GLA Boar System v7.6", layout="wide")

def fetch_data(sheet_id, gid):
    # 使用 export 格式確保數據流穩定
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        # 移除欄位名稱與內容的頭尾空格
        df.columns = [str(c).strip() for c in df.columns]
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"數據抓取失敗: {e}")
        return None

# --- 數據源配置 ---
GRADE_SHEET_ID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
GRADE_GID = "0"
SEMEN_SHEET_ID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
SEMEN_GID = "1428367761"

st.markdown("## 🔍 SEARCH BOAR ID")
search_input = st.text_input("", placeholder="輸入編號 (如: 1401)...", label_visibility="collapsed").strip()

if search_input:
    # --- 1. 公豬分級表現 (動態欄位匹配) ---
    st.markdown("## 📊 I. BOAR GRADE PERFORMANCE")
    df_grade = fetch_data(GRADE_SHEET_ID, GRADE_GID)
    
    if df_grade is not None:
        # 自動偵測可能的 ID 欄位 (找包含 'Tag' 或 'ID' 的欄位)
        id_col = next((c for c in df_grade.columns if 'Tag' in c or 'ID' in c), None)
        
        if id_col:
            res_grade = df_grade[df_grade[id_col].astype(str).str.contains(search_input, case=False, na=False)]
            if not res_grade.empty:
                # 定義優先顯示的關鍵指標 (依序檢查是否存在)
                key_metrics = ['Grade', 'Breed', id_col, 'Index Score', 'Strategy', 'Avg TSO', 'CR %']
                display_cols = [c for c in key_metrics if c in df_grade.columns]
                st.table(res_grade[display_cols].head(1))
            else:
                st.warning(f"分級表中查無編號 '{search_input}'")
        else:
            st.error(f"❌ 錯誤：在分級表中找不到包含 'Tag ID' 的標題欄位。請檢查 Excel 第一行。目前的欄位有: {list(df_grade.columns)}")

    st.markdown("---")

    # --- 2. 最近十次採精紀錄 ---
    st.markdown("## 📋 II. RECENT 10 EXTRACTIONS")
    df_semen = fetch_data(SEMEN_SHEET_ID, SEMEN_GID)
    
    if df_semen is not None:
        # 採精紀錄通常 ID 在第 3 欄 (Index 2)
        res_semen = df_semen[df_semen.iloc[:, 2].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_semen.empty:
            df_display = res_semen.iloc[:, 0:11].copy()
            # 統一賦予標準顯示名稱
            df_display.columns = ['Date', 'Breed', 'ID', 'Vol', 'Odor', 'Color', 'Vit', 'Conc', 'Imp', 'Diluted', 'Note']
            df_display['Date'] = pd.to_datetime(df_display['Date'], errors='coerce')
            df_display = df_display.sort_values(by='Date', ascending=False).head(10)
            df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
            st.table(df_display)
        else:
            st.warning("採精紀錄中查無此編號。")
