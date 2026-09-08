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

# CSS-Anpassungen für gute Lesbarkeit & Mobile Touch
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    div[data-baseweb="select"] { font-size: 16px; }
    button { min-height: 48px; font-size: 16px !important; }
    
    /* Optimierter Kontrast für deaktivierte/schreibgeschützte Felder */
    input:disabled {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    div[data-baseweb="input"] {
        background-color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# WKN-DATENBANK FÜR ZERO / SMARTBROKER+
# ---------------------------------------------------------
WKN_DB = {
    # Elite 7 & US-Titel
    "MSFT": "870747", "AVGO": "A2JG9Z", "V": "A0NC7B", "PG": "852062", "O": "899744",
    "AAPL": "865985", "GOOGL": "A14Y6F", "GOOG": "A14Y6H", "AMZN": "906866", "META": "A1JWVX",
    "NVDA": "918422", "TSLA": "A1CX3T", "XOM": "852549", "CVX": "852552", "JNJ": "853243",
    "JPM": "850628", "UNH": "869561", "HD": "866953", "CAT": "850598", "BA": "850471",
    "GS": "920332", "MCD": "856958", "KO": "850663", "DIS": "855686", "IBM": "851399",
    "CSCO": "878841", "VZ": "868402", "WMT": "860853", "CRM": "A0B87V", "INTC": "855681",
    "AMD": "863186", "COST": "888351", "NFLX": "552484", "TMUS": "A1T7LU", "LLY": "858560", 
    "BRK-B": "A0YJQ2", "IWM": "599013", "VTWO": "A1CS69", "SMCI": "A0LC13", "AAL": "A1W97M", 
    "MSTR": "A0DLH4", "CELH": "A0YH6K", "CROX": "A0HLVU", "RBLX": "A2QH3D",
    # DAX 40 (DE)
    "SAP.DE": "716460", "SIE.DE": "723610", "ALV.DE": "840400", "DTE.DE": "555750", 
    "AIR.DE": "938914", "MBG.DE": "710000", "BMW.DE": "519000", "BAS.DE": "BASF11", 
    "BAYN.DE": "BAY001", "ADS.DE": "A1EWWW", "RWE.DE": "703712", "DB1.DE": "581005", 
    "IFX.DE": "623100", "MUV2.DE": "843002", "DTG.DE": "DTR0CK", "HEN3.DE": "604843", 
    "EONG.DE": "ENAG99", "MRK.DE": "659990", "VOW3.DE": "766403", "CON.DE": "543900",
    # MDAX (DE)
    "LHA.DE": "823212", "EVK.DE": "EVNK01", "HFG.DE": "A16140", "PUG.DE": "PAH003", 
    "G1A.DE": "630500", "TKA.DE": "750000", "DEQ.DE": "580100", "FPE3.DE": "A0Z2XN", "KGX.DE": "620200",
    # SDAX (DE)
    "S92.DE": "722800", "HDD.DE": "604700", "12D1.DE": "A12DM8", "HAG.DE": "HAG000", 
    "PFP.DE": "691660", "SOW.DE": "A16140", "SNG.DE": "723530",
    # Euro Stoxx 50 (EU)
    "ASML.AS": "A1J4U4", "MC.PA": "853292", "OR.PA": "853888", "TTE.PA": "850727", 
    "SAN.MC": "870737", "SU.PA": "860180", "IBE.MC": "A0M46B", "CDI.PA": "883388"
}

# ---------------------------------------------------------
# 1. WATCHLISTS & STRATEGIEN DEFINITION (INKL. HALTEDAUER)
# ---------------------------------------------------------
WATCHLISTS = {
    "Elite 7 (EMR-Strategie)": [
        "MSFT", "AVGO", "SAP.DE", "V", "ALV.DE", "PG", "O"
    ],
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
        "AAPL", "MSFT", "UNH", "GS", "HD", "CAT", "AMZN", "V", "BA", "JNJ", "PG", "JPM", "CVX", "XOM", "MCD", "WMT"
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
        "sl_factor": 0.97,
        "holding_time": "3 bis 10 Tage (Klassischer Swing Trade)",
        "desc": "Rücksetzer nahe EMA 20 im intakten Aufwärtstrend."
    },
    "Breakout / Allzeithoch (Momentum)": {
        "ema_fast": 10,
        "ema_slow": 30,
        "sl_factor": 0.96,
        "holding_time": "2 bis 8 Tage (Zügiger Impuls-Trade)",
        "desc": "Momentum-Ausbruch nahe am Periodenhoch."
    },
    "Trendfolge & Supertrend (Swing)": {
        "ema_fast": 20,
        "ema_slow": 50,
        "sl_factor": 0.95,
        "holding_time": "1 bis 4 Wochen (Mittelfristiger Trend)",
        "desc": "Stetiger Aufwärtstrend über EMA 20 & 50 reiten."
    },
    "Qualitäts- & Value-Trend": {
        "ema_fast": 50,
        "ema_slow": 200,
        "sl_factor": 0.93,
        "holding_time": "1 bis 6 Monate (Positions-Trading)",
        "desc": "Übergeordneter Großtrend (EMA 50 / EMA 200)."
    }
}

TIMEFRAMES = {
    "Swingtrading (Tageschart - D1)": {"period": "2y", "interval": "1d", "tv_interval": "D"},
    "Positions-Trading (Wochenchart - W1)": {"period": "5y", "interval": "1wk", "tv_interval": "W"},
    "Daytrading (1 Std - H1)": {"period": "1mo", "interval": "60m", "tv_interval": "60"},
    "Daytrading (15 Min - M15)": {"period": "5d", "interval": "15m", "tv_interval": "15"}
}

# ---------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# ---------------------------------------------------------
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "SAP.DE"
if "selected_wkn" not in st.session_state:
    st.session_state["selected_wkn"] = "716460"
if "entry_price" not in st.session_state:
    st.session_state["entry_price"] = 180.00
if "calculated_sl" not in st.session_state:
    st.session_state["calculated_sl"] = 174.60
if "target_crv" not in st.session_state:
    st.session_state["target_crv"] = 2.00
if "active_strategy" not in st.session_state:
    st.session_state["active_strategy"] = list(STRATEGIES.keys())[0]

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
@st.cache_data(ttl=1800)
def get_eur_usd_rate():
    try:
        fx = yf.Ticker("EURUSD=X")
        rate = fx.fast_info.get("last_price")
        if rate and float(rate) > 0:
            return float(rate)
    except Exception:
        pass
    return 1.163

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

def run_scan(watchlist_name, watchlist_tickers, strategy_key, timeframe_key, eur_usd):
    strat = STRATEGIES[strategy_key].copy()
    is_elite = (watchlist_name == "Elite 7 (EMR-Strategie)")
    
    # AUTOPILOT FÜR ELITE 7: Zwingt den Scanner auf EMA 50 & 200
    if is_elite:
        strat["ema_fast"] = 50
        strat["ema_slow"] = 200
        strat["sl_factor"] = 0.93
        
    tf = TIMEFRAMES[timeframe_key]
    results = []
    
    for ticker in watchlist_tickers:
        df = fetch_ticker_data(ticker, tf["period"], tf["interval"])
        if df is None:
            continue
            
        close = float(df["Close"].iloc[-1])
        ema_fast = float(df["Close"].ewm(span=strat["ema_fast"], adjust=False).mean().iloc[-1])
        ema_slow = float(df["Close"].ewm(span=strat["ema_slow"], adjust=False).mean().iloc[-1])
        
        # Euro-Umrechnung für Zero
        is_eur = ticker.endswith((".DE", ".PA", ".AS", ".MC"))
        fx = 1.0 if is_eur else eur_usd
        close_eur = close / fx
        
        if is_elite:
            abstand_ema = ((close - ema_slow) / ema_slow) * 100
            reference_col = f"Abstand (EMA {strat['ema_slow']})"
            
            if close > ema_slow:
                status = "🟢 Intakt (Halten / Sparplan)"
            else:
                status = "🔴 Unter EMA 200 (Cash parken)"
        else:
            abstand_ema = ((close - ema_fast) / ema_fast) * 100
            reference_col = f"Abstand (EMA {strat['ema_fast']})"
            
            if close > ema_fast and ema_fast > ema_slow:
                if abs(abstand_ema) <= 1.5:
                    status = "🔥 PERFECT MPS SETUP"
                else:
                    status = "📈 Aufwärtstrend"
            elif close < ema_fast and ema_fast < ema_slow:
                status = "📉 Abwärtstrend"
            else:
                status = "⚪ Neutral"
                
        sl_price = min(ema_slow, close * strat["sl_factor"])
        sl_eur = sl_price / fx
        
        results.append({
            "Ticker": ticker,
            "WKN": WKN_DB.get(ticker, "-"),
            "Status": status,
            "Kurs (€)": round(close_eur, 2),
            "SL (€)": round(sl_eur, 2),
            "Kurs (Orig)": f"{round(close, 2)} {'€' if is_eur else '$'}",
            f"EMA {strat['ema_fast']}": round(ema_fast, 2),
            f"EMA {strat['ema_slow']}": round(ema_slow, 2),
            reference_col: f"{round(abstand_ema, 2)} %"
        })
        
    return pd.DataFrame(results)

def render_tv_chart_mobile(ticker, tv_interval, ema_fast=20, ema_slow=50):
    tv_symbol = ticker.strip().upper()
    
    if tv_symbol.endswith(".DE"):
        tv_symbol = f"XETR:{tv_symbol.replace('.DE', '')}"
    elif tv_symbol.endswith(".PA"):
        tv_symbol = f"EURONEXT:{tv_symbol.replace('.PA', '')}"
    elif tv_symbol.endswith(".AS"):
        tv_symbol = f"EURONEXT:{tv_symbol.replace('.AS', '')}"
    elif tv_symbol.endswith(".MC"):
        tv_symbol = f"BME:{tv_symbol.replace('.MC', '')}"
    else:
        tv_symbol = tv_symbol.replace("-", ".")
    
    chart_html = f"""
    <div class="tradingview-widget-container" style="height:480px;width:100%;">
      <div id="tradingview_chart" style="height:480px;width:100%;"></div>
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
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart",
        "studies": [
          {{
            "id": "STD;EMA",
            "inputs": {{
              "length": {ema_fast}
            }}
          }},
          {{
            "id": "STD;EMA",
            "inputs": {{
              "length": {ema_slow}
            }}
          }}
        ]
      }});
      </script>
    </div>
    """
    components.html(chart_html, height=490)

# ---------------------------------------------------------
# 4. MAIN APP UI
# ---------------------------------------------------------
st.title("📱 MPS Mobile Scanner")

tab1, tab2 = st.tabs(["🔎 Scanner", "📊 Chart & Rechner"])

# TAB 1: SCANNER
with tab1:
    selected_watchlist = st.selectbox("1. Watchlist wählen:", list(WATCHLISTS.keys()))
    st.session_state["selected_watchlist"] = selected_watchlist
    
    if selected_watchlist == "Eigene Watchlist":
        custom_input = st.text_input("Ticker eingeben (kommagetrennt):", "SAP.DE, SIE.DE, AAPL, TSLA, XOM")
        tickers_to_scan = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
    else:
        tickers_to_scan = WATCHLISTS[selected_watchlist]

    with st.expander("⚙️ Strategie & Zeiteinheit anpassen", expanded=True):
        selected_strategy = st.selectbox("Strategie:", list(STRATEGIES.keys()))
        selected_tf = st.selectbox("Zeiteinheit:", list(TIMEFRAMES.keys()))
        
        st.info(f"⏱️ **Ungefähre Haltedauer:** {STRATEGIES[selected_strategy]['holding_time']}\n\nℹ️ {STRATEGIES[selected_strategy]['desc']}")
        st.session_state["active_strategy"] = selected_strategy
        st.session_state["active_tf"] = selected_tf

    eur_usd_live = get_eur_usd_rate()
    st.caption(f"EUR/USD-Kurs: **{eur_usd_live:.4f}** (US-Kurse & Stop-Loss werden automatisch in Euro umgerechnet)")

    if st.button("🚀 Scan starten", use_container_width=True):
        with st.spinner(f"Scanne {len(tickers_to_scan)} Werte... (Das dauert bei D1 kurz wg. 2-Jahres-Historie)"):
            scan_df = run_scan(selected_watchlist, tickers_to_scan, selected_strategy, selected_tf, eur_usd_live)
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
            sel_wkn = df_res.iloc[row_idx]["WKN"]
            sel_price = float(df_res.iloc[row_idx]["Kurs (€)"])
            sel_sl = float(df_res.iloc[row_idx]["SL (€)"])
            
            st.session_state["selected_ticker"] = sel_ticker
            st.session_state["selected_wkn"] = sel_wkn
            st.session_state["entry_price"] = sel_price
            st.session_state["calculated_sl"] = sel_sl
            
            st.info(f"✅ **{sel_ticker}** (WKN: {sel_wkn}) geladen. Wechsel zum Tab 'Chart & Rechner'.")

# TAB 2: CHART & POSITIONSRECHNER
with tab2:
    wkn_display = st.session_state.get("selected_wkn", "-")
    st.subheader(f"Wert: {st.session_state['selected_ticker']} | WKN: {wkn_display}")
    
    curr_strat_key = st.session_state.get("active_strategy", list(STRATEGIES.keys())[0])
    
    # AUTOPILOT FÜR CHART: Wenn Elite 7 ausgewählt ist, zwinge Chart auf EMA 50 & 200
    if st.session_state.get("selected_watchlist", "") == "Elite 7 (EMR-Strategie)":
        ema_fast_chart = 50
        ema_slow_chart = 200
    else:
        ema_fast_chart = STRATEGIES[curr_strat_key]["ema_fast"]
        ema_slow_chart = STRATEGIES[curr_strat_key]["ema_slow"]
    
    active_tf = st.session_state.get("active_tf", list(TIMEFRAMES.keys())[0])
    tv_tf = TIMEFRAMES[active_tf]["tv_interval"]
    
    render_tv_chart_mobile(st.session_state["selected_ticker"], tv_tf, ema_fast_chart, ema_slow_chart)
    
    st.markdown("---")
    st.subheader("🧮 Positionsrechner (Euro / Zero)")
    
    calc_mode = st.radio("Berechnungsmethode:", ["Risikobasiert (% Depot)", "Feste Investition (€)"])
    
    if calc_mode == "Risikobasiert (% Depot)":
        depot_size = st.number_input("Gesamtkapital (€):", value=1500.0, step=100.0)
        risk_pct = st.number_input("Risiko pro Trade (%):", value=2.0, step=0.25)
        max_risk_eur = depot_size * (risk_pct / 100.0)
    else:
        invest_amount = st.number_input("Anlagebetrag (€):", value=1000.0, step=100.0)
        max_risk_eur = None

    target_crv = st.number_input(
        "🎯 Wunsch-CRV (Anpassbar):", 
        value=float(st.session_state["target_crv"]), 
        step=0.25, 
        min_value=1.0, 
        max_value=10.0
    )
    st.session_state["target_crv"] = target_crv

    entry = st.session_state["entry_price"]
    sl = st.session_state["calculated_sl"]
    risk_per_share = entry - sl
    tp = entry + (risk_per_share * target_crv)
    
    curr_holding = STRATEGIES[curr_strat_key]["holding_time"]
    
    st.markdown("#### 🔒 Order-Parameter für Zero")
    st.text_input("⏱️ Geplante Haltedauer:", value=curr_holding, disabled=True)
    st.number_input("Einstieg / Limit Order (€):", value=float(round(entry, 2)), disabled=True)
    st.number_input("Stop Loss (€) [Strategie-Fix]:", value=float(round(sl, 2)), disabled=True)
    st.number_input("Take Profit (€) [Aus CRV berechnet]:", value=float(round(tp, 2)), disabled=True)

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
            st.metric("🔴 Max. Verlust", f"{max_risk_eur:,.2f} €")
            st.metric("💰 Gesamtvolumen", f"{total_volume:,.2f} €")
        with col_m2:
            st.metric("⚖️ Effektives CRV", f"1 : {target_crv:.2f}")
            st.metric("🟢 Max. Gewinn", f"{total_profit:,.2f} €")
            
        st.info(f"💡 **Order für Zero:** Kaufe **{shares}** Stk. mit Limit **{round(entry, 2)} €** und platziere einen Stop-Loss bei **{round(sl, 2)} €**.")
    else:
        st.error("Ungültiges Setup: Stop Loss liegt nicht unter dem Einstiegskurs.")
