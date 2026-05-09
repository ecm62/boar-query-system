import streamlit as st
import pandas as pd

# --- 1. CONFIG & REFINED UI ---
st.set_page_config(page_title="GLA Boar Elite v8.5", layout="wide")

st.markdown("""
    <style>
    /* 全域背景與字體強制設定 */
    .stApp { background-color: #F1F5F9 !important; color: #1E293B !important; }
    
    /* 頂部標題 */
    .main-header {
        text-align: center; color: #FFFFFF !important; padding: 30px;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
        border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    /* KPI 指標卡片 */
    .metric-container {
        display: flex; justify-content: space-between; gap: 20px; margin-bottom: 25px;
    }
    .metric-box {
        background: white !important; padding: 20px; border-radius: 12px; flex: 1;
        text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border-top: 5px solid #3B82F6;
    }
    .metric-label { font-size: 14px; color: #64748B !important; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 28px; color: #1E3A8A !important; font-weight: 800; margin-top: 5px; }

    /* 等級標籤 (Badges) */
    .badge-elite {
        background-color: #1E3A8A !important; color: #FFFFFF !important;
        padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px;
    }
    
    /* 章節標題 */
    .section-title {
        border-left: 6px solid #1E3A8A; padding-left: 15px;
        color: #1E3A8A !important; font-weight: 800; font-size: 22px; margin: 40px 0 20px 0;
    }

    /* 數據卡片區域 */
    .data-card {
        background: white !important; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
    }

    /* 表格樣式美化 */
    .stTable { background-color: white !important; border-radius: 10px; overflow: hidden; }
    .stTable th { background-color: #F8FAFC !important; color: #1E3A8A !important; font-weight: 700 !important; }
    .stTable td { color: #334155 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* 隱藏預設元件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def fetch_data(sheet_id, gid, header_row=0):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url, header=header_row)
        df.columns = [str(c).strip() for c in df.columns]
        # 使用 2026 最新 Pandas 語法
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"FETCH ERROR: {e}")
        return None

def format_val(val, suffix=""):
    try:
        if pd.isna(val) or val == "": return "0.0"
        num = pd.to_numeric(str(val).replace('%',''), errors='coerce')
        return f"{float(num):.1f}{suffix}" if pd.notnull(num) else str(val)
    except:
        return str(val)

# --- 3. SOURCES ---
GRADE_SID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
SEMEN_SID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"

# --- 4. APP LAYOUT ---
st.markdown('<div class="main-header"><h1>GLA BOAR PERFORMANCE ANALYTICS</h1><p style="opacity: 0.8; font-weight: 500;">Precision Swine Management & Breeding Intelligence</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    search_query = st.text_input("🔍 SEARCH BOAR ID / CARI ID BOAR", placeholder="Enter Boar ID (e.g. 1401)").strip()

if search_query:
    # --- I. GENETIC PERFORMANCE ---
    st.markdown('<p class="section-title">I. GENETIC RANKING & KPI</p>', unsafe_allow_html=True)
    df_g = fetch_data(GRADE_SID, "0", header_row=1)
    
    if df_g is not None:
        id_col = next((c for c in df_g.columns if 'Tag' in c or 'ID' in c), None)
        strat_col = next((c for c in df_g.columns if 'Strategy' in c), None)
        
        if id_col:
            res_g = df_g[df_g[id_col].astype(str).str.contains(search_query, case=False, na=False)]
            if not res_g.empty:
                data = res_g.iloc[0]
                
                # 指標卡片區塊
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-box">
                        <div class="metric-label">Genetic Index</div>
                        <div class="metric-value">{format_val(data.get('Index Score', 'N/A'))}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Conception Rate</div>
                        <div class="metric-value" style="color: #059669 !important;">{format_val(data.get('CR %', 'N/A'), '%')}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Avg TSO</div>
                        <div class="metric-value">{format_val(data.get('Avg TSO', 'N/A'))}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 詳細資料卡
                with st.container():
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**TAG ID:** `{data.get(id_col)}`")
                        st.markdown(f"**BREED:** `{data.get('Breed')}`")
                    with c2:
                        grade_val = data.get('Grade', 'Unknown')
                        st.markdown(f"**GRADE:** <span class='badge-elite'>{grade_val}</span>", unsafe_allow_html=True)
                        st.markdown(f"**TOTAL MATED:** `{data.get('Mated')}`")
                    with c3:
                        st.markdown(f"**MANAGEMENT STRATEGY:**")
                        st.info(data.get(strat_col, "No strategy defined."))
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(f"No match found for Boar ID: {search_query}")

    # --- II. EXTRACTION LOGS ---
    st.markdown('<p class="section-title">II. RECENT EXTRACTION DATA (TOP 20)</p>', unsafe_allow_html=True)
    df_s = fetch_data(SEMEN_SID, "1428367761", header_row=0)
    
    if df_s is not None:
        res_s = df_s[df_s.iloc[:, 2].astype(str).str.contains(search_query, case=False, na=False)]
        if not res_s.empty:
            out_s = res_s.iloc[:, 0:11].copy()
            out_s.columns = ['Date', 'Breed', 'ID', 'Vol(ml)', 'Odor', 'Color', 'Vit', 'Conc', 'Imp%', 'Diluted', 'Note']
            out_s['Date'] = pd.to_datetime(out_s['Date'], errors='coerce')
            out_s = out_s.sort_values(by='Date', ascending=False).head(20)
            out_s['Date'] = out_s['Date'].dt.strftime('%Y-%m-%d')
            
            # 格式化數值欄位
            num_cols = ['Vol(ml)', 'Vit', 'Conc', 'Imp%', 'Diluted']
            for nc in num_cols: out_s[nc] = out_s[nc].apply(lambda x: format_val(x))
            
            st.table(out_s)
        else:
            st.warning("No extraction history available in the system.")
