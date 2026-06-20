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

st.title("📈 Agente Portafoglio Titoli – Dashboard Interattiva")

securities = list_securities()
isin_list = [s.isin for s in securities]

selected_isin = st.selectbox("Seleziona ISIN", isin_list)

# DEBUG: mostra ticker
st.write("Ticker selezionato:", ISIN_TO_TICKER.get(selected_isin))

selected_date = st.date_input(
    "Seleziona la data",
    value=date(2024, 12, 30),
    min_value=date(2000, 1, 1),
    max_value=date.today()
)

if st.button("Mostra scheda titolo"):
    st.subheader("📄 Scheda titolo")
    st.text(summarize_security(selected_isin))

if st.button("Mostra prezzo storico"):
    provider = YahooFinanceProvider()
    st.subheader("💶 Prezzo storico")
    result = get_price_summary(selected_isin, selected_date, provider)
    st.text(result)

if st.button("Mostra grafico prezzi"):
    st.subheader("📉 Grafico storico dei prezzi (12 mesi)")
    series = get_price_series(selected_isin, months=12)

    if series is None:
        st.warning("Nessun dato disponibile per questo titolo.")
    else:
        st.line_chart(series)
