import streamlit as st
import pandas as pd

# --- 專業管理介面設定 ---
st.set_page_config(page_title="GLA Boar System v5.6", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    h2 { 
        font-size: 18px !important; color: #1E3A8A; font-weight: bold; 
        border-left: 5px solid #1E3A8A; padding: 10px 0 10px 15px; 
        margin-top: 35px !important; margin-bottom: 15px;
    }
    .stTable td, .stTable th { text-align: center !important; vertical-align: middle !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_data(gid):
    sheet_id = "1qvo4INF0LZjA2u49grKW_cHeEPJO48_dk6gOlXoMgaM"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        # 讀取整張表，不預設 header，避免重複欄位報錯
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

df_raw = fetch_data("1428367761")

# --- 1. 查詢框架 ---
st.markdown("## 🔍 搜尋公豬耳號 / SEARCH BOAR ID")
search_id = st.text_input("", placeholder="輸入耳號 (例如: D1397)...", label_visibility="collapsed").strip()

if df_raw is not None and search_id:
    # 物理座標定位：Row 2 是索引 1 (標題)，數據從索引 2 開始
    # Tag ID 位於 X 欄 (索引 23)
    try:
        data_rows = df_raw.iloc[2:] # 真正的數據行
        # 搜尋索引 23 (X 欄，Tag ID)
        res = data_rows[data_rows[23].astype(str).str.fullmatch(search_id, case=False, na=False)]
        
        if not res.empty:
            # --- 第一部分：育種資訊 (強制抓取 V 欄到 AD 欄，即索引 21 到 29) ---
            st.markdown("## I. 公豬等級與資訊 (BOAR INFORMATION)")
            
            # 抓取物理位置數據
            df_v_ad = res.iloc[:, 21:30].copy() 
            
            # 手動定義標題，確保 UI 乾淨專業
            df_v_ad.columns = [
                'Grade', 'Breed', 'Tag ID', 'Index Score', 
                'Strategy (策略)', 'Avg TSO', 'Mated', 'CR %', 'Avg Birth Wt'
            ]
            
            # 數值整數化，解決 17.0000 問題
            for col in df_v_ad.columns:
                df_v_ad[col] = pd.to_numeric(df_v_ad[col], errors='ignore')
                if df_v_ad[col].dtype in ['float64', 'int64']:
                    df_v_ad[col] = df_v_ad[col].fillna(0).astype(int)
            
            st.table(df_v_ad)

            # --- 第二部分：六週採精分析 (BY:CG) ---
            st.markdown("## II. 最近六週採精分析 (LAST 6 WEEKS PERFORMANCE)")
            
            # 根據物理偏移量抓取特定區塊 (這裡示意抓取 Breed/Gen/Tag + 數據)
            # 採精資訊座標複雜，建議維持名稱搜尋但先過濾掉重複項
            header_row = df_raw.iloc[1].fillna('').astype(str).tolist()
            # 移除重複標題影響
            unique_cols = []
            for i, col in enumerate(header_row):
                unique_cols.append(f"{col}_{i}")
            
            df_tmp = res.copy()
            df_tmp.columns = unique_cols
            
            metrics = {"Usage": "Usage", "Vitality": "Vitality", "Conc.": "Concentration", "Imp.": "Impurities", "Vol.": "Volume"}
            weeks = ['W06', 'W05', 'W04', 'W03', 'W02', 'W01']
            
            for label, key in metrics.items():
                target_cols = [c for c in unique_cols if any(k in c for k in ['Breed_22', 'Tag ID_23'])] # 鎖定基礎資訊
                # 抓取符合週次與關鍵字的欄位索引
                week_hits = [c for w in weeks for c in unique_cols if w in c and key.lower() in c.lower()]
                
                if week_hits:
                    st.markdown(f"**{label}**")
                    df_final = df_tmp[target_cols + week_hits].copy()
                    # 去除標題後的索引後綴顯示
                    df_final.columns = [c.split('_')[0] for c in df_final.columns]
                    for col in df_final.columns:
                        df_final[col] = pd.to_numeric(df_final[col], errors='ignore')
                        if df_final[col].dtype in ['float64', 'int64']:
                            df_final[col] = df_final[col].fillna(0).astype(int)
                    st.table(df_final)
                    
        else:
            st.error(f"查無耳號: {search_id}")
    except Exception as e:
        st.error(f"解析錯誤: {e}")
else:
    st.info("💡 請輸入公豬耳號。")
