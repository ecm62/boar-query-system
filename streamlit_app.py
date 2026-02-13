import streamlit as st
import pandas as pd

st.set_page_config(page_title="GLA Boar System v7.7", layout="wide")

def fetch_data(sheet_id, gid, header_row=0):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        # 增加 header 參數來指定標題行位置
        df = pd.read_csv(url, header=header_row)
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
    # --- 1. 公豬分級表現 (修正：將 header_row 設為 1) ---
    st.markdown("## 📊 I. BOAR GRADE PERFORMANCE")
    # 因為您的 Excel 第一行是大標題，所以真正的欄位名稱在第二行 (Index 1)
    df_grade = fetch_data(GRADE_SHEET_ID, GRADE_GID, header_row=1)
    
    if df_grade is not None:
        # 自動偵測 ID 欄位
        id_col = next((c for c in df_grade.columns if 'Tag' in c or 'ID' in c), None)
        
        if id_col:
            res_grade = df_grade[df_grade[id_col].astype(str).str.contains(search_input, case=False, na=False)]
            if not res_grade.empty:
                # 這裡定義要顯示的 A:J 欄位關鍵指標
                key_metrics = ['Grade', 'Breed', id_col, 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %']
                display_cols = [c for c in key_metrics if c in df_grade.columns]
                st.table(res_grade[display_cols].head(1))
            else:
                st.warning(f"分級表中查無編號 '{search_input}'")
        else:
            # 輔助除錯：如果還是找不到，顯示目前抓到的正確標題列
            st.error(f"❌ 標題對位錯誤。目前抓到的欄位名稱為: {list(df_grade.columns)}")

    st.markdown("---")

    # --- 2. 最近十次採精紀錄 (維持原樣) ---
    st.markdown("## 📋 II. RECENT 10 EXTRACTIONS")
    df_semen = fetch_data(SEMEN_SHEET_ID, SEMEN_GID, header_row=0)
    
    if df_semen is not None:
        # 採精紀錄通常 ID 在第 3 欄 (Index 2)
        res_semen = df_semen[df_semen.iloc[:, 2].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_semen.empty:
            df_display = res_semen.iloc[:, 0:11].copy()
            # 強制重新定義顯示用標題，避免原表標題過長
            df_display.columns = ['Date', 'Breed', 'ID', 'Vol', 'Odor', 'Color', 'Vit', 'Conc', 'Imp', 'Diluted', 'Note']
            df_display['Date'] = pd.to_datetime(df_display['Date'], errors='coerce')
            df_display = df_display.sort_values(by='Date', ascending=False).head(10)
            df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
            st.table(df_display)
        else:
            st.warning("採精紀錄中查無此編號。")
