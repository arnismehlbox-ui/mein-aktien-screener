import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd

# -------------------------------------------------------------------
# PAGE CONFIG & STYLING
# -------------------------------------------------------------------
st.set_page_config(page_title="Trading Hub", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding: 0.5rem 0.2rem !important; max-width: 100% !important; }
    .stApp { background-color: #131722 !important; color: #d1d4dc !important; }
    input, select, div[role="combobox"] { background-color: #1e222d !important; color: #ffffff !important; border: 1px solid #2a2e39 !important; border-radius: 6px !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .trade-box-tp { background-color: rgba(38, 166, 154, 0.15); border-left: 5px solid #26a69a; padding: 12px; border-radius: 6px; margin-bottom: 8px; }
    .trade-box-entry { background-color: rgba(41, 98, 255, 0.15); border-left: 5px solid #2962ff; padding: 12px; border-radius: 6px; margin-bottom: 8px; }
    .trade-box-sl { background-color: rgba(239, 83, 80, 0.15); border-left: 5px solid #ef5350; padding: 12px; border-radius: 6px; margin-bottom: 8px; }
    .trade-box-info { background-color: rgba(255, 193, 7, 0.15); border-left: 5px solid #ffc107; padding: 10px; border-radius: 6px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# WATCHLISTS MIT DEINEN INDIZES
# -------------------------------------------------------------------
if "watchlists" not in st.session_state:
    st.session_state.watchlists = {
        "Meine Favoriten": ["NVDA", "PLTR", "SAP.DE"],
        "DAX (Deutschland Top 40)": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BMW.DE", "MBG.DE", "MUV2.DE", "BAS.DE"],
        "MDAX & SDAX (DE Mid/Small)": ["RHM.DE", "LHA.DE", "TKA.DE", "PUM.DE", "HFG.DE", "FPE.DE"],
        "Dow Jones (US Top 30)": ["AAPL", "MSFT", "V", "JNJ", "WMT", "JPM", "PG", "DIS", "HD", "UNH"],
        "S&P 500 (US Schwergewichte)": ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "AMD"],
        "EURO STOXX 50 (Europa)": ["ASML.AS", "MC.PA", "SAP.DE", "OR.PA", "SAN.MC", "SHEL.L", "TTE.PA"],
        "Russell 2000 (US Small Caps)": ["PLTR", "SMCI", "CELH", "SOFI", "HOOD", "RBLX"]
    }

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

# -------------------------------------------------------------------
# WATCHLIST & TICKER AUSWAHL
# -------------------------------------------------------------------
st.markdown("<h3 style='margin:0; text-align:center; color:#2962ff;'>⚡ Trading Command Center</h3>", unsafe_allow_html=True)

col_wl_sel, col_sym_sel = st.columns(2)

with col_wl_sel:
    wl_name = st.selectbox("📁 Index / Watchlist wählen:", list(st.session_state.watchlists.keys()))
    
with col_sym_sel:
    current_list = st.session_state.watchlists[wl_name]
    ticker_choice = st.selectbox("🎯 Aktie aus Liste:", current_list)
    st.session_state.selected_ticker = ticker_choice

with st.expander("➕ Ticker zur aktuellen Liste hinzufügen"):
    new_symbol = st.text_input("Symbol eingeben (z.B. BABA, NFLX, CON.DE):").strip().upper()
    if st.button("Hinzufügen") and new_symbol:
        if new_symbol not in st.session_state.watchlists[wl_name]:
            st.session_state.watchlists[wl_name].append(new_symbol)
            st.session_state.selected_ticker = new_symbol
            st.rerun()

# -------------------------------------------------------------------
# STRATEGIE AUSWAHL
# -------------------------------------------------------------------
strategy = st.selectbox(
    "📊 Handelsstrategie wählen:",
    ["Swing Trading (SL: 5% | TP: 15%)", "Momentum / Breakout (SL: 3% | TP: 9%)", "Konservativ (SL: 2% | TP: 4%)"]
)

# -------------------------------------------------------------------
# TRADINGVIEW CHART
# -------------------------------------------------------------------
def get_tradingview_widget(ticker, strat):
    # Börsenplatz-Zuordnung
    if ".DE" in ticker:
        tv_symbol = f"XETR:{ticker.replace('.DE', '')}"
    elif ".PA" in ticker:
        tv_symbol = f"EURONEXT:{ticker.replace('.PA', '')}"
    elif ".AS" in ticker:
        tv_symbol = f"EURONEXT:{ticker.replace('.AS', '')}"
    elif ".MC" in ticker:
        tv_symbol = f"BME:{ticker.replace('.MC', '')}"
    elif ".L" in ticker:
        tv_symbol = f"LSE:{ticker.replace('.L', '')}"
    elif ticker in ["NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "AMD", "PLTR", "AVGO", "COST"]:
        tv_symbol = f"NASDAQ:{ticker}"
    else:
        tv_symbol = f"NYSE:{ticker}"

    studies = ["MASimple@tv-basicstudies", "RSI@tv-basicstudies"]
    if "Momentum" in strat:
        studies = ["RSI@tv-basicstudies", "MACD@tv-basicstudies"]

    studies_js = str(studies).replace("'", '"')

    return f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%;">
      <div id="tradingview_chart" style="height:480px;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{tv_symbol}", "interval": "D", "timezone": "Europe/Berlin",
        "theme": "dark", "style": "1", "locale": "de_DE", "toolbar_bg": "#1e222d",
        "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
        "studies": {studies_js}, "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """

components.html(get_tradingview_widget(st.session_state.selected_ticker, strategy), height=490, scrolling=False)

# -------------------------------------------------------------------
# AUTOMATISCHER TRADE & RISIKO MANAGER
# -------------------------------------------------------------------
st.markdown("### 🧮 Auto Trade-Manager")

capital = st.number_input("💰 Dein einzusetzendes Kapital (€):", value=2000.0, step=100.0)

symbol = st.session_state.selected_ticker
current_price = 100.0

try:
    ticker_data = yf.Ticker(symbol).history(period="1d")
    if not ticker_data.empty:
        current_price = float(ticker_data['Close'].iloc[-1])
except Exception:
    pass

if "Swing Trading" in strategy:
    sl_pct, tp_pct = 0.05, 0.15
elif "Momentum" in strategy:
    sl_pct, tp_pct = 0.03, 0.09
else:
    sl_pct, tp_pct = 0.02, 0.04

limit_order = current_price
sl_price = current_price * (1 - sl_pct)
tp_price = current_price * (1 + tp_pct)

shares = int(capital // limit_order) if limit_order > 0 else 0
invested = shares * limit_order
max_risk = (limit_order - sl_price) * shares
max_profit = (tp_price - limit_order) * shares
crv = max_profit / max_risk if max_risk > 0 else 0

st.markdown(f"""
<div class="trade-box-info">
    <b>ℹ️ Aktueller Marktpreis ({symbol}):</b> {current_price:.2f} | <b>Investitionsvolumen:</b> {invested:.2f} €
</div>
<div class="trade-box-tp">
    <strong style="color:#26a69a;">🟢 Take Profit (TP Target)</strong><br>
    Verkaufssignal bei: <b>{tp_price:.2f}</b> (+{tp_pct*100:.0f}%) | Ziel-Gewinn: <b>+{max_profit:.2f} €</b>
</div>
<div class="trade-box-entry">
    <strong style="color:#2962ff;">🔵 Limit Buy Order (Einstieg)</strong><br>
    Kauf-Order setzen bei: <b>{limit_order:.2f}</b> | Empfohlene Stückzahl: <b>{shares} Stück</b>
</div>
<div class="trade-box-sl">
    <strong style="color:#ef5350;">🔴 Stop Loss (SL Absicherung)</strong><br>
    Stopp setzen bei: <b>{sl_price:.2f}</b> (-{sl_pct*100:.0f}%) | Max. Risiko: <b>-{max_risk:.2f} €</b> | CRV: <b>1:{crv:.1f}</b>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SCREENER
# -------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🔍 Markt-Screener (Direktübersicht)")

if st.button("🚀 Live-Scan für ausgewählte Watchlist starten", type="primary"):
    scan_symbols = st.session_state.watchlists[wl_name]
    scan_results = []
    
    with st.spinner("Scanne Kurse..."):
        for sym in scan_symbols:
            try:
                df = yf.Ticker(sym).history(period="1mo")
                if not df.empty and len(df) >= 20:
                    cp = float(df['Close'].iloc[-1])
                    chg = float(((cp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100)
                    sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
                    trend = "🟢 Bullisch" if cp > sma20 else "🔴 Bärisch"
                    
                    scan_results.append({
                        "Ticker": sym, 
                        "Kurs": f"{cp:.2f}", 
                        "24h Trend": f"{chg:+.2f}%", 
                        "Signal": trend
                    })
            except Exception:
                pass

    if scan_results:
        st.dataframe(pd.DataFrame(scan_results), use_container_width=True)
