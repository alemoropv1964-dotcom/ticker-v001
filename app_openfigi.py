# app_openfigi.py
import streamlit as st
import requests
import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path

# Config
CACHE_FILE = Path("figi_cache.json")
CACHE_TTL = 60 * 60 * 24 * 7  # 7 giorni

# Carica o inizializza cache
if CACHE_FILE.exists():
    try:
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
else:
    cache = {}

def save_cache():
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        st.warning(f"Impossibile salvare cache: {e}")

def openfigi_map_isin(isin, api_key):
    now = int(time.time())
    # Usa cache se valida
    if isin in cache:
        entry = cache[isin]
        if now - entry.get("ts", 0) < CACHE_TTL:
            return entry["results"]
    url = "https://api.openfigi.com/v3/mapping"
    headers = {"Content-Type": "application/json", "X-OPENFIGI-APIKEY": api_key}
    payload = [{"idType": "ID_ISIN", "idValue": isin}]
    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"OpenFIGI error {resp.status_code}: {resp.text}")
    data = resp.json()
    results = data[0].get("data", []) if isinstance(data, list) else []
    cache[isin] = {"ts": now, "results": results}
    save_cache()
    return results

def choose_ticker_from_figi_results(results):
    choices = []
    for r in results:
        ticker = r.get("ticker") or r.get("compositeFIGI") or r.get("exchCode")
        name = r.get("name") or r.get("securityType") or ""
        exch = r.get("exchCode") or r.get("exchange")
        # For ETFs sometimes 'ticker' is empty; try 'shareClassFIGI' or 'compositeFIGI'
        if ticker:
            choices.append({"ticker": ticker, "name": name, "exchange": exch, "figi": r.get("figi")})
    return choices

def fetch_price_and_plot(ticker, start_date):
    df = yf.download(ticker, start=start_date, end=datetime.today().strftime("%Y-%m-%d"), progress=False)
    if df.empty:
        raise Exception("Dati non disponibili per il ticker richiesto.")
    return df

# Lista ISIN estratta dal documento
ISIN_LIST = [
"IT0003128367","IT0000062072","LU0908500753","IE00BKM4GZ66","IE00B4L5Y983",
"IE00BFZPF439","IE00B9M6RS56","IE00BJK55C48","IE00BYXYYK40","LU1645380368",
"IE00BH04GL39","LU1109943388","IE00B579F325"
]

st.set_page_config(page_title="ISIN → Ticker con OpenFIGI", layout="wide")
st.title("Risoluzione automatica ISIN → ticker e grafico prezzi")

st.markdown("Inserisci la tua **OpenFIGI API Key** per risolvere automaticamente ISIN → ticker. La chiave non viene salvata su server esterni; rimane locale nella sessione.")

api_key = st.text_input("OpenFIGI API Key", type="password")

selected_isin = st.selectbox("Seleziona ISIN", ISIN_LIST)
st.write(f"**ISIN selezionato**: {selected_isin}")

if not api_key:
    st.info("Per risolvere automaticamente i ticker è necessaria la OpenFIGI API Key. Puoi ottenere la chiave registrandoti su openfigi.com.")
else:
    if st.button("Risolvi ticker con OpenFIGI"):
        try:
            results = openfigi_map_isin(selected_isin, api_key)
            choices = choose_ticker_from_figi_results(results)
            if not choices:
                st.warning("Nessun mapping trovato su OpenFIGI per questo ISIN.")
            else:
                opt_labels = [f"{c['ticker']} — {c['name']} — exch:{c['exchange']}" for c in choices]
                pick = st.selectbox("Scegli il ticker corretto (se più di uno)", opt_labels, key=f"pick_{selected_isin}")
                idx = opt_labels.index(pick)
                chosen = choices[idx]
                st.success(f"Ticker scelto: {chosen['ticker']}")
                st.session_state['chosen_ticker'] = chosen['ticker']
                # Mostra metadati utili
                st.json(chosen)
        except Exception as e:
            st.error(f"Errore OpenFIGI: {e}")

# Campo per inserire manualmente o sovrascrivere ticker
manual = st.text_input("Oppure inserisci manualmente il ticker (es. ENEL.MI)", value=st.session_state.get('chosen_ticker',''))
start_date = st.date_input("Data di inizio storico", value=datetime(2025,1,1), max_value=datetime.today())

col1, col2 = st.columns([2,1])
with col1:
    if st.button("Mostra prezzo e grafico"):
        ticker = manual.strip()
        if not ticker:
            st.error("Inserisci o risolvi un ticker prima di procedere.")
        else:
            try:
                df = fetch_price_and_plot(ticker, start_date.strftime("%Y-%m-%d"))
                current_price = df['Close'].iloc[-1]
                # Prova a leggere la valuta dal ticker info (se disponibile)
                try:
                    info = yf.Ticker(ticker).info
                    currency = info.get('currency', 'EUR')
                except Exception:
                    currency = 'EUR'
                st.metric("Prezzo corrente", f"{current_price:.2f} {currency}")
                st.line_chart(df['Close'].rename('Prezzo'))
                # Metriche sintetiche
                if len(df) > 22:
                    perf_1m = (df['Close'].iloc[-1] / df['Close'].iloc[-22] - 1) * 100
                    st.write(f"Performance 1 mese: {perf_1m:.2f}%")
                else:
                    st.write("Performance 1 mese: dati insufficienti")
                if len(df) > 66:
                    perf_3m = (df['Close'].iloc[-1] / df['Close'].iloc[-66] - 1) * 100
                    st.write(f"Performance 3 mesi: {perf_3m:.2f}%")
                else:
                    st.write("Performance 3 mesi: dati insufficienti")
            except Exception as e:
                st.error(f"Errore nel recupero dati: {e}")

with col2:
    st.markdown("**Azioni rapide**")
    if st.button("Esporta mappatura cache CSV"):
        # Esporta cache in CSV con ISIN, ticker possibili
        rows = []
        for k,v in cache.items():
            results = v.get("results", [])
            tickers = []
            for r in results:
                t = r.get("ticker")
                if t:
                    tickers.append(t)
            rows.append({"isin": k, "tickers": ";".join(tickers)})
        df_cache = pd.DataFrame(rows)
        if df_cache.empty:
            st.info("Cache vuota.")
        else:
            csv = df_cache.to_csv(index=False).encode('utf-8')
            st.download_button("Scarica CSV mappatura", data=csv, file_name="figi_cache_mapping.csv", mime="text/csv")

st.markdown("**Note**: la cache evita chiamate ripetute a OpenFIGI. Se OpenFIGI restituisce più listing, scegli quello corretto in base all'exchange (es. .MI per Borsa Italiana).")
