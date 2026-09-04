import streamlit as st
import yfinance as yf
import pandas as pd

# Konfiguration der App-Oberfläche
st.set_page_config(page_title="Aktien-Screener", page_icon="📈", layout="wide")

st.title("📈 Mein persönlicher Börsen-Screener")
st.caption("Scanne europäische und US-Märkte mit einem Klick.")

# Markt-Auswahl per Button
markt = st.radio("Wähle den Markt:", ["Europa 🇪🇺", "USA 🇺🇸"], horizontal=True)

# Beispiel-Standardlisten (beliebig erweiterbar)
TICKERS_EUROPA = ["SAP.DE", "SIE.DE", "ALV.DE", "AIR.PA", "OR.PA", "ASML.AS", "NESN.SW", "NOVN.SW", "RMS.PA"]
TICKERS_USA = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JNJ", "PG"]

if st.button("🚀 Scan jetzt starten", use_container_width=True):
    auswahl = TICKERS_EUROPA if "Europa" in markt else TICKERS_USA
    st.info(f"Scanne {len(auswahl)} Werte... Bitte kurz warten.")
    
    ergebnisse = []
    progress_bar = st.progress(0)
    
    for idx, symbol in enumerate(auswahl):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            
            kurs = info.last_price
            prev = info.previous_close
            aenderung = ((kurs - prev) / prev) * 100 if prev else 0
            
            ergebnisse.append({
                "Aktie": symbol,
                "Kurs": round(kurs, 2),
                "Veränderung (%)": round(aenderung, 2),
                "52W-Hoch": round(info.year_high, 2) if hasattr(info, 'year_high') else "N/A",
                "52W-Tief": round(info.year_low, 2) if hasattr(info, 'year_low') else "N/A"
            })
        except Exception:
            pass
        
        progress_bar.progress((idx + 1) / len(auswahl))
        
    df = pd.DataFrame(ergebnisse)
    
    st.success("Scan abgeschlossen!")
    st.dataframe(df, use_container_width=True)
