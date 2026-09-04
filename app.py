import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd

# -------------------------------------------------------------------
# PAGE CONFIG & TRADINGVIEW DARK THEME STYLING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="TradingView Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Erzwingt das TradingView Dark-Theme für die gesamte App
st.markdown("""
<style>
    /* Haupt-Hintergrund */
    .stApp, .main {
        background-color: #131722 !important;
        color: #d1d4dc !important;
    }
    /* Seitenleiste Dunkel */
    section[data-testid="stSidebar"] {
        background-color: #1e222d !important;
        border-right: 1px solid #2a2e39;
    }
    /* Textfarben in Seitenleiste */
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {
        color: #d1d4dc !important;
    }
    /* Eingabefelder Dunkel */
    input, select, div[role="combobox"] {
        background-color: #2a2e39 !important;
        color: #ffffff !important;
        border: 1px solid #363c4e !important;
    }
    /* Buttons */
    .stButton>button {
        background-color: #2962ff !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1e53e5 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SIDEBAR: NAVIGATION & SETUP
# -------------------------------------------------------------------
st.sidebar.title("⚡ TRADING CENTER")

# A. Aktiensuche
st.sidebar.markdown("### 🔍 Aktie / Ticker suchen")
search_ticker = st.sidebar.text_input("Symbol eingeben:", value="NVDA").strip().upper()

# B. Favoriten
st.sidebar.markdown("### ⭐ Schnellzugriff")
fav_stocks = ["NVDA", "AAPL", "GOOGL", "AVGO", "O", "TSLA", "PLTR"]
selected_fav = st.sidebar.selectbox("Favoriten:", ["-- Auswählen --"] + fav_stocks)

# Bestimme aktiven Ticker
active_ticker = search_ticker
if selected_fav != "-- Auswählen --":
    active_ticker = selected_fav

# C. Optionsstrategie & Setups
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Setup & Strategie")
strategy = st.sidebar.selectbox(
    "Strategie:", 
    ["Aktie / Long Trade", "Cash-Secured Put (CSP)", "Bull Put Spread", "Bear Call Spread"]
)

# Market selection for Scanner
st.sidebar.markdown("---")
market = st.sidebar.radio("Screener Markt:", ["USA 🇺🇸", "Europa 🇪🇺"])

# -------------------------------------------------------------------
# TRADINGVIEW EMBEDDED WIDGET FUNCTION
# -------------------------------------------------------------------
def render_tradingview_widget(ticker):
    """Baut das echte TradingView Interactive Chart Widget ein"""
    # Yahoo Ticker zu TradingView Format anpassen (z.B. SIE.DE -> XETR:SIE)
    tv_symbol = ticker
    if ".DE" in ticker:
        tv_symbol = f"XETR:{ticker.replace('.DE', '')}"
    elif "." not in ticker:
        tv_symbol = f"NASDAQ:{ticker}" if ticker in ["NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "AMD", "PLTR"] else f"NYSE:{ticker}"

    widget_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:650px;width:100%;">
      <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "D",
        "timezone": "Europe/Berlin",
        "theme": "dark",
        "style": "1",
        "locale": "de_DE",
        "toolbar_bg": "#1e222d",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(widget_code, height=660, scrolling=False)

# -------------------------------------------------------------------
# MAIN CONTENT AREA
# -------------------------------------------------------------------
st.title(f"📈 {active_ticker} | TradingView Command Center")

tab_chart, tab_scanner = st.tabs(["📉 TradingView Chart", "🔍 Screener & Watchlist"])

# TAB 1: ECHTES TRADINGVIEW CHART
with tab_chart:
    st.markdown(f"**Aktive Strategie:** `{strategy}` | **Symbol:** `{active_ticker}`")
    
    # Echte TradingView Umgebung laden
    render_tradingview_widget(active_ticker)

# TAB 2: SCREENER
with tab_scanner:
    st.subheader("Markt-Screener")
    if st.button("🚀 Scannen starten", type="primary"):
        st.info("Scanner wird ausgeführt...")
        tickers = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"] if market == "USA 🇺🇸" else ["SAP.DE", "SIE.DE", "ALV.DE"]
        
        results = []
        for sym in tickers:
            try:
                t = yf.Ticker(sym)
                h = t.history(period="1mo")
                if not h.empty:
                    cp = h['Close'].iloc[-1]
                    chg = ((cp - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
                    results.append({"Ticker": sym, "Kurs": round(cp, 2), "Veränderung (%)": round(chg, 2)})
            except:
                pass
        
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)

    
