import streamlit as st
from datetime import date
from portfolio_agent import (
    list_securities,
    summarize_security,
    get_price_summary,
    YahooFinanceProvider
)

# =========================
# UI Streamlit
# =========================

st.title("📈 Agente Portafoglio Titoli – Versione Interattiva")

st.write("Seleziona un titolo dal menu a tendina e scegli una data per ottenere il prezzo storico.")

# 1) Menu a tendina ISIN
securities = list_securities()
isin_list = [s.isin for s in securities]

selected_isin = st.selectbox("Seleziona ISIN", isin_list)

# 2) Selettore data
selected_date = st.date_input(
    "Seleziona la data",
    value=date(2024, 12, 30),
    min_value=date(2000, 1, 1),
    max_value=date.today()
)

# 3) Mostra scheda titolo
if st.button("Mostra scheda titolo"):
    st.subheader("📄 Scheda titolo")
    st.text(summarize_security(selected_isin))

# 4) Mostra prezzo storico
if st.button("Mostra prezzo storico"):
    provider = YahooFinanceProvider()
    st.subheader("💶 Prezzo storico")
    result = get_price_summary(selected_isin, selected_date, provider)
    st.text(result)
