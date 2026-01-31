import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Enterprise UI Configuration ---
st.set_page_config(page_title="GLA Boar System", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for refined aesthetics (Smaller fonts, tighter padding)
st.markdown("""
    <style>
    .main { font-size: 14px; }
    h1 { font-size: 24px !important; font-weight: 700; color: #1E3A8A; margin-bottom: 0px; }
    h2 { font-size: 18px !important; font-weight: 600; color: #374151; margin-top: 20px; }
    h3 { font-size: 16px !important; color: #1F2937; }
    .stMetric { background-color: #F3F4F6; padding: 10px; border-radius: 5px; }
    [data-testid="stTable"] { font-size: 12px; }
    [data-testid="stDataFrame"] { font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        # Ensure 'Date' column exists and is parsed
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"System Error: Connection Failed / Kegagalan Sambungan: {e}")
        return None

# --- Header Section ---
st.title("BOAR PERFORMANCE & MATING TRACKER")
st.caption("PEMANTAUAN PRESTASI BOAR & REKOD MENGAWAN")
st.markdown("---")

df = load_data()

if df is not None:
    # --- Sidebar Search ---
    st.sidebar.header("SEARCH / CARIAN")
    search_id = st.sidebar.text_input("Boar Ear Tag / Tag Telinga Boar", placeholder="e.g. L1234").strip()
    
    # Range Definitions
    grade_cols = df.columns[21:30]    # V:AD (Grading Data)
    history_cols = df.columns[76:83]  # BY:CE (History Data)
    four_weeks_limit = datetime.now() - timedelta(weeks=4)

    if search_id:
        result = df[df['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]
    else:
        result = df

    if not result.empty:
        # Latest record for current status
        latest_row = result.sort_values(by='Date', ascending=False).iloc[0]

        # --- Dashboard Layout ---
        col_main, col_side = st.columns([3, 1])

        with col_side:
            st.subheader("Current Grade / Gred Semasa")
            # Logic for Grade Display
            grade_val = latest_row.get('Grade', 'N/A')
            st.metric(label="GRADE / GRED", value=grade_val)
            
            # Simple metadata
            st.info(f"**Breed / Baka:** {latest_row.get('Breed', 'N/A')}")
            st.info(f"**Last Date / Tarikh Akhir:** {latest_row['Date'].strftime('%Y-%m-%d') if pd.notnull(latest_row['Date']) else 'N/A'}")

        with col_main:
            st.subheader("I. Grading Indicators / Penunjuk Gred (V:AD)")
            # Transposing for better vertical reading on mobile/tablets
            grade_data = latest_row[grade_cols].to_frame(name="Value / Nilai")
            st.table(grade_data)

        st.markdown("---")

        # --- History Section ---
        st.subheader("II. 4-Week Activity Log / Log Aktiviti 4 Minggu (BY:CE)")
        
        # Filter for 4 weeks
        mask = (result['Date'] >= four_weeks_limit)
        history_df = result[mask].sort_values(by='Date', ascending=False)

        if not history_df.empty:
            st.dataframe(history_df[history_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("No records found in the past 4 weeks. / Tiada rekod dalam 4 minggu lepas.")

    else:
        st.warning("No data found for this Boar ID. / Tiada data untuk ID Boar ini.")

else:
    st.info("System Ready. Please use the sidebar to search. / Sistem sedia. Sila guna bar sisi untuk cari.")
