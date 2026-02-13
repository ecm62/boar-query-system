import streamlit as st
import pandas as pd
import numpy as np

# --- 1. 系統配置與 CSS 強制置中 ---
st.set_page_config(page_title="GLA Boar System v7.8", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 30px !important; margin-bottom: 15px;
    }
    /* 強制所有表格儲存格內容置中 */
    .stTable td, .stTable th { 
        text-align: center !important; 
        vertical-align: middle !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 數據抓取與數值格式化函數 ---
def format_dataframe(df):
    """將 DataFrame 中的數值統一格式化為小數點後一位"""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # 排除純整數 ID 或編號欄位，其餘轉為浮點數並格式化
            if "ID" not in col and "Grade" not in col:
                df[col] = df[col].map(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
    return df

def fetch_data(sheet_id, gid, header_row=0):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url, header=header_row)
        df.columns = [str(c).strip() for c in df.columns]
        # 移除字串前後空格
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"數據抓取失敗: {e}")
        return None

# --- 3. 數據源配置 ---
GRADE_SHEET_ID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
GRADE_GID = "0"
SEMEN_SHEET_ID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
SEMEN_GID = "1428367761"

# --- 4. 搜尋與輸出邏輯 ---
st.markdown("## 🔍 SEARCH BOAR ID")
search_input = st.text_input("", placeholder="輸入公豬編號 (如: 1401)...", label_visibility="collapsed").strip()

if search_input:
    # --- 表一：公豬分級表現 (標題在第二行) ---
    st.markdown("## 📊 I. BOAR GRADE PERFORMANCE / 公豬分級表現")
    df_grade = fetch_data(GRADE_SHEET_ID, GRADE_GID, header_row=1)
    
    if df_grade is not None:
        # 自動偵測 ID 欄位
        id_col = next((c for c in df_grade.columns if 'Tag' in c or 'ID' in c), None)
        
        if id_col:
            res_grade = df_grade[df_grade[id_col].astype(str).str.contains(search_input, case=False, na=False)]
            if not res_grade.empty:
                # 嚴格定義要求的輸出欄位
                target_cols = ['Grade', 'Breed', id_col, 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %']
                # 檢查欄位是否存在並過濾
                available_cols = [c for c in target_cols if c in df_grade.columns]
                
                # 選取數據並格式化
                display_grade = res_grade[available_cols].head(1).copy()
                # 確保數值列正確轉換為小數點一位
                for col in ['Index Score', 'Avg TSO', 'CR %']:
                    if col in display_grade.columns:
                        display_grade[col] = pd.to_numeric(display_grade[col], errors='coerce').map(lambda x: f"{x:.1f}" if pd.notnull(x) else "0.0")
                
                st.table(display_grade)
            else:
                st.warning("分級表中查無此編號。")
        else:
            st.error("無法鎖定 Tag ID 欄位。")

    st.markdown("---")

    # --- 表二：最近二十次採精紀錄 ---
    st.markdown("## 📋 II. RECENT 20 EXTRACTIONS / 最近 20 次採精紀錄")
    df_semen = fetch_data(SEMEN_SHEET_ID, SEMEN_GID, header_row=0)
    
    if df_semen is not None:
        # 採精紀錄通常 ID 在第 3 欄
        res_semen = df_semen[df_semen.iloc[:, 2].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_semen.empty:
            df_display = res_semen.iloc[:, 0:11].copy()
            df_display.columns = ['Date', 'Breed', 'ID', 'Vol', 'Odor', 'Color', 'Vit', 'Conc', 'Imp', 'Diluted', 'Note']
            
            # 日期排序與格式化
            df_display['Date'] = pd.to_datetime(df_display['Date'], errors='coerce')
            df_display = df_display.sort_values(by='Date', ascending=False).head(20) # 擴展至 20 次
            df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
            
            # 數值欄位小數點一位格式化 (Vol, Vit, Conc, Diluted)
            num_cols = ['Vol', 'Vit', 'Conc', 'Imp', 'Diluted']
            for col in num_cols:
                df_display[col] = pd.to_numeric(df_display[col], errors='coerce').map(lambda x: f"{x:.1f}" if pd.notnull(x) else "0.0")
            
            st.table(df_display)
        else:
            st.warning("採精紀錄中查無此編號。")
else:
    st.info("💡 請輸入公豬編號。")
