import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd

# -------------------------------------------------------------------
# PAGE CONFIG & CSS OPTIMIERUNG
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
</style>
""", unsafe_allow_html=True)

# Session State
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

# -------------------------------------------------------------------
# KOPFZEILE: WATCHLIST & STRATEGIE
# -------------------------------------------------------------------
st.markdown(f"<h3 style='margin:0; padding:0; color:#2962ff; text-align:center;'>⚡ {st.session_state.selected_ticker}</h3>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    watchlist = ["-- Eigene Eingabe --", "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "PLTR", "SAP.DE", "SIE.DE"]
    selection = st.selectbox("📋 Watchlist", watchlist, label_visibility="collapsed")

with c2:
    if selection == "-- Eigene Eingabe --":
        manual = st.text_input("🔍 Suche:", value=st.session_state.selected_ticker, label_visibility="collapsed").strip().upper()
        if manual:
            st.session_state.selected_ticker = manual
    else:
        st.session_state.selected_ticker = selection

strategy = st.selectbox(
    "Strategie Indikatoren:",
    ["Swing Trading (EMA & RSI)", "Momentum (RSI & MACD)", "Volumen Ausbruch (Volume Profile)"],
    label_visibility="collapsed"
)

# -------------------------------------------------------------------
# TRADINGVIEW CHART
# -------------------------------------------------------------------
def get_tradingview_widget(ticker, strat):
    if ".DE" in ticker:
        tv_symbol = f"XETR:{ticker.replace('.DE', '')}"
    elif ticker in ["NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "AMD", "PLTR"]:
        tv_symbol = f"NASDAQ:{ticker}"
    else:
        tv_symbol = f"NYSE:{ticker}"

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
      <div id="tradingview_chart" style="height:500px;width:100%;"></div>
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

components.html(get_tradingview_widget(st.session_state.selected_ticker, strategy), height=510, scrolling=False)

# -------------------------------------------------------------------
# TRADE & RISIKO-MANAGER
# -------------------------------------------------------------------
st.markdown("### 🧮 Trade & Risiko Manager")

col_cap, col_en = st.columns(2)
col_sl, col_tp = st.columns(2)

with col_cap:
    capital = st.number_input("💰 Kapital (€)", value=2000.0, step=100.0)
with col_en:
    entry = st.number_input("🔵 Kauf (Entry)", value=100.0, step=1.0)
with col_sl:
    sl = st.number_input("🔴 Stop Loss", value=95.0, step=1.0)
with col_tp:
    tp = st.number_input("🟢 Take Profit", value=115.0, step=1.0)

shares = capital / entry if entry > 0 else 0
risk_per_share = entry - sl
profit_per_share = tp - entry

total_risk = risk_per_share * shares if risk_per_share > 0 else 0
total_profit = profit_per_share * shares if profit_per_share > 0 else 0
crv = total_profit / total_risk if total_risk > 0 else 0

st.markdown(f"""
<div class="trade-box-tp">
    <strong style="color:#26a69a;">🎯 Take Profit (TP)</strong><br>
    Verkauf bei: <b>{tp:.2f}</b> | Möglicher Gewinn: <b>+{total_profit:.2f} €</b>
</div>
<div class="trade-box-entry">
    <strong style="color:#2962ff;">🔵 Entry (Kaufzone)</strong><br>
    Kauf bei: <b>{entry:.2f}</b> | Positionsgröße: <b>{shares:.2f} Stück</b>
</div>
<div class="trade-box-sl">
    <strong style="color:#ef5350;">🛑 Stop Loss (SL)</strong><br>
    Ausstieg bei: <b>{sl:.2f}</b> | Max. Risiko: <b>-{total_risk:.2f} €</b> | CRV: <b>{crv:.2f}</b>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SCREENER
# -------------------------------------------------------------------
with st.expander("🔍 **Live Markt-Screener & Watchlist (Ausklappen)**", expanded=False):
    if st.button("🚀 Live-Scan starten"):
        scan_symbols = ["NVDA", "AAPL", "MSFT", "AMZN", "TSLA", "PLTR", "SAP.DE", "SIE.DE"]
        results = []
        for sym in scan_symbols:
            try:
                df = yf.Ticker(sym).history(period="1mo")
                if not df.empty:
                    cp = df['Close'].iloc[-1]
                    chg = ((cp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                    sma20 = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else cp
                    trend = "🟢" if cp > sma20 else "🔴"
                    results.append({"Ticker": sym, "Kurs": round(cp, 2), "24h %": round(chg, 2), "Trend": trend})
            except Exception:
                pass
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
