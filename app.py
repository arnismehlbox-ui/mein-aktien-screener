import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components

# ---------------------------------------------------------
# PAGE CONFIGURATION (MOBILE OPTIMIZED)
# ---------------------------------------------------------
st.set_page_config(
    page_title="MPS Mobile Scanner",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    div[data-baseweb="select"] { font-size: 16px; }
    button { min-height: 48px; font-size: 16px !important; }
    input:disabled { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; opacity: 0.85; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. WATCHLISTS & STRATEGIEN DEFINITION
# ---------------------------------------------------------
WATCHLISTS = {
    "DAX 40 (DE)": [
        "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", 
        "BAS.DE", "BAYN.DE", "ADS.DE", "RWE.DE", "DB1.DE", "IFX.DE", "MUV2.DE",
        "DTG.DE", "HEN3.DE", "EONG.DE", "MRK.DE", "VOW3.DE", "CON.DE"
    ],
    "MDAX (DE)": [
        "LHA.DE", "EVK.DE", "HFG.DE", "PUG.DE", "G1A.DE", "TKA.DE", "DEQ.DE", "FPE3.DE", "KGX.DE"
    ],
    "SDAX (DE)": [
        "S92.DE", "HDD.DE", "12D1.DE", "HAG.DE", "PFP.DE", "SOW.DE", "SNG.DE"
    ],
    "Euro Stoxx 50 (EU)": [
        "ASML.AS", "MC.PA", "SAP.DE", "OR.PA", "TTE.PA", "SAN.MC", "SU.PA", "IBE.MC", "CDI.PA"
    ],
    "Dow Jones Industrial (US)": [
        "AAPL", "MSFT", "UNH", "GS", "HD", "CAT", "AMZN", "V", "BA", "JNJ", "PG", "JPM", "CVX", "MCD", "WMT"
    ],
    "S&P 500 (US)": [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "LLY", "TSLA", "AVGO", "JPM", "UNH", "XOM"
    ],
    "US Tech / Nasdaq 100 (US)": [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA", "AMD", "COST", "NFLX", "TMUS"
    ],
    "Russell 2000 (US)": [
        "IWM", "VTWO", "SMCI", "AAL", "MSTR", "CELH", "CROX", "RBLX"
    ],
    "Eigene Watchlist": []
}

STRATEGIES = {
    "MPS (Market Pullback Setup - EMA20)": {
        "ema_fast": 20,
        "ema_slow": 50,
        "sl_factor": 0.97,  # SL knapp unter EMA 50 / ca. 3% Puffer
        "desc": "Rücksetzer nahe EMA 20. SL wird automatisch unter dem Support gesetzt."
    },
    "Trendfolge & Supertrend (Swing)": {
        "ema_fast": 20,
        "ema_slow": 50,
        "sl_factor": 0.95,  # SL ca. 5% unter Einstieg / EMA 50
        "desc": "Stetiger Aufwärtstrend über EMA 20 & 50."
    },
    "Breakout / Allzeithoch (Momentum)": {
        "ema_fast": 10,
        "ema_slow": 30,
        "sl_factor": 0.96,  # Enge Absicherung ca. 4%
        "desc": "Momentum-Werte nahe am Periodenhoch."
    },
    "Qualitäts- & Value-Trend": {
        "ema_fast": 50,
        "ema_slow": 200,
        "sl_factor": 0.93,  # Weiterer SL ca. 7%
        "desc": "Übergeordneter Trend (EMA 50 / EMA 200)."
    }
}

TIMEFRAMES = {
    "Swingtrading (Tageschart - D1)": {"period": "6mo", "interval": "1d", "tv_interval": "D"},
    "Positions-Trading (Wochenchart - W1)": {"period": "2y", "interval": "1wk", "tv_interval": "W"},
    "Daytrading (1 Std - H1)": {"period": "1mo", "interval": "60m", "tv_interval": "60"},
    "Daytrading (15 Min - M15)": {"period": "5d", "interval": "15m", "tv_interval": "15"}
}

# ---------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# ---------------------------------------------------------
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "SAP.DE"
if "entry_price" not in st.session_state:
    st.session_state["entry_price"] = 180.00
if "calculated_sl" not in st.session_state:
    st.session_state["calculated_sl"] = 174.60
if "target_crv" not in st.session_state:
    st.session_state["target_crv"] = 2.00

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_ticker_data(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty or len(df) < 20:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

def run_scan(watchlist_tickers, strategy_key, timeframe_key):
    strat = STRATEGIES[strategy_key]
    tf = TIMEFRAMES[timeframe_key]
    results = []
    
    for ticker in watchlist_tickers:
        df = fetch_ticker_data(ticker, tf["period"], tf["interval"])
        if df is None:
            continue
            
        close = float(df["Close"].iloc[-1])
        ema_fast = float(df["Close"].ewm(span=strat["ema_fast"]).mean().iloc[-1])
        ema_slow = float(df["Close"].ewm(span=strat["ema_slow"]).mean().iloc[-1])
        
        abstand_ema = ((close - ema_fast) / ema_fast) * 100
        
        # Strategiebasierte SL-Berechnung
        sl_price = min(ema_slow, close * strat["sl_factor"])
        
        if close > ema_fast and ema_fast > ema_slow:
            if abs(abstand_ema) <= 1.5:
                status = "🔥 PERFECT MPS SETUP"
            else:
                status = "📈 Aufwärtstrend"
        elif close < ema_fast and ema_fast < ema_slow:
            status = "📉 Abwärtstrend"
        else:
            status = "⚪ Neutral"
            
        results.append({
            "Ticker": ticker,
            "Status": status,
            "Kurs": round(close, 2),
            "SL (Strategie)": round(sl_price, 2),
            f"EMA {strat['ema_fast']}": round(ema_fast, 2),
            "Abstand %": round(abstand_ema, 2)
        })
        
    return pd.DataFrame(results)

def render_tv_chart_mobile(ticker, tv_interval):
    tv_symbol = ticker
    if ticker.endswith(".DE"):
        tv_symbol = f"XETR:{ticker.replace('.DE', '')}"
    elif ticker.endswith(".PA"):
        tv_symbol = f"EURONEXT:{ticker.replace('.PA', '')}"
    elif ticker.endswith(".AS"):
        tv_symbol = f"EURONEXT:{ticker.replace('.AS', '')}"
    elif ticker.endswith(".MC"):
        tv_symbol = f"BME:{ticker.replace('.MC', '')}"
    
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:400px;width:100%;">
      <div id="tradingview_chart" style="height:400px;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{tv_interval}",
        "timezone": "Europe/Berlin",
        "theme": "dark",
        "style": "1",
        "locale": "de_DE",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": true,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(chart_html, height=410)

# ---------------------------------------------------------
# 4. MAIN APP UI
# ---------------------------------------------------------
st.title("📱 MPS Mobile Scanner")

tab1, tab2 = st.tabs(["🔎 Scanner", "📊 Chart & Rechner"])

# TAB 1: SCANNER
with tab1:
    selected_watchlist = st.selectbox("1. Watchlist wählen:", list(WATCHLISTS.keys()))
    
    if selected_watchlist == "Eigene Watchlist":
        custom_input = st.text_input("Ticker eingeben (kommagetrennt):", "SAP.DE, SIE.DE, AAPL, TSLA")
        tickers_to_scan = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
    else:
        tickers_to_scan = WATCHLISTS[selected_watchlist]

    with st.expander("⚙️ Strategie & Zeiteinheit anpassen", expanded=False):
        selected_strategy = st.selectbox("Strategie:", list(STRATEGIES.keys()))
        selected_tf = st.selectbox("Zeiteinheit:", list(TIMEFRAMES.keys()))
        
    if 'selected_strategy' not in locals():
        selected_strategy = list(STRATEGIES.keys())[0]
    if 'selected_tf' not in locals():
        selected_tf = list(TIMEFRAMES.keys())[0]

    if st.button("🚀 Scan starten", use_container_width=True):
        with st.spinner(f"Scanne {len(tickers_to_scan)} Werte..."):
            scan_df = run_scan(tickers_to_scan, selected_strategy, selected_tf)
            st.session_state["last_scan_df"] = scan_df

    if "last_scan_df" in st.session_state and not st.session_state["last_scan_df"].empty:
        df_res = st.session_state["last_scan_df"]
        st.success(f"Scan fertig! {len(df_res)} Werte analysiert.")
        
        event = st.dataframe(
            df_res,
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun"
        )
        
        selected_rows = event.selection.rows if hasattr(event, "selection") else []
        if selected_rows:
            row_idx = selected_rows[0]
            sel_ticker = df_res.iloc[row_idx]["Ticker"]
            sel_price = float(df_res.iloc[row_idx]["Kurs"])
            sel_sl = float(df_res.iloc[row_idx]["SL (Strategie)"])
            
            st.session_state["selected_ticker"] = sel_ticker
            st.session_state["entry_price"] = sel_price
            st.session_state["calculated_sl"] = sel_sl
            
            st.info(f"✅ **{sel_ticker}** geladen. Wechsel zum Tab 'Chart & Rechner'.")

# TAB 2: CHART & POSITIONSRECHNER
with tab2:
    st.subheader(f"Wert: {st.session_state['selected_ticker']}")
    
    tv_tf = TIMEFRAMES[selected_tf]["tv_interval"] if 'selected_tf' in locals() else "D"
    render_tv_chart_mobile(st.session_state["selected_ticker"], tv_tf)
    
    st.markdown("---")
    st.subheader("🧮 Positionsrechner (Fixes Setup)")
    
    calc_mode = st.radio("Berechnungsmethode:", ["Risikobasiert (% Depot)", "Feste Investition (€)"])
    
    if calc_mode == "Risikobasiert (% Depot)":
        depot_size = st.number_input("Gesamtkapital (€):", value=1500.0, step=100.0)
        risk_pct = st.number_input("Risiko pro Trade (%):", value=2.0, step=0.25)
        max_risk_eur = depot_size * (risk_pct / 100.0)
    else:
        invest_amount = st.number_input("Anlagebetrag (€):", value=1000.0, step=100.0)
        max_risk_eur = None

    # CRV Steuerung
    target_crv = st.number_input(
        "🎯 Wunsch-CRV (Anpassbar):", 
        value=float(st.session_state["target_crv"]), 
        step=0.25, 
        min_value=1.0, 
        max_value=10.0
    )
    st.session_state["target_crv"] = target_crv

    # Feste, schreibgeschützte Werte (Strategiebasiert)
    entry = st.session_state["entry_price"]
    sl = st.session_state["calculated_sl"]
    risk_per_share = entry - sl
    
    # Automatische TP Berechnung basierend auf CRV
    tp = entry + (risk_per_share * target_crv)
    
    st.markdown("#### 🔒 Ausgewählte Strategie-Parameter")
    st.number_input("Einstieg / Limit Order (€/$):", value=float(entry), disabled=True)
    st.number_input("Stop Loss (€/$) [Strategie-Fix]:", value=float(sl), disabled=True)
    st.number_input("Take Profit (€/$) [Aus CRV berechnet]:", value=float(round(tp, 2)), disabled=True)

    if risk_per_share > 0:
        if calc_mode == "Risikobasiert (% Depot)":
            shares = int(max_risk_eur / risk_per_share)
            total_volume = shares * entry
        else:
            shares = int(invest_amount / entry)
            total_volume = shares * entry
            max_risk_eur = shares * risk_per_share
            
        total_profit = shares * (tp - entry)
        
        st.markdown("---")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("📦 Stückzahl", f"{shares} Stk.")
            st.metric("🛡️ Risiko", f"{max_risk_eur:,.2f} €")
        with col_m2:
            st.metric("💰 Volumen", f"{total_volume:,.2f} €")
            st.metric("⚖️ Effektives CRV", f"1 : {target_crv:.2f}")
    else:
        st.error("Ungültiges Setup: Stop Loss liegt nicht unter dem Einstiegskurs.")
