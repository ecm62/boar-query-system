import streamlit as st
import pandas as pd
import re

# --- System Configuration / Konfigurasi Sistem ---
st.set_page_config(page_title="GLA Boar System v7.2", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 30px !important; margin-bottom: 15px;
    }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        df = pd.read_csv(url, header=None)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        st.error(f"Connection Failed / Sambungan Gagal: {e}")
        return None

# Load Data (GID: 1428367761)
df_raw = fetch_data("1428367761")

# --- 1. Search Framework / Kerangka Carian ---
st.markdown("## 🔍 SEARCH BOAR ID / CARI ID BOAR")
search_input = st.text_input("", placeholder="Enter ID or Number (e.g. 1401 or D1401)...", label_visibility="collapsed").strip()

if df_raw is not None and search_input:
    try:
        data_rows = df_raw.iloc[2:].copy()
        
        # --- Fuzzy Search Logic / Logik Carian Kabur ---
        # 1. 搜尋表 I (索引 23, X 欄) 與 表 II (索引 2, C 欄)
        # 支援大小寫不限與包含比對 (contains)
        def fuzzy_filter(df, col_idx, query):
            return df[df[col_idx].astype(str).str.contains(query, case=False, na=False)]

        res_info = fuzzy_filter(data_rows, 23, search_input)
        res_semen = fuzzy_filter(data_rows, 2, search_input)
        
        if not res_info.empty:
            st.markdown("## I. BOAR GRADE & INFORMATION / GRED & MAKLUMAT BOAR")
            # 若有多筆，取第一筆精確度最高的或最新的
            df_v_ad = res_info.iloc[[0], 21:30].copy() 
            df_v_ad.columns = [
                'Grade / Gred', 'Breed / Baka', 'Tag ID / No. Tag', 'Index Score / Skor Indeks', 
                'Strategy / Strategi', 'Avg TSO', 'Mated / Mengawan', 'CR % / Kadar 受胎', 'Avg Birth Wt / Berat Lahir'
            ]
            
            for col in df_v_ad.columns:
                df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                if df_v_ad[col].dtype in ['float64', 'int64']:
                    df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
            st.table(df_v_ad)
        
        if not res_semen.empty:
            st.markdown("## II. RECENT 10 EXTRACTIONS / 10 REKOD PENGUMPULAN TERKINI")
            
            df_a_k = res_semen.iloc[:, 0:11].copy()
            df_a_k.columns = [
                'Date / Tarikh', 'Breed / Baka', 'Boar ID / No. Tag', 
                'Volume Collected (ml)', 'Odor / Bau', 'Color / Warna', 
                'Vitality / Aktiviti', 'Concentration', 
                'Impurities (%)', 'Volume After Dilution (ml)', 'Other Record'
            ]
            
            # Sort and Top 10
            df_a_k['Date / Tarikh'] = pd.to_datetime(df_a_k['Date / Tarikh'], errors='coerce')
            df_a_k = df_a_k.sort_values(by='Date / Tarikh', ascending=False).head(10)
            df_a_k['Date / Tarikh'] = df_a_k['Date / Tarikh'].dt.strftime('%Y-%m-%d')
            
            for col in df_a_k.columns:
                if col not in ['Date / Tarikh', 'Breed / Baka', 'Boar ID / No. Tag', 'Odor / Bau', 'Color / Warna', 'Other Record']:
                    df_a_k[col] = pd.to_numeric(df_a_k[col], errors='coerce').fillna(0)
                    df_final_val = df_a_k[col].apply(lambda x: int(x) if x == int(x) else round(x, 2))
                    df_a_k[col] = df_final_val

            st.table(df_a_k)
        else:
            if res_info.empty:
                st.warning(f"No results for '{search_input}' / Tiada keputusan untuk '{search_input}'.")

    except Exception as e:
        st.error(f"Error / Ralat: {e}")
else:
    st.info("💡 Enter Boar ID or number to search / Masukkan ID Boar atau nombor untuk carian.")

