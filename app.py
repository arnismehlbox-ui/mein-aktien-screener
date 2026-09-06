import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(page_title="Trading Command Center - MPS", page_icon="⚡", layout="wide")

st.title("⚡ Trading Command Center — Momentum-Pullback-System")

# ---------------------------------------------------------
# SIDEBAR: Risikomanagement & Konto-Einstellungen
# ---------------------------------------------------------
st.sidebar.header("🛡️ Risikomanagement (MPS)")
account_capital = st.sidebar.number_input("Gesamtkapital (€)", value=1300, step=100)
risk_percentage = st.sidebar.slider("Risiko pro Trade (%)", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
target_crv = st.sidebar.selectbox("Ziel-CRV (Chance-Risiko-Verhältnis)", [2.0, 2.5, 3.0], index=0)

max_risk_amount = account_capital * (risk_percentage / 100.0)
st.sidebar.info(f"Maximales Risiko pro Trade: **{max_risk_amount:.2f} €**")

# Watchlists
WATCHLISTS = {
    "Meine Favoriten": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "TKA.DE", "RHM.DE", "SAP.DE"],
    "DAX 40 (DE)": ["ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "DTG.DE", "DB1.DE", "DBK.DE", "DTE.DE", "EOAN.DE", "IFX.DE", "MBG.DE", "MUV2.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SRT.DE", "SY1.DE", "VOW3.DE"],
    "MDAX & SDAX Highlights": ["TKA.DE", "RHM.DE", "HAG.DE", "PUM.DE", "AIXA.DE", "EVT.DE", "NEM.DE", "GXI.DE", "FPE.DE"],
    "US Tech & Momentum": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "AMD", "NFLX", "PLTR"]
}

# ---------------------------------------------------------
# FUNKTION: MPS SCANNER (Trend + Pullback Logik)
# ---------------------------------------------------------
def scan_mps_candidates(tickers):
    results = []
    progress_bar = st.progress(0)
    
    for idx, ticker in enumerate(tickers):
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty or len(df) < 200:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Technische Indikatoren berechnen
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            
            latest = df.iloc[-1]
            close = float(latest['Close'])
            sma50 = float(latest['SMA_50'])
            sma200 = float(latest['SMA_200'])
            ema20 = float(latest['EMA_20'])
            high_52w = float(df['High'].max())
            
            # MPS Kriterien:
            # 1. Intakter Aufwärtstrend: Close > SMA50 und SMA50 > SMA200
            uptrend = (close > sma50) and (sma50 > sma200) and (close >= high_52w * 0.80)
            
            # 2. Pullback an den EMA 20 (Abstand max. 3.5%)
            dist_ema20_pct = ((close - ema20) / ema20) * 100
            pullback = (abs(dist_ema20_pct) <= 3.5) or (float(latest['Low']) <= ema20 * 1.01 and close >= ema20 * 0.97)
            
            if uptrend and pullback:
                status = "🔥 PERFECT MPS SETUP"
            elif uptrend:
                status = "📈 Aufwärtstrend (Kein Pullback)"
            else:
                status = "➖ Kein Trend"
                
            results.append({
                "Ticker": ticker,
                "Status": status,
                "Kurs": round(close, 2),
                "EMA 20": round(ema20, 2),
                "Abstand EMA20 (%)": round(dist_ema20_pct, 1),
                "Abstand 52W-Hoch (%)": round(((close / high_52w) - 1) * 100, 1)
            })
        except Exception:
            pass
            
        progress_bar.progress((idx + 1) / len(tickers))
        
    progress_bar.empty()
    return pd.DataFrame(results)

# ---------------------------------------------------------
# APP TABS: Scanner vs. Chart & Order-Rechner
# ---------------------------------------------------------
tab_scan, tab_chart = st.tabs(["🔍 MPS Auto-Scanner", "📊 Single Chart & Positionsrechner"])

