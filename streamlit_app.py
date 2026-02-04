import streamlit as st
import pandas as pd

# --- 專業管理介面設定 (Bilingual UI) ---
st.set_page_config(page_title="GLA Boar Query System", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    h2 { font-size: 18px !important; color: #1E3A8A; font-weight: bold; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-top: 20px; margin-bottom: 10px;}
    .stTable { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid, range_str=None):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    # 使用 range 參數來精確抓取 V2:AE2298 等範圍
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    if range_str:
        url += f"&range={range_str}"
    
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"連線失敗 GID {gid}: {e}")
        return None

# --- 資料獲取 ---
# 表格一：Boar 基本資訊 (V2:AE2298)
df_boar_info = fetch_data("1428367761", "V2:AE2298")
# 表格二：最近六週採精資訊 (BY2:CG2298)
df_semen_history = fetch_data("1428367761", "BY2:CG2298")

# --- 1. 查詢框架 (Search Framework) ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

if search_id:
    if df_boar_info is not None and not df_boar_info.empty:
        # 尋找耳號欄位 (預期為 Tag ID)
        target_col = 'Tag ID' if 'Tag ID' in df_boar_info.columns else df_boar_info.columns[2]
        
        # 精確匹配
        res_info = df_boar_info[df_boar_info[target_col].astype(str) == search_id]
        
        if not res_info.empty:
            # --- 表格一：公豬基本資訊 ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            # 指定顯示欄位：Grade, Breed, Tag ID, Index Score, Strategy, Avg TSO, Mated, CR %, Avg Birth Wt, Data Source
            info_cols = ['Grade', 'Breed', 'Tag ID', 'Index Score', 'Strategy', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt', 'Data Source']
            # 僅過濾存在的欄位以防報錯
            display_info = res_info[[c for c in info_cols if c in res_info.columns]]
            st.table(display_info)

            # --- 表格二：最近六週採精資訊 ---
            if df_semen_history is not None:
                # 假設歷史紀錄表的 Tag ID 在其欄位中 (BY:CG 範圍內的 Tag ID)
                hist_tag_col = 'Tag ID' if 'Tag ID' in df_semen_history.columns else df_semen_history.columns[2]
                res_hist = df_semen_history[df_semen_history[hist_tag_col].astype(str) == search_id]
                
                if not res_hist.empty:
                    st.markdown("## II. 最近六週採精分析 (LAST 6 WEEKS PERFORMANCE)")
                    st.markdown("> 包含：📈 使用頻率、⚡ 精子活力、💧 精子濃度、⚠️ 雜質率、🥛 歷史產精量")
                    
                    # 指定顯示欄位：Breed, Gen, Tag ID, W06, W05, W04, W03, W02, W01
                    hist_display_cols = ['Breed', 'Gen', 'Tag ID', 'W06', 'W05', 'W04', 'W03', 'W02', 'W01']
                    display_hist = res_hist[[c for c in hist_display_cols if c in res_hist.columns]]
                    st.table(display_hist)
                else:
                    st.warning(f"未找到耳號 {search_id} 的採精紀錄 (BY:CG 範圍)。")
        else:
            st.error(f"找不到耳號為 '{search_id}' 的公豬資料。")
    else:
        st.error("無法載入資料來源，請檢查網路連線或試算表權限。")
else:
    st.info("💡 請在上方輸入公豬耳號以啟動查詢系統。")
