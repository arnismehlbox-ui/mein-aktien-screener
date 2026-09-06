import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# -----------------------------------------------------------------------------
# 1. SEITEN-KONFIGURATION & LAYOUT (Mobil-optimiert)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MPS Mobile Scanner",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS für kompakte Mobil-Optik
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 12px;
        padding-right: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 MPS Mobile Scanner")

# -----------------------------------------------------------------------------
# 2. FUNKTION: TRADINGVIEW CHART RENDERER
# -----------------------------------------------------------------------------
def render_tv_chart_mobile(ticker, interval, ema_fast=9, ema_slow=20):
    tv_symbol = ticker.strip().upper()
    
    # 1. Börsenplätze für Europa anpassen
    if tv_symbol.endswith(".DE"):
        tv_symbol = f"XETR:{tv_symbol.replace('.DE', '')}"
    elif tv_symbol.endswith(".PA"):
        tv_symbol = f"EURONEXT:{tv_symbol.replace('.PA', '')}"
    elif tv_symbol.endswith(".AS"):
        tv_symbol = f"EURONEXT:{tv_symbol.replace('.AS', '')}"
    elif tv_symbol.endswith(".MC"):
        tv_symbol = f"BME:{tv_symbol.replace('.MC', '')}"
    # 2. Indizes abfangen
    elif tv_symbol in ["DAX", "^GDAXI"]:
        tv_symbol = "XER:FDAX1!"
    elif tv_symbol in ["SPX", "S&P500", "^GSPC"]:
        tv_symbol = "FOREXCOM:SPXUSD"
    elif tv_symbol in ["DJI", "DOW", "^DJI"]:
        tv_symbol = "FOREXCOM:DJI"
    elif tv_symbol in ["NDX", "NASDAQ", "^IXIC"]:
        tv_symbol = "NASDAQ:NDX"
    else:
        # WICHTIG: Wandelt US-Klassensymbole wie BRK-B für TradingView in BRK.B um
        # Verhindert, dass TradingView "BRK minus B" berechnet
        tv_symbol = tv_symbol.replace("-", ".")

    # TradingView Intervall-Zuordnung
    interval_mapping = {
        "1m": "1",
        "3m": "3",
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "1h": "60",
        "4h": "240",
        "D": "D",
        "W": "W"
    }
    tv_interval = interval_mapping.get(interval, "D")

    # TradingView HTML Widget Code
    html_code = f"""
    <div class="tradingview-widget-container" style="height:520px; width:100%;">
      <div id="tradingview_chart_widget" style="height:500px; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{tv_interval}",
        "timezone": "Europe/Berlin",
        "theme": "dark",
        "style": "1",
        "locale": "de_DE",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart_widget",
        "studies": [
          {{
            "id": "STD;EMA",
            "inputs": {{ "length": {ema_fast} }}
          }},
          {{
            "id": "STD;EMA",
            "inputs": {{ "length": {ema_slow} }}
          }}
        ]
      }}
      );
      </script>
    </div>
    """
    components.html(html_code, height=520)

# -----------------------------------------------------------------------------
# 3. APP NAVIGATION VIA TABS
# -----------------------------------------------------------------------------
tab_scanner, tab_chart_rechner = st.tabs(["🔎 Scanner", "📊 Chart & Rechner"])

# =============================================================================
# TAB 1: SCANNER
# =============================================================================
with tab_scanner:
    st.subheader("Markt Scanner")
    
    index_selection = st.selectbox(
        "Index / Liste wählen:",
        ["Favoriten", "DAX", "MDAX", "SDAX", "EURO STOXX 50", "S&P 500", "Dow Jones", "Russell 2000"]
    )
    
    # Beispielhafte Listenübersicht
    st.info(f"Ausgewählte Liste: **{index_selection}**")
    
    # Hier kannst du deine bestehende Scann-Logik einbinden
    # Beispiel-Tabelle zur Veranschaulichung:
    sample_data = pd.DataFrame({
        "Ticker": ["BRK-B", "AAPL", "SAP.DE", "MSFT", "NVDA"],
        "Name": ["Berkshire Hathaway B", "Apple Inc.", "SAP SE", "Microsoft", "Nvidia"],
        "Trend": ["Bullisch", "Konsolidierung", "Bullisch", "Bearisch", "Bullisch"],
        "RSI": [58.4, 45.2, 62.1, 38.9, 71.3]
    })
    
    st.dataframe(sample_data, use_container_width=True)

# =============================================================================
# TAB 2: CHART & POSITIONSRECHNER
# =============================================================================
with tab_chart_rechner:
    st.markdown("### Wert: ")
    
    # Ticker-Eingabe & Einstellungen
    col_sym, col_tf = st.columns([2, 1])
    with col_sym:
        ticker_input = st.text_input("Ticker-Symbol:", value="BRK-B").strip()
    with col_tf:
        timeframe = st.selectbox("Zeitfenster:", ["1m", "3m", "5m", "15m", "30m", "1h", "4h", "D", "W"], index=7)
    
    # Live Chart rendern
    if ticker_input:
        render_tv_chart_mobile(ticker_input, timeframe)
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # POSITIONSRECHNER
    # -------------------------------------------------------------------------
    st.subheader("🧮 Positionsrechner")
    
    col_acc, col_risk = st.columns(2)
    with col_acc:
        account_size = st.number_input("Kontogröße (€):", value=10000.0, step=500.0)
    with col_risk:
        risk_percent = st.number_input("Risiko pro Trade (%):", value=1.0, step=0.25)
        
    col_entry, col_sl = st.columns(2)
    with col_entry:
        entry_price = st.number_input("Einstiegskurs ($/€):", value=450.0, step=1.0)
    with col_sl:
        stop_loss = st.number_input("Stop Loss ($/€):", value=440.0, step=1.0)
        
    # Berechnungen
    max_risk_eur = account_size * (risk_percent / 100.0)
    risk_per_share = abs(entry_price - stop_loss)
    
    if risk_per_share > 0:
        shares = int(max_risk_eur / risk_per_share)
        position_value = shares * entry_price
        
        st.success(f"""
        **Berechnete Positionsgröße:**
        * **Max. Risiko (€):** {max_risk_eur:.2f} €
        * **Stückzahl:** {shares} Aktien
        * **Positionswert:** {position_value:.2f} $/€
        * **Risiko pro Aktie:** {risk_per_share:.2f} $/€
        """)
    else:
        st.warning("Einstiegskurs und Stop Loss dürfen nicht identisch sein.")
