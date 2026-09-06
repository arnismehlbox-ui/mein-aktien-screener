import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(page_title="MPS & Daytrading Scanner", layout="wide")

# ---------------------------------------------------------
# 1. SESSION STATE INITIALISIERUNG
# ---------------------------------------------------------
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "AAPL"

# ---------------------------------------------------------
# 2. SEITENLEISTE: HANDELSSTIL & KAPITAL-EINSTELLUNGEN
# ---------------------------------------------------------
st.sidebar.header("⚙️ Trading-Einstellungen")

trading_style = st.sidebar.selectbox(
    "Trading-Art wählen:",
    ["MPS / Swingtrading (D1)", "Daytrading (M15)", "Scalping (M5)"]
)

# Parameter je nach Handelsstil anpassen
if "MPS" in trading_style:
    tv_interval = "D"
    default_ema = [20]
    style_label = "MPS Swingtrading (Tageschart)"
elif "Daytrading" in trading_style:
    tv_interval = "15"
    default_ema = [20, 50]
    style_label = "Daytrading (15-Minuten-Chart)"
else:
    tv_interval = "5"
    default_ema = [9, 21]
    style_label = "Scalping (5-Minuten-Chart)"

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Risikomanagement")

total_capital = st.sidebar.number_input(
    "Gesamtkapital (€):", 
    min_value=100.0, 
    value=10000.0, 
    step=500.0
)

risk_percent = st.sidebar.slider(
    "Risiko pro Trade (%):", 
    min_value=0.25, 
    max_value=3.0, 
    value=1.0, 
    step=0.25
)

max_risk_amount = total_capital * (risk_percent / 100.0)

# ---------------------------------------------------------
# 3. TABS: SCANNER & CHART / CALCULATOR
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🚀 MPS Auto-Scanner", "📊 Single Chart & Positionsrechner"])

# --- TAB 1: SCANNER ---
with tab1:
    st.title(f"Automatischer Scanner – {style_label}")
    watchlist = st.selectbox("Watchlist wählen:", ["US Tech (US)", "DAX 40 (DE)"])
    
    if st.button("🚀 MPS-Scan jetzt starten"):
        st.success("Scan abgeschlossen!")

    # Beispieldaten des Scanners
    scan_data = pd.DataFrame([
        {"Ticker": "AAPL", "Status": "🔥 PERFECT MPS SETUP", "Kurs": 319.97, "EMA 20": 316.87, "Abstand EMA20 (%)": 1.0},
        {"Ticker": "MSFT", "Status": "🔥 PERFECT MPS SETUP", "Kurs": 499.70, "EMA 20": 489.86, "Abstand EMA20 (%)": 2.0},
        {"Ticker": "AMZN", "Status": "🔥 PERFECT MPS SETUP", "Kurs": 258.51, "EMA 20": 259.60, "Abstand EMA20 (%)": -0.4},
        {"Ticker": "NVDA", "Status": "📈 Aufwärtstrend (Kein Pullback)", "Kurs": 230.36, "EMA 20": 219.30, "Abstand EMA20 (%)": 5.0},
    ])

    st.markdown("💡 *Tipp: Klicke auf eine Zeile in der Tabelle, um das Kürzel direkt in den Chart zu laden.*")
    
    # Interaktive Tabelle mit Zeilenauswahl
    event = st.dataframe(
        scan_data, 
        use_container_width=True, 
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    if len(event.selection["rows"]) > 0:
        selected_index = event.selection["rows"][0]
        st.session_state["selected_ticker"] = scan_data.iloc[selected_index]["Ticker"]
        st.info(f"✅ Symbol **{st.session_state['selected_ticker']}** für Chart & Rechner ausgewählt.")

# --- TAB 2: CHART & RECHNER ---
with tab2:
    st.title(f"Analyse & Orderberechnung: {st.session_state['selected_ticker']}")
    
    current_symbol = st.text_input("Aktuelles Kürzel (Ticker):", value=st.session_state["selected_ticker"]).upper()
    st.session_state["selected_ticker"] = current_symbol

    col_chart, col_calc = st.columns([2, 1])

    with col_calc:
        st.subheader("🎯 Positionsrechner")
        
        entry_price = st.number_input("Limit-Order / Einstieg (€):", min_value=0.01, value=320.00, step=0.50)
        stop_loss = st.number_input("Stop Loss (SL) (€):", min_value=0.01, value=310.00, step=0.50)
        take_profit = st.number_input("Take Profit (TP) (€):", min_value=0.01, value=340.00, step=0.50)

        risk_per_share = abs(entry_price - stop_loss)
        reward_per_share = abs(take_profit - entry_price)

        if risk_per_share > 0:
            shares = int(max_risk_amount // risk_per_share)
            position_size = shares * entry_price
            total_loss = shares * risk_per_share
            total_profit = shares * reward_per_share
            crv = reward_per_share / risk_per_share if risk_per_share > 0 else 0

            st.markdown("---")
            st.success(f"""
            **Order-Vorgabe für deinen Broker:**
            * **Stückzahl:** {shares} Aktien
            * **Positionsvolumen:** {position_size:,.2f} €
            * **Maximaler Verlust:** {total_loss:,.2f} € ({risk_percent}% von {total_capital:,.0f} €)
            * **Möglicher Gewinn:** {total_profit:,.2f} € (CRV {crv:.2f}:1)
            """)
        else:
            st.warning("Einstieg und Stop Loss dürfen nicht identisch sein.")

    with col_chart:
        st.subheader(f"Chart ({style_label})")
        
        # TradingView Widget HTML mit aktivierten Zeichenwerkzeugen (hide_side_toolbar: false)
        tv_widget_code = f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container" style="height:600px;width:100%;">
          <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{current_symbol}",
            "interval": "{tv_interval}",
            "timezone": "Europe/Berlin",
            "theme": "dark",
            "style": "1",
            "locale": "de",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_side_toolbar": false,  // ZEICHENWERKZEUGE AKTIVIERT
            "allow_symbol_change": true,
            "details": true,
            "hotlist": true,
            "calendar": true,
            "studies": [
              "STD;EMA"
            ],
            "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        components.html(tv_widget_code, height=620)
