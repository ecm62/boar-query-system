import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="GLA Boar Management System", layout="wide")

def load_data():
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    gid = "1428367761"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        # Read data and handle dates
        df = pd.read_csv(url)
        # Assuming date column for history is at index 76 (BY) or general 'Date'
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data / Ralat memuatkan data: {e}")
        return None

# --- UI Header ---
st.title("🐗 Boar Grading & Mating Inquiry")
st.subheader("Sistem Semakan Gred Boar & Maklumat Mengawan")
st.markdown("---")

df = load_data()

if df is not None:
    # Sidebar Search
    search_id = st.sidebar.text_input("🔍 Search Boar ID / Cari ID Boar", "").strip()
    
    # Range Definitions (Zero-indexed for Python)
    # V:AD -> Index 21 to 30
    # BY:CE -> Index 76 to 83
    grade_cols = df.columns[21:30]
    history_cols = df.columns[76:83]
    four_weeks_ago = datetime.now() - timedelta(weeks=4)

    # Filter Logic
    if search_id:
        result = df[df['Boar Ear Tag'].astype(str).str.contains(search_id, na=False, case=False)]
    else:
        result = df

    if not result.empty:
        # Part 1: Boar Grading Information (V:AD)
        st.header("🏆 Boar Grade / Gred Boar (V:AD)")
        
        # Get the latest entry
        latest_record = result.sort_values(by='Date', ascending=False).iloc[0]
        
        # Highlight Grade
        # Note: Ensure the column name 'Grade' exists in your V:AD range
        grade_val = latest_record.get('Grade', 'N/A')
        st.markdown(f"### CURRENT GRADE / GRED SEMASA: :red[{grade_val}]")
        
        # Display Grade Detail Table
        st.write("**Grade Indicators / Penunjuk Gred:**")
        st.table(latest_record[grade_cols].to_frame().T)

        st.markdown("---")

        # Part 2: 4-Week Mating/Boar History (BY:CE)
        st.header("📅 4-Week Records / Rekod 4 Minggu (BY:CE)")
        
        recent_history = result[result['Date'] >= four_weeks_ago].sort_values(by='Date', ascending=False)
        
        if not recent_history.empty:
            st.write("**Recent Activity / Aktiviti Terkini:**")
            st.dataframe(recent_history[history_cols], use_container_width=True)
        else:
            st.warning("⚠️ No records found in the last 4 weeks. / Tiada rekod dalam 4 minggu lepas.")
            
    else:
        st.info("Please enter Boar ID to start. / Sila masukkan ID Boar untuk memulakan.")

else:
    st.error("Database connection failed. Please check permissions. / Sambungan pangkalan data gagal.")
