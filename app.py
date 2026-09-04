import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd

# -------------------------------------------------------------------
# PAGE CONFIG (FULLSCREEN & MOBILE OPTIMIZED FOR NOTHING PHONE)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Trading Hub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Theme + Mobile Response Fixes
st.markdown("""
<style>
    /* Full Width & Zero Margins for Mobile Display */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #131722 !important;
        color: #d1d4dc !important;
    }
    /* Input & Button Styling */
    input, select, div[role="combobox"] {
        background-color: #1e222d !important;
        color: #ffffff !important;
        border: 1px solid #2a2e39 !important;
        border-radius: 6px !important;
    }
    .stButton>button {
        background-color: #2962ff !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold;
        width: 100%;
        border-radius: 6px !important;
    }
    /* Hide Header Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session State for Selected Ticker
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

# -------------------------------------------------------------------
# HEADER & CONTROL BAR (ONE SCREEN LAYOUT)
# -------------------------------------------------------------------
col_title, col_search, col_strat = st.columns([1.2, 1.2, 1.6])

with col_title:
    st.markdown(f"<h3 style='margin:0; padding:0; color:#2962ff;'>⚡ {st.session_state.selected_ticker}</h3>", unsafe_allow_html=True)

with col_search:
    manual_input = st.text_input("Ticker:", value=st.session_state.selected_ticker, label_visibility="collapsed").strip().upper()
    if manual_input != st.session_state.selected_ticker and manual_input != "":
        st.session_state.selected_ticker = manual_input

with col_strat:
    strategy = st.selectbox(
        "Strategie",
        ["Swing Trading", "Momentum", "Volumen Ausbruch", "Cash-Secured Put", "Bull Put Spread"],
        label_visibility="collapsed"
    )

# Quick Favorites Bar
fav_list = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "PLTR", "SAP.DE", "SIE.DE"]
cols_fav = st.columns(len(fav_list))
for idx, fav in enumerate(fav_list):
    if cols_fav[idx].button(fav, key=f"btn_{fav}"):
        st.session_state.selected_ticker = fav
        st.rerun()

# -------------------------------------------------------------------
# COMBINED USA & EU SCREENER WITH KEY METRICS
# -------------------------------------------------------------------
with st.expander("🔍 **Markt-Screener (USA & EU Combined)**", expanded=False):
    if st.button("🚀 Live-Scan ausführen"):
        scan_symbols = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "PLTR", "SAP.DE", "SIE.DE", "ALV.DE", "MBG.DE"]
        scan_results = []
        
        for sym in scan_symbols:
            try:
                t = yf.Ticker(sym)
                df = t.history(period="3mo")
                if len(df) >= 20:
                    cp = df['Close'].iloc[-1]
                    chg = ((cp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                    
                    # RSI 14 Calculation
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    rsi = round(100 - (100 / (1 + rs.iloc[-1])), 1)
                    
                    # SMA 20 & 50
                    sma20 = df['Close'].rolling(20).mean().iloc[-1]
                    sma50 = df['Close'].rolling(50).mean().iloc[-1]
                    trend = "🟢 Bullisch" if cp > sma20 > sma50 else ("🔴 Bärisch" if cp < sma20 < sma50 else "🟡 Neutral")
                    
                    # 52-Week High Distance
                    high_52 = df['High'].max()
                    dist_52h = round(((cp - high_52) / high_52) * 100, 1)

                    scan_results.append({
                        "Ticker": sym,
                        "Kurs": round(cp, 2),
                        "24h (%)": round(chg, 2),
                        "RSI (14)": rsi,
                        "Trend (SMA)": trend,
                        "Abst. 52W-Hoch": f"{dist_52h}%"
                    })
            except:
                pass
        
        if scan_results:
            df_res = pd.DataFrame(scan_results)
            st.dataframe(df_res, use_container_width=True)

# -------------------------------------------------------------------
# TRADINGVIEW CHART (FULLSCREEN ADAPTIVE WITH STRATEGY INDICATORS)
# -------------------------------------------------------------------
def get_tradingview_widget(ticker, strat):
    # Mapping Tickers for TV
    tv_symbol = ticker
    if ".DE" in ticker:
        tv_symbol = f"XETR:{ticker.replace('.DE', '')}"
    elif ticker in ["NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "AMD", "PLTR"]:
        tv_symbol = f"NASDAQ:{ticker}"
    else:
        tv_symbol = f"NYSE:{ticker}"

    # Adaptive Studies based on Strategy
    studies = ["MASimple@tv-basicstudies"]
    if "Momentum" in strat:
        studies = ["RSI@tv-basicstudies", "MACD@tv-basicstudies"]
    elif "Volumen" in strat:
        studies = ["Volume@tv-basicstudies", "VPVR@tv-basicstudies"]
    elif "Swing" in strat:
        studies = ["STD;EMA", "RSI@tv-basicstudies"]

    studies_js = str(studies).replace("'", '"')

    return f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%;">
      <div id="tradingview_chart" style="height:580px;width:100%;"></div>
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
        "details": false,
        "hotlist": false,
        "calendar": false,
        "studies": {studies_js},
        "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    """

components.html(get_tradingview_widget(st.session_state.selected_ticker, strategy), height=585, scrolling=False)

# -------------------------------------------------------------------
# BOTTOM SECTION: TRADE & RISK CALCULATOR
# -------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🧮 Trade & Risiko-Manager")

c1, c2, c3, c4 = st.columns(4)

with c1:
    capital = st.number_input("Eingesetztes Kapital (€):", value=2000, step=250)
with c2:
    horizon = st.selectbox("Anlagehorizont:", ["Intraday", "1-3 Tage (Swing)", "1-4 Wochen", "1-3 Monate (Optionen)"])
with c3:
    max_risk_pct = st.number_input("Max. Risiko (%):", value=2.0, step=0.5)
with c4:
    target_profit_pct = st.number_input("Ziel-Gewinn (%):", value=6.0, step=1.0)

# Calculations
max_loss_eur = capital * (max_risk_pct / 100.0)
max_profit_eur = capital * (target_profit_pct / 100.0)
crv = round(target_profit_pct / max_risk_pct, 2) if max_risk_pct > 0 else 0

st.info(f"📊 **Ergebnis:** Max. Verlust: **-{max_loss_eur:.2f} €** | Max. Gewinn: **+{max_profit_eur:.2f} €** | Chance-Risiko-Verhältnis (CRV): **{crv}**")