with tab_scan:
    st.subheader("Automatischer MPS-Scanner")
    selected_list_name = st.selectbox("Watchlist für Scan wählen:", list(WATCHLISTS.keys()))
    
    if st.button("🚀 MPS-Scan jetzt starten"):
        with st.spinner("Scanne Aktien nach Aufwärtstrend & Pullback..."):
            scan_df = scan_mps_candidates(WATCHLISTS[selected_list_name])
            
            if not scan_df.empty:
                # Sortieren: MPS Setups ganz nach oben
                scan_df = scan_df.sort_values(by="Status", ascending=False)
                st.dataframe(scan_df, use_container_width=True)
                
                mps_setups = scan_df[scan_df["Status"].str.contains("PERFECT MPS")]
                if not mps_setups.empty:
                    st.success(f"Gefunden: **{len(mps_setups)}** aktuelle MPS-Setups!")
                else:
                    st.info("Aktuell kein perfekter Pullback in dieser Liste – Geduld auf den Rücksetzer!")
            else:
                st.warning("Keine Daten gefunden.")

with tab_chart:
    st.subheader("Chart-Analyse & Positionsgrößen-Berechnung")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        selected_watchlist = st.selectbox("Kategorie:", list(WATCHLISTS.keys()), key="chart_cat")
    with col_sel2:
        selected_ticker = st.selectbox("Aktie auswählen:", WATCHLISTS[selected_watchlist], key="chart_ticker")
        
    custom_ticker = st.text_input("Oder Ticker manuell eingeben (z. B. AAPL, SAP.DE):", "").upper()
    if custom_ticker:
        selected_ticker = custom_ticker

    # Realtime Data Fetch für Positionsrechner
    try:
        data = yf.Ticker(selected_ticker)
        fast_info = data.fast_info
        current_price = float(fast_info.get('lastPrice', 100.0))
    except Exception:
        current_price = 100.0

    st.markdown(f"### Aktueller Kurs für **{selected_ticker}**: `{current_price:.2f}`")
    
    # ---------------------------------------------------------
    # POSITIONSGRÖSSEN-RECHNER (MPS Regelwerk)
    # ---------------------------------------------------------
    st.markdown("#### 📐 Tradesetup & Positionsrechner")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        entry_price = st.number_input("Einstieg / Stop-Buy (€/$)", value=round(current_price * 1.005, 2), step=0.1)
    with col_p2:
        # Standardmäßig SL ca. 3% unter Einstieg (nahe Swing Low / EMA 20)
        stop_loss = st.number_input("Stop Loss (€/$)", value=round(entry_price * 0.97, 2), step=0.1)
    with col_p3:
        risk_per_share = entry_price - stop_loss
        if risk_per_share > 0:
            tp_price = entry_price + (risk_per_share * target_crv)
        else:
            tp_price = entry_price * 1.06
        take_profit = st.number_input(f"Take Profit (CRV {target_crv}:1)", value=round(tp_price, 2), step=0.1)

    if risk_per_share > 0:
        shares_to_buy = int(max_risk_amount / risk_per_share)
        total_position_size = shares_to_buy * entry_price
        
        st.success(f"""
        **Exakte Order-Vorgabe für deinen Broker:**
        * **Stückzahl:** `{shares_to_buy} Aktien`
        * **Positionsvolumen:** `{total_position_size:.2f} €`
        * **Maximaler Verlust bei SL:** `{(shares_to_buy * risk_per_share):.2f} €` ({risk_percentage}% vom Gesamtkonto)
        * **Möglicher Gewinn bei TP:** `{(shares_to_buy * (take_profit - entry_price)):.2f} €` (CRV {target_crv}:1)
        """)
    else:
        st.error("Stop Loss muss unter dem Einstiegspreis liegen!")

    # ---------------------------------------------------------
    # TRADINGVIEW CHART EMBED
    # ---------------------------------------------------------
    tv_ticker = selected_ticker.replace(".DE", "") # TradingView Ticker Bereinigung
    if ".DE" in selected_ticker:
        tv_symbol = f"XETR:{tv_ticker}"
    else:
        tv_symbol = f"NASDAQ:{tv_ticker}"

    tv_widget = f"""
    <div class="tradingview-widget-container" style="height:550px;width:100%;">
      <div id="tradingview_chart" style="height:500px;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "D",
        "timezone": "Europe/Berlin",
        "theme": "dark",
        "style": "1",
        "locale": "de_DE",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tv_widget, height=520)
