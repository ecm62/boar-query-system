import streamlit as st
import pandas as pd

# --- 1. CONFIG & REFINED UI ---
st.set_page_config(page_title="GLA Boar Elite v8.5", layout="wide")

st.markdown("""
    <style>
    /* 全域背景 */
    .stApp { background-color: #F8FAFC !important; color: #1E293B !important; }
    
    /* 頂部標題 */
    .main-header {
        text-align: center; color: #FFFFFF !important; padding: 25px;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
        border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    
    /* 四大狀態框佈局 */
    .status-container {
        display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px;
    }
    .status-box {
        background: white !important; padding: 15px; border-radius: 10px; flex: 1;
        text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0; border-top: 4px solid #3B82F6;
    }
    .status-label { font-size: 12px; color: #64748B !important; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .status-value { font-size: 20px; color: #1E3A8A !important; font-weight: 800; }
    
    /* 策略專用框樣式 */
    .strategy-box {
        background-color: #EFF6FF !important; border-top: 4px solid #10B981 !important;
    }

    /* 等級標籤 (Badges) */
    .badge-grade {
        background-color: #1E3A8A !important; color: #FFFFFF !important;
        padding: 2px 10px; border-radius: 15px; font-weight: bold; font-size: 18px;
    }
    
    /* 章節標題 */
    .section-title {
        border-left: 6px solid #1E3A8A; padding-left: 15px;
        color: #1E3A8A !important; font-weight: 800; font-size: 20px; margin: 30px 0 15px 0;
    }

    /* 表格樣式美化 */
    .stTable { background-color: white !important; border-radius: 8px; overflow: hidden; }
    .stTable th { background-color: #F1F5F9 !important; color: #1E3A8A !important; font-weight: 700 !important; }
    .stTable td { color: #334155 !important; font-family: 'Consolas', monospace; }
    
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
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"FETCH ERROR: {e}")
        return None

def format_val(val):
    try:
        if pd.isna(val) or val == "": return "0.0"
        num = pd.to_numeric(str(val).replace('%',''), errors='coerce')
        return f"{float(num):.1f}" if pd.notnull(num) else str(val)
    except:
        return str(val)

# --- 3. SOURCES ---
GRADE_SID = "1vK71OXZum2NrDkAPktOVz01-sXoETcdxdrBgC4jtc-c"
SEMEN_SID = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"

# --- 4. APP LAYOUT ---
st.markdown('<div class="main-header"><h1>GLA BOAR PERFORMANCE ANALYTICS</h1><p style="opacity: 0.8; font-size: 14px;">PhD Standard Swine Breeding Dashboard</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    search_query = st.text_input("🔍 SEARCH BOAR ID / CARI ID BOAR", placeholder="e.g. 1400").strip()

if search_query:
    # --- I. STATUS TILES (The 4 Boxes) ---
    df_g = fetch_data(GRADE_SID, "0", header_row=1)
    
    if df_g is not None:
        id_col = next((c for c in df_g.columns if 'Tag' in c or 'ID' in c), None)
        strat_col = next((c for c in df_g.columns if 'Strategy' in c), None)
        
        if id_col:
            res_g = df_g[df_g[id_col].astype(str).str.contains(search_query, case=False, na=False)]
            if not res_g.empty:
                data = res_g.iloc[0]
                
                # 四個核心框佈局
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f'<div class="status-box"><div class="status-label">TAG ID</div><div class="status-value">{data.get(id_col)}</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="status-box"><div class="status-label">BREED</div><div class="status-value">{data.get("Breed")}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="status-box"><div class="status-label">GRADE</div><div class="status-value"><span class="badge-grade">{data.get("Grade", "N/A")}</span></div></div>', unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<div class="status-box strategy-box"><div class="status-label">MANAGEMENT STRATEGY</div><div class="status-value">{data.get(strat_col, "N/A")}</div></div>', unsafe_allow_html=True)

                # 展示 Avg TSO 指標 (保持與上回一致的專業呈現)
                st.markdown('<p class="section-title">PERFORMANCE KPI</p>', unsafe_allow_html=True)
                st.metric(label="Average TSO", value=format_val(data.get('Avg TSO', '0.0')))
                
            else:
                st.warning(f"No match found for: {search_query}")

    # --- II. EXTRACTION LOGS (NOTE REMOVED) ---
    st.markdown('<p class="section-title">II. RECENT EXTRACTION DATA (TOP 20)</p>', unsafe_allow_html=True)
    df_s = fetch_data(SEMEN_SID, "1428367761", header_row=0)
    
    if df_s is not None:
        # 使用第 2 欄位進行搜尋 (ID 欄位)
        res_s = df_s[df_s.iloc[:, 2].astype(str).str.contains(search_query, case=False, na=False)]
        if not res_s.empty:
            # 修正處：只選取前 10 欄位，移除第 11 欄 (Note)
            out_s = res_s.iloc[:, 0:10].copy()
            out_s.columns = ['Date', 'Breed', 'ID', 'Vol(ml)', 'Odor', 'Color', 'Vit', 'Conc', 'Imp%', 'Diluted']
            
            out_s['Date'] = pd.to_datetime(out_s['Date'], errors='coerce')
            out_s = out_s.sort_values(by='Date', ascending=False).head(20)
            out_s['Date'] = out_s['Date'].dt.strftime('%Y-%m-%d')
            
            # 格式化數值
            num_cols = ['Vol(ml)', 'Vit', 'Conc', 'Imp%', 'Diluted']
            for nc in num_cols: out_s[nc] = out_s[nc].apply(format_val)
            
            st.table(out_s)
        else:
            st.warning("No extraction history found.")
