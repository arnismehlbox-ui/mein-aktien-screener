import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Aktien Screener & Trading Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Custom Styling (TradingView Look)
st.markdown("""
<style>
    .main { background-color: #131722; color: #d1d4dc; }
    .stApp { background-color: #131722; }
    div[data-testid="stSidebar"] { background-color: #1e222d; }
    h1, h2, h3, h4 { color: #d1d4dc !important; }
    .stButton>button { background-color: #2962ff; color: white; border: none; border-radius: 4px; font-weight: bold; }
    .stButton>button:hover { background-color: #1e53e5; color: white; }
</style>
""", unsafe_allow_html=True)

# Session State for Saved Watchlists
if "saved_watchlists" not in st.session_state:
    st.session_state["saved_watchlists"] = {}

# -------------------------------------------------------------------
# SIDEBAR: Navigation, Search, Strategy & Watchlists
# -------------------------------------------------------------------
st.sidebar.title("⚡ TRADING CENTER")

# A. Direct Ticker Search
st.sidebar.markdown("### 🔍 Aktie suchen")
custom_search = st.sidebar.text_input("Ticker eingeben (z.B. NVDA, AAPL, O):", value="").strip().upper()

# B. Favorites Quick Selection
st.sidebar.markdown("### ⭐ Wichtigste Favoriten")
fav_stocks = ["NVDA", "AAPL", "GOOGL", "AVGO", "O", "TEAM", "BABA", "PLTR"]
selected_fav = st.sidebar.selectbox("Schnellauswahl:", ["-- Wählen --"] + fav_stocks)

# C. Options Strategy Selection
st.sidebar.markdown("### 🎯 Setup / Strategie")
strategies = [
    "Aktie / Long Trade",
    "Cash-Secured Put (CSP)",
    "Bull Put Spread",
    "Bear Call Spread",
    "Covered Call"
]
selected_strategy = st.sidebar.selectbox("Strategie für Marken:", strategies)

# D. Preset Tickers for Scanner
TICKERS_EUROPA = ["ASML.AS", "SAP.DE", "SIE.DE", "ALV.DE", "AIR.PA", "OR.PA", "MC.PA"]
TICKERS_USA = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "AMD", "PLTR", "O"]

st.sidebar.markdown("---")
market_choice = st.sidebar.radio("Scanner Markt:", ["USA 🇺🇸", "Europa 🇪🇺", "Kombiniert 🌎"])

if market_choice == "Europa 🇪🇺":
    base_tickers = TICKERS_EUROPA
elif market_choice == "USA 🇺🇸":
    base_tickers = TICKERS_USA
else:
    base_tickers = list(set(TICKERS_EUROPA + TICKERS_USA))

# -------------------------------------------------------------------
# MAIN PANEL: Screener & Interactive Charting
# -------------------------------------------------------------------
st.title("📈 Aktien Screener & TradingView Hub")

tabs = st.tabs(["📊 Screener & Watchlist", "📉 TradingView Chart Analysator"])

