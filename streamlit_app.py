import streamlit as st
import pandas as pd

# --- 1. 系統配置 ---
st.set_page_config(page_title="GLA Boar System v7.3", layout="wide")

# 套用專業管理介面 CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 30px !important; margin-bottom: 15px;
    }
    .stTable td, .stTable th { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_worksheet(sheet_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        # 清除所有空格與字串格式化
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

# --- 2. 數據源定義 (Data Sources) ---
# 新提供的評級表 (BOAR_GRADE_CUMULATIVE)
SHEET_GRADE_ID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
GID_GRADE = "0"

# 原有的採精記錄表 (假設 ID 不變，若有變請更新此處)
SHEET_SEMEN_ID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
GID_SEMEN = "1428367761"

# 加載數據
df_grade = fetch_worksheet(SHEET_GRADE_ID, GID_GRADE)
df_semen = fetch_worksheet(SHEET_SEMEN_ID, GID_SEMEN)

# --- 3. 搜尋邏輯 ---
st.markdown("## 🔍 SEARCH BOAR ID")
search_input = st.text_input("", placeholder="輸入公豬編號 (例如: D1401)...", label_visibility="collapsed").strip()

if search_input:
    # A. 處理評級資訊 (新表邏輯)
    if df_grade is not None:
        # 匹配 Tag ID 欄位 (新表為 C 欄)
        res_grade = df_grade[df_grade['Tag ID'].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_grade.empty:
            st.markdown("## I. BOAR GRADE & STRATEGY / 公豬評級與決策建議")
            # 顯示特定專業欄位，避免顯示雜訊
            display_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy (策略)', 'Avg TSO', 'CR %']
            st.table(res_grade[display_cols].head(1))
        else:
            st.warning("⚠️ 評級表中查無此編號。")

    # B. 處理近期採精記錄 (原表邏輯)
    if df_semen is not None:
        # 注意：原表數據結構較雜亂，需跳過標題列或指定正確欄位
        # 這裡假設您的採精表維持舊有模糊搜尋邏輯
        res_semen = df_semen[df_semen.iloc[:, 2].astype(str).str.contains(search_input, case=False, na=False)]
        
        if not res_semen.empty:
            st.markdown("## II. RECENT 10 EXTRACTIONS / 近期採精趨勢")
            # 依日期排序並格式化
            df_display = res_semen.iloc[:, 0:11].copy()
            df_display.columns = [
                'Date', 'Breed', 'ID', 'Volume(ml)', 'Odor', 'Color', 
                'Vitality', 'Concentration', 'Impurities', 'Diluted Vol', 'Note'
            ]
            st.table(df_display.head(10))
