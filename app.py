import streamlit as st
from datetime import date
import pandas as pd
import yfinance as yf

from portfolio_agent import (
    list_securities,
    summarize_security,
    get_price_summary,
    YahooFinanceProvider,
    ISIN_TO_TICKER
)

# =========================
# Funzione per serie storica
# =========================

def get_price_series(isin: str, months: int = 12):
    from datetime import datetime, timedelta

    ticker = ISIN_TO_TICKER.get(isin)
    if ticker is None:
        return None

    end = datetime.today()
    start = end - timedelta(days=30 * months)

    data = yf.download(ticker, start=start, end=end)

    if data.empty:
        return None

    return data["Close"]


# =========================
# UI Streamlit
# =========================

st.title("📈 Agente Portafoglio Titoli – Dashboard Interattiva")

st.write("Seleziona un titolo e una data per visualizzare scheda, prezzo storico e grafico.")

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

# 5) Mostra grafico prezzi
if st.button("Mostra grafico prezzi"):
    st.subheader("📉 Grafico storico dei prezzi (12 mesi)")
    series = get_price_series(selected_isin, months=12)

    if series is None:
        st.warning("Nessun dato disponibile per questo titolo.")
    else:
        st.line_chart(series)
