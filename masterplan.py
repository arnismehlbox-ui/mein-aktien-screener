import streamlit as st
import pandas as pd
import yfinance as yf

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Renten-Masterplan", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    .metric-box { background-color: #1e222d; padding: 15px; border-radius: 8px; border-left: 5px solid #2962ff; margin-bottom: 15px; }
    .metric-box-green { border-left-color: #26a69a; }
    </style>
""", unsafe_allow_html=True)

st.title("👑 Der Masterplan: Freiheit ab 68")

# ---------------------------------------------------------
# HELPER: BERECHNUNGS-LOGIK (Monat für Monat)
# ---------------------------------------------------------
def calculate_wealth(start_cap, monthly_base, monthly_booster, booster_start_month, years, yield_pa):
    months_total = int(years * 12)
    monthly_rate = (yield_pa / 100) / 12
    
    cap = start_cap
    invested = start_cap
    history = [{"Monat": 0, "Jahr": 0, "Depotwert": cap, "Eingezahlt": invested}]
    
    for m in range(1, months_total + 1):
        deposit = monthly_base
        if m > booster_start_month:
            deposit += monthly_booster
            
        cap = cap * (1 + monthly_rate) + deposit
        invested += deposit
        
        if m % 12 == 0:
            history.append({"Monat": m, "Jahr": m//12, "Depotwert": round(cap, 2), "Eingezahlt": round(invested, 2)})
            
    return pd.DataFrame(history), cap, invested

def calc_pension(final_capital):
    div_capital = final_capital * 0.70
    cc_capital = final_capital * 0.30
    
    div_monthly = (div_capital * 0.05) / 12  # 5% Netto-Dividende
    cc_monthly = (cc_capital * 0.08) / 12    # 8% Netto-Stillhalter ETF
    
    return div_monthly + cc_monthly, div_capital, cc_capital

# ---------------------------------------------------------
# HELPER: LIVE DIVIDENDEN DER ELITE 7
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_elite_dividends():
    tickers = ["MSFT", "AVGO", "SAP.DE", "V", "ALV.DE", "PG", "O"]
    # Fallbacks falls Yahoo Finance API klemmt
    fallbacks = {"MSFT": 0.73, "AVGO": 1.20, "SAP.DE": 1.35, "V": 0.72, "ALV.DE": 4.50, "PG": 2.40, "O": 5.30}
    
    data = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            div = info.get('dividendYield')
            if div is not None:
                div_pct = div
            else:
                div_pct = fallbacks[t]
        except:
            div_pct = fallbacks[t]
            
        data.append({"Aktie": t, "Live Dividendenrendite": f"{div_pct:.2f} %"})
        
    return pd.DataFrame(data)

# ---------------------------------------------------------
# TABS AUFBAUEN
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🔒 1. Fixer Masterplan", "🎯 2. Ist-Zustand Tracker", "🎛️ 3. Spielwiese (Kalkulator)"])

# ==========================================
# TAB 1: FIXER MASTERPLAN
# ==========================================
with tab1:
    st.subheader("Dein verbindlicher Plan (Stand September 2026)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Der 80/20 Maschinenraum:**
        * **Startkapital:** 1.080 € (Elite 7) + 270 € (MPS Swing)
        * **Sparrate (Basis):** 320 € (Elite 7) + 80 € (MPS)
        * **Booster (ab 06/2030):** +170 € (Nach Kreditende)
        * **Geplante Laufzeit:** 14 Jahre (bis Alter 68)
        * **Ziel-Rendite:** 11 % p.a. (Elite 7) | 15 % p.a. (MPS)
        """)
        
    with col2:
        st.markdown("**Live Dividendenrenditen (Elite 7):**")
        df_divs = get_elite_dividends()
        st.dataframe(df_divs, hide_index=True)
        
    st.markdown("---")
    
    # Feste Berechnung Elite 7 (Booster fließt voll in Elite)
    df_elite, final_elite, inv_elite = calculate_wealth(1080, 320, 170, 45, 14, 11)
    # Feste Berechnung MPS
    df_mps, final_mps, inv_mps = calculate_wealth(270, 80, 0, 45, 14, 15)
    
    total_final = final_elite + final_mps
    pension_net, part_div, part_cc = calc_pension(total_final)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-box'><b>📈 Endkapital Elite 7:</b><br><h2 style='margin:0;color:#2962ff;'>{final_elite:,.0f} €</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-box'><b>⚔️ Endkapital MPS:</b><br><h2 style='margin:0;color:#2962ff;'>{final_mps:,.0f} €</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-box metric-box-green'><b>💰 Rente (Netto/Monat):</b><br><h2 style='margin:0;color:#26a69a;'>{pension_net:,.0f} €</h2></div>", unsafe_allow_html=True)
    
    st.line_chart(df_elite.set_index("Jahr")["Depotwert"], height=300)

