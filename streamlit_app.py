import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Enterprise UI Configuration ---
st.set_page_config(page_title="GLA Boar System", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h2 { font-size: 18px !important; color: #1E3A8A; border-bottom: 2px solid #E5E7EB; padding-bottom: 5px; margin-top: 20px; font-weight: bold; }
    .stMetric { background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 10px; border-radius: 4px; }
    [data-testid="stTable"] { font-size: 12px !important; }
    [data-testid="stDataFrame"] { font-size: 12px !important; }
    .stTextInput>div>div>input { background-color: #F1F5F9; font-size: 16px; border: 2px solid #CBD5E1; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        # Load all data
        df = pd.read_csv(url)
        # Standardize "Date" for the whole system
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"System Link Error: {e}")
        return None

# --- TOP: Search Framework ---
df = load_data()

st.markdown("### 🔍 SEARCH BOAR / CARI BOAR")
search_id = st.text_input("", placeholder="Enter Boar Ear Tag...", label_visibility="collapsed").strip()

if df is not None and search_id:
    # Filter by Boar ID
    result = df[df['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]
    
    if not result.empty:
        # Latest record for Grading
        latest_row = result.sort_values(by='Date', ascending=False).iloc[0]
        
        # --- MIDDLE: I. Grading Indicators (V:AD) ---
        st.markdown("## I. GRADING INDICATORS / PENUNJUK GRED")
        
        # Slicing V:AD (Columns 21 to 30)
        grade_cols = list(df.columns[21:30])
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("CURRENT GRADE", str(latest_row.get('Grade', 'N/A')))
        with m2:
            st.metric("BREED / BAKA", str(latest_row.get('Breed', 'N/A')))
        with m3:
            st.metric("LAST RECORD", latest_row['Date'].strftime('%Y-%m-%d') if pd.notnull(latest_row['Date']) else "N/A")

        # Display Grading Table (V:AD)
        st.table(latest_row[grade_cols].to_frame().T)

        # --- BOTTOM: Frequency & Activity Log (BY:CE) ---
        st.markdown("---")
        
        # Calculate Frequency (Past 4 Weeks)
        four_weeks_limit = datetime.now() - timedelta(weeks=4)
        recent_activity = result[result['Date'] >= four_weeks_limit]
        usage_frequency = len(recent_activity)

        st.markdown(f"## USAGE FREQUENCY (PAST 4 WEEKS): :red[{usage_frequency} TIMES / KALI]")
        
        # Define Activity History (BY:CE Columns 76 to 83)
        history_cols = list(df.columns[76:83])
        
        # BZ2:CE2 Implementation: Use the second row of the slice as headers if needed, 
        # but here we show the data frame with the headers defined in your sheet.
        st.markdown("## ACTIVITY LOG / REKOD AKTIVITI")
        
        if not recent_activity.empty:
            # FIX: We keep 'Date' in the dataframe for sorting, then hide it in the view if needed
            # Or ensure 'Date' is part of the display for workers to see WHEN it happened
            display_df = recent_activity.sort_values(by='Date', ascending=False)
            
            # Show ONLY the BY:CE columns as requested
            st.dataframe(display_df[history_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("No records found in the last 4 weeks. / Tiada rekod dalam 4 minggu.")

    else:
        st.error("BOAR ID NOT FOUND / ID BOAR TIDAK DIJUMPA")
else:
    if not search_id:
        st.info("Awaiting Input... Please enter Boar Ear Tag above.")