# Tab 1: Screener Execution
with tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("1. Markt Scannen")
        sort_by = st.selectbox(
            "Sortieren nach:",
            ["Veränderung (%)", "RVOL", "RSI (14)", "Abstand 52W Hoch (%)"]
        )
        
        if st.button("🚀 Scan jetzt starten", type="primary"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, symbol in enumerate(base_tickers):
                status_text.text(f"Analysiere {symbol} ({i+1}/{len(base_tickers)})...")
                progress_bar.progress((i + 1) / len(base_tickers))
                
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1y")
                    
                    if len(hist) >= 50:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2]
                        change_pct = ((current_price - prev_close) / prev_close) * 100
                        
                        # RVOL (20)
                        avg_vol_20 = hist['Volume'].iloc[-21:-1].mean()
                        rvol = hist['Volume'].iloc[-1] / avg_vol_20 if avg_vol_20 > 0 else 0
                        
                        # RSI (14)
                        delta = hist['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs)).iloc[-1]
                        
                        # 52W High
                        high_52 = hist['High'].max()
                        dist_52h = ((current_price - high_52) / high_52) * 100
                        
                        results.append({
                            "Ticker": symbol,
                            "Kurs": round(current_price, 2),
                            "Veränderung (%)": round(change_pct, 2),
                            "RVOL": round(rvol, 2),
                            "RSI (14)": round(rsi, 1),
                            "Abstand 52W Hoch (%)": round(dist_52h, 2)
                        })
                except Exception:
                    continue
            
            status_text.empty()
            progress_bar.empty()
            
            if results:
                df_results = pd.DataFrame(results)
                
                # Sort logic
                if sort_by == "Veränderung (%)":
                    df_results = df_results.sort_values(by="Veränderung (%)", ascending=False)
                elif sort_by == "RVOL":
                    df_results = df_results.sort_values(by="RVOL", ascending=False)
                elif sort_by == "RSI (14)":
                    df_results = df_results.sort_values(by="RSI (14)", ascending=True)
                elif sort_by == "Abstand 52W Hoch (%)":
                    df_results = df_results.sort_values(by="Abstand 52W Hoch (%)", ascending=False)
                
                st.session_state["last_scan_df"] = df_results
                st.success(f"Scan abgeschlossen! {len(df_results)} Werte gefunden.")
    
    with col2:
        st.subheader("2. Watchlist Speichern")
        wl_name = st.text_input("Name für die Watchlist:", placeholder="z.B. High_RVOL_Setups")
        if st.button("💾 Speichern"):
            if "last_scan_df" in st.session_state and wl_name:
                st.session_state["saved_watchlists"][wl_name] = st.session_state["last_scan_df"]["Ticker"].tolist()
                st.success(f"Watchlist '{wl_name}' gespeichert!")
            else:
                st.warning("Bitte erst einen Scan ausführen und einen Namen eingeben.")

    # Show Scan Results Table
    if "last_scan_df" in st.session_state:
        st.dataframe(
            st.session_state["last_scan_df"],
            use_container_width=True,
            hide_index=True
        )

# Tab 2: Chart Analysis
with tabs[1]:
    st.subheader("📊 Interaktive Chart-Analyse")
    
    # Determine Active Ticker
    active_ticker = "NVDA" # Default
    if custom_search:
        active_ticker = custom_search
    elif selected_fav != "-- Wählen --":
        active_ticker = selected_fav
    elif "last_scan_df" in st.session_state and not st.session_state["last_scan_df"].empty:
        active_ticker = st.session_state["last_scan_df"].iloc[0]["Ticker"]

    active_ticker = st.text_input("Aktueller Chart-Ticker:", value=active_ticker).upper()

    if active_ticker:
        try:
            df_chart = yf.download(active_ticker, period="6m", interval="1d")
            
            if not df_chart.empty:
                current_p = float(df_chart['Close'].iloc[-1])
                
                st.markdown(f"**Aktueller Kurs ({active_ticker}):** `{current_p:.2f} €/$` | **Gewählte Strategie:** `{selected_strategy}`")
                
                # Setup Levels Logic
                col_s1, col_s2, col_s3 = st.columns(3)
                if "Spread" in selected_strategy or "Put" in selected_strategy:
                    short_s = col_s1.number_input("Short Strike (Verkauf):", value=round(current_p * 0.95, 2))
                    long_s = col_s2.number_input("Long Strike (Schutz/SL):", value=round(current_p * 0.90, 2))
                    tp_val = col_s3.number_input("Take Profit (Ziel):", value=round(current_p * 1.05, 2))
                else:
                    entry_v = col_s1.number_input("Entry Kurs:", value=round(current_p, 2))
                    sl_v = col_s2.number_input("Stop Loss:", value=round(current_p * 0.95, 2))
                    tp_v = col_s3.number_input("Take Profit:", value=round(current_p * 1.08, 2))

                # Candlestick Chart via Streamlit Line/Bar View
                st.line_chart(df_chart['Close'], use_container_width=True)
                st.info("💡 Tipp: Für vollwertige TradingView Canvas-Interaktion inkl. Zeichnen integrieren wir im nächsten Schritt das Lightweight-Charts Package.")
            else:
                st.error("Keine Daten für diesen Ticker gefunden.")
        except Exception as e:
            st.error(f"Fehler beim Laden des Charts: {e}")