# ==========================================
# TAB 2: IST-ZUSTAND TRACKER
# ==========================================
with tab2:
    st.subheader("Aktueller Stand & Anpassung an die Realität")
    st.info("Trage hier regelmäßig deinen tatsächlichen Depotwert ein, um zu sehen, ob du noch auf Kurs für deine Zielrente bist.")
    
    tc1, tc2 = st.columns(2)
    with tc1:
        ist_elite = st.number_input("Aktueller Wert Elite 7 Depot (€):", value=1080.0, step=100.0)
        ist_mps = st.number_input("Aktueller Wert MPS Verrechnungskonto (€):", value=270.0, step=100.0)
    with tc2:
        rest_jahre = st.number_input("Verbleibende Jahre bis zur Rente:", value=14.0, step=0.5)
        rest_monate_booster = st.number_input("Monate bis Kredit wegfällt (Booster Start):", value=45, step=1)
        
    df_elite_ist, final_elite_ist, _ = calculate_wealth(ist_elite, 320, 170, rest_monate_booster, rest_jahre, 11)
    df_mps_ist, final_mps_ist, _ = calculate_wealth(ist_mps, 80, 0, rest_monate_booster, rest_jahre, 15)
    
    total_ist = final_elite_ist + final_mps_ist
    pension_net_ist, _, _ = calc_pension(total_ist)
    
    st.markdown("---")
    st.markdown(f"### 🎯 Neue Prognose basierend auf deinem Ist-Zustand")
    st.markdown(f"Erwartetes Gesamtkapital: **{total_ist:,.0f} €**")
    st.markdown(f"<h3 style='color:#26a69a;'>💸 Erwarteter Rentenzuschuss: {pension_net_ist:,.0f} € Netto / Monat</h3>", unsafe_allow_html=True)


# ==========================================
# TAB 3: SPIELWIESE (KALKULATOR)
# ==========================================
with tab3:
    st.subheader("Was wäre wenn...? (Freier Rechner)")
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("**Startkapital & Laufzeit**")
        v_start_elite = st.number_input("Startkapital Elite (€)", value=1080, step=100)
        v_start_mps = st.number_input("Startkapital MPS (€)", value=270, step=100)
        v_jahre = st.slider("Jahre bis zur Rente", min_value=1, max_value=25, value=14)
        
    with sc2:
        st.markdown("**Sparraten & Booster**")
        v_rate_elite = st.number_input("Mtl. Rate Elite (€)", value=320, step=10)
        v_rate_mps = st.number_input("Mtl. Rate MPS (€)", value=80, step=10)
        v_booster = st.number_input("Kredit-Booster Summe (€)", value=170, step=10)
        v_booster_start = st.slider("Booster startet in X Monaten", min_value=0, max_value=120, value=45)
        
    with sc3:
        st.markdown("**Rendite-Annahmen (% p.a.)**")
        v_rendite_elite = st.slider("Rendite Elite 7", min_value=2.0, max_value=20.0, value=11.0, step=0.5)
        v_rendite_mps = st.slider("Rendite MPS", min_value=2.0, max_value=30.0, value=15.0, step=0.5)
        
    # Frei berechnen
    df_elite_free, final_elite_free, _ = calculate_wealth(v_start_elite, v_rate_elite, v_booster, v_booster_start, v_jahre, v_rendite_elite)
    df_mps_free, final_mps_free, _ = calculate_wealth(v_start_mps, v_rate_mps, 0, v_booster_start, v_jahre, v_rendite_mps)
    
    total_free = final_elite_free + final_mps_free
    pension_net_free, _, _ = calc_pension(total_free)
    
    st.markdown("---")
    st.markdown("### 📊 Simulations-Ergebnis")
    
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Gesamtkapital Elite 7", f"{final_elite_free:,.0f} €")
    fc2.metric("Gesamtkapital MPS", f"{final_mps_free:,.0f} €")
    fc3.markdown(f"<h3 style='color:#26a69a; margin-top:0;'>Passive Rente: {pension_net_free:,.0f} € / Monat</h3>", unsafe_allow_html=True)
    
    st.markdown("**(Hybrid-Entnahme: 70% in 5% Netto-Dividenden, 30% in 8% Netto-Stillhalter ETF)**")
    
    # Kombinierter Chart für die Spielwiese
    df_combined = pd.DataFrame({
        "Jahr": df_elite_free["Jahr"],
        "Elite 7 Wert": df_elite_free["Depotwert"],
        "MPS Wert": df_mps_free["Depotwert"]
    }).set_index("Jahr")
    
    st.line_chart(df_combined, height=350)
