import streamlit as st
import yfinance as yf
import pandas as pd

# Seitentitel & Konfiguration
st.set_page_config(page_title="Aktien-Screener Pro", layout="wide", page_icon="📈")

st.title("📈 Mein persönlicher Börsen-Screener Pro")
st.caption("Echtzeit-Analyse für Trading-Setups (RVOL, RSI-14, Trends & eigene Ticker)")

# Marktauswahl direkt auf der Hauptseite
markt = st.radio("Wähle den Markt:", ("Europa 🇪🇺", "USA 🇺🇸", "Kombiniert (EU + USA)"), horizontal=True)

# Standard-Listen
TICKERS_EUROPA = ['SAP.DE', 'SIE.DE', 'ALV.DE', 'AIR.PA', 'OR.PA', 'ASML.AS', 'NESN.SW', 'NOVN.SW', 'RMS.PA', 'RHM.DE']
TICKERS_USA = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD', 'SPY', 'QQQ', 'O']

if markt == "Europa 🇪🇺":
    base_tickers = TICKERS_EUROPA
elif markt == "USA 🇺🇸":
    base_tickers = TICKERS_USA
else:
    base_tickers = TICKERS_EUROPA + TICKERS_USA

# Freitext-Eingabe für eigene Ticker
custom_input = st.text_input(
    "➕ Eigene Ticker manuell hinzufügen (kommagetrennt):",
    placeholder="z.B. PLTR, BABA, DIS"
)

# Sortierung
sort_by = st.selectbox(
    "Sortieren nach:",
    ("Veränderung (%)", "RVOL", "RSI (14)", "Abstand 52W-Hoch (%)", "Volumen (Tsd)")
)

# Ticker zusammenführen
additional_tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]
all_tickers = list(dict.fromkeys(base_tickers + additional_tickers))

st.write(f"Anzahl der Werte im Scan: **{len(all_tickers)} Ticker**")

if st.button("🚀 Scan jetzt starten", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    data = []
    total = len(all_tickers)
    
    for i, symbol in enumerate(all_tickers):
        status_text.text(f"Analysiere {symbol} ({i+1}/{total})...")
        progress_bar.progress((i + 1) / total)
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if len(hist) >= 20:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                # RVOL (Heute Vol / 20T Ø Vol)
                current_vol = hist['Volume'].iloc[-1]
                avg_vol_20 = hist['Volume'].iloc[-21:-1].mean()
                rvol = (current_vol / avg_vol_20) if avg_vol_20 > 0 else 0
                
                # RSI (14 Tage)
                delta = hist['Close'].diff()
                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)
                avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                rs = avg_gain / avg_loss
                rsi_series = 100 - (100 / (1 + rs))
                current_rsi = rsi_series.iloc[-1]
                
                # 52W Hoch & Abstand
                high_52 = hist['High'].max()
                dist_high_pct = ((current_price - high_52) / high_52) * 100
                
                # SMA 20 & Abstand
                sma20 = hist['Close'].tail(20).mean()
                dist_sma20 = ((current_price - sma20) / sma20) * 100
                
                # Marktkapitalisierung (Mrd. USD/EUR)
                info = ticker.info or {}
                mcap = info.get('marketCap', 0)
                mcap_mrd = round(mcap / 1e9, 1) if mcap else 0
                
                data.append({
                    "Aktie": symbol,
                    "Kurs": round(current_price, 2),
                    "Veränderung (%)": round(change_pct, 2),
                    "RVOL": round(rvol, 2),
                    "RSI (14)": round(current_rsi, 1),
                    "Abstand SMA20 (%)": round(dist_sma20, 2),
                    "Abstand 52W-Hoch (%)": round(dist_high_pct, 2),
                    "Volumen (Tsd)": int(current_vol / 1000),
                    "Market Cap (Mrd)": mcap_mrd if mcap_mrd > 0 else "N/A"
                })
        except Exception:
            continue

    status_text.empty()
    progress_bar.empty()

    if data:
        df = pd.DataFrame(data)
        
        # Sortierung anwenden
        ascending = False if sort_by in ["Veränderung (%)", "RVOL", "Volumen (Tsd)"] else True
        if sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
        
        st.success("✅ Scan erfolgreich abgeschlossen!")
        
        # Tabelle anzeigen
        st.dataframe(
            df,
            column_config={
                "Veränderung (%)": st.column_config.NumberColumn(format="%.2f %%"),
                "Abstand SMA20 (%)": st.column_config.NumberColumn(format="%.2f %%"),
                "Abstand 52W-Hoch (%)": st.column_config.NumberColumn(format="%.2f %%"),
                "RVOL": st.column_config.NumberColumn(format="%.2f x"),
                "RSI (14)": st.column_config.NumberColumn(format="%.1f"),
                "Kurs": st.column_config.NumberColumn(format="%.2f"),
                "Volumen (Tsd)": st.column_config.NumberColumn(format="%d k"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error("Keine gültigen Daten gefunden. Bitte prüfe die Ticker-Eingabe.")
