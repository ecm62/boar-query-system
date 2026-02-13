import streamlit as st
import pandas as pd

# --- 1. UI CUSTOMIZATION ---
st.set_page_config(page_title="GLA Boar Elite v8.2", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .main-header {
        text-align: center; color: #1E3A8A; padding: 20px;
        background: white; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 25px;
    }
    .section-title {
        border-left: 6px solid #1E3A8A; padding-left: 15px;
        color: #1E3A8A; font-weight: bold; font-size: 20px; margin: 30px 0 15px 0;
    }
    .stTable { background-color: white; border-radius: 10px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }
    .stTable th { background-color: #1E3A8A !important; color: white !important; text-align: center !important; }
    .stTable td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def fetch_data(sheet_id, gid, header_row=0):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url, header=header_row)
        # Clean column names immediately
        df.columns = [str(c).strip() for c in df.columns]
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
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

# --- 4. APP ---
st.markdown('<div class="main-header"><h1>GLA BOAR PERFORMANCE ANALYTICS</h1><p>Bilingual Professional Management v8.2</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_query = st.text_input("SEARCH BOAR ID / CARI ID BOAR", placeholder="e.g. 1401").strip()

if search_query:
    # --- SECTION I: PERFORMANCE ---
    st.markdown('<p class="section-title">I. GENETIC PERFORMANCE & STRATEGY</p>', unsafe_allow_html=True)
    df_g = fetch_data(GRADE_SID, "0", header_row=1)
    
    if df_g is not None:
        # 1. Identify ID Column
        id_col = next((c for c in df_g.columns if 'Tag' in c or 'ID' in c), None)
        
        if id_col:
            res_g = df_g[df_g[id_col].astype(str).str.contains(search_query, case=False, na=False)]
            if not res_g.empty:
                # 2. Robust Column Selection (Only select if exists)
                mapping = {
                    'Grade': 'Grade', 
                    'Breed': 'Breed', 
                    id_col: 'Tag ID',
                    'Index Score': 'Index Score', 
                    'Strategy': 'Strategy',
                    'Avg TSO': 'Avg TSO', 
                    'Mated': 'Mated', 
                    'CR %': 'CR %'
                }
                
                # Check which keys actually exist in the dataframe
                existing_cols = [k for k in mapping.keys() if k in df_g.columns]
                
                # Filter and Rename
                out_g = res_g[existing_cols].rename(columns=mapping).head(1).copy()
                
                # 3. Format numeric columns
                for k in ['Index Score', 'Avg TSO', 'Mated', 'CR %']:
                    target_name = mapping.get(k)
                    if target_name in out_g.columns:
                        out_g[target_name] = out_g[target_name].apply(format_val)
                
                st.table(out_g)
                
                # Diagnostic help (only shown if columns are missing)
                missing = set(mapping.keys()) - set(df_g.columns)
                if missing:
                    st.caption(f"Note: Some columns were not found in the sheet: {missing}")
            else:
                st.warning(f"No match found for ID: {search_query}")
        else:
            st.error(f"Cannot find ID column. Found columns: {list(df_g.columns)}")

    # --- SECTION II: EXTRACTIONS ---
    st.markdown('<p class="section-title">II. RECENT 20 EXTRACTION LOGS</p>', unsafe_allow_html=True)
    df_s = fetch_data(SEMEN_SID, "1428367761", header_row=0)
    
    if df_s is not None:
        # Use Index 2 for the ID column in Extraction sheet
        res_s = df_s[df_s.iloc[:, 2].astype(str).str.contains(search_query, case=False, na=False)]
        if not res_s.empty:
            out_s = res_s.iloc[:, 0:11].copy()
            out_s.columns = ['Date', 'Breed', 'ID', 'Vol(ml)', 'Odor', 'Color', 'Vit', 'Conc', 'Imp%', 'Diluted', 'Note']
            out_s['Date'] = pd.to_datetime(out_s['Date'], errors='coerce')
            out_s = out_s.sort_values(by='Date', ascending=False).head(20)
            out_s['Date'] = out_s['Date'].dt.strftime('%Y-%m-%d')
            
            num_cols = ['Vol(ml)', 'Vit', 'Conc', 'Imp%', 'Diluted']
            for nc in num_cols: out_s[nc] = out_s[nc].apply(format_val)
            st.table(out_s)
        else:
            st.warning("No extraction history found.")
