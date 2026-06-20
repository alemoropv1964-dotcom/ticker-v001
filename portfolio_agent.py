# file: portfolio_agent.py

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Dict

# =========================
# 1. Modello dati titoli
# =========================

@dataclass
class Security:
    isin: str
    name: str
    category: str
    asset_class: str
    notes: str = ""


SECURITIES: Dict[str, Security] = {
    "IT0003128367": Security("IT0003128367", "ENEL", "AZIONE", "Equity",
                             "Utility elettrica italiana, large cap, area Euro."),
    "IT0000062072": Security("IT0000062072", "GENERALI", "AZIONE", "Equity",
                             "Assicurazioni italiane, large cap."),
    "LU0908500753": Security("LU0908500753", "Amundi Core STOXX Europe 600 UCITS ETF Acc",
                             "ETF AZIONARIO", "Equity",
                             "Azionario Europa sviluppata, replica STOXX Europe 600."),
    "IE00BKM4GZ66": Security("IE00BKM4GZ66", "iShares Core MSCI Emerging Markets IMI UCITS ETF",
                             "ETF AZIONARIO", "Equity",
                             "Azionario Paesi Emergenti, replica MSCI EM IMI."),
    "IE00B4L5Y983": Security("IE00B4L5Y983", "iShares Core MSCI World UCITS ETF",
                             "ETF AZIONARIO", "Equity",
                             "Azionario globale Paesi sviluppati, replica MSCI World."),
    "IE00BFZPF439": Security("IE00BFZPF439", "Invesco AT1 Capital Bond UCITS ETF EUR Hedged Dist",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Obbligazioni bancarie AT1 (CoCo), rischio elevato."),
    "IE00B9M6RS56": Security("IE00B9M6RS56", "iShares JPM $ Emerging Markets Bond EUR Hedged",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Obbligazioni Paesi Emergenti in USD, coperto in EUR."),
    "IE00BJK55C48": Security("IE00BJK55C48", "iShares EUR High Yield Corporate Bond ETF",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Corporate high yield in EUR."),
    "IE00BYXYYK40": Security("IE00BYXYYK40", "iShares JPMorgan USD Emerging Markets Bond ETF",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Obbligazioni Paesi Emergenti in USD."),
    "LU1645380368": Security("LU1645380368", "UBS ETF Euro Inflation Linked 1-10",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Obbligazioni area Euro indicizzate all'inflazione."),
    "IE00BH04GL39": Security("IE00BH04GL39", "Vanguard Eurozone Government Bond UCITS ETF",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Obbligazioni governative area Euro."),
    "LU1109943388": Security("LU1109943388", "Xtrackers II EUR High Yield Corporate Bond ETF",
                             "ETF OBBLIGAZIONARIO", "Bond",
                             "Corporate high yield in EUR."),
    "IE00B579F325": Security("IE00B579F325", "Source Physical Gold ETC (EUR)",
                             "ETC", "Commodity",
                             "ETC fisico sull'oro."),
}

# =========================
# 2. Mapping ISIN → ticker
# =========================

ISIN_TO_TICKER = {
    "IT0003128367": "ENEL.MI",
    "IT0000062072": "G.MI",
    "LU0908500753": "CEU6.MI",
    "IE00BKM4GZ66": "EIMI.MI",
    "IE00B4L5Y983": "SWDA.MI",
    "IE00BFZPF439": "AT1H.L",
    "IE00B9M6RS56": "EMBE.MI",
    "IE00BJK55C48": "IHYG.MI",
    "IE00BYXYYK40": "SEMB.MI",
    "LU1645380368": "EI1U.DE",
    "IE00BH04GL39": "VEGB.MI",
    "LU1109943388": "XHYG.DE",
    "IE00B579F325": "SGLD.MI",
}

# =========================
# 3. Funzioni agente
# =========================

def list_securities() -> List[Security]:
    return list(SECURITIES.values())


def get_security(isin: str) -> Optional[Security]:
    return SECURITIES.get(isin)


def summarize_security(isin: str) -> str:
    sec = get_security(isin)
    if sec is None:
        return f"Nessun titolo trovato per ISIN {isin}."
    return (
        f"Titolo: {sec.name}\n"
        f"ISIN: {sec.isin}\n"
        f"Categoria: {sec.category}\n"
        f"Asset class: {sec.asset_class}\n"
        f"Note: {sec.notes}"
    )

# =========================
# 4. Provider dati di mercato
# =========================

class MarketDataProvider:
    def get_price_on(self, isin: str, d: date) -> Optional[float]:
        raise NotImplementedError


try:
    import yfinance as yf
except ImportError:
    yf = None


class YahooFinanceProvider(MarketDataProvider):
    def get_price_on(self, isin: str, d: date) -> Optional[float]:
        if yf is None:
            raise RuntimeError("yfinance non è installato.")

        ticker = ISIN_TO_TICKER.get(isin)
        if ticker is None:
            raise ValueError(f"Nessun ticker associato all'ISIN {isin}.")

        from datetime import timedelta
        ds = d.isoformat()
        de = (d + timedelta(days=1)).isoformat()

        data = yf.download(ticker, start=ds, end=de)

        if data.empty:
            return None

        close_value = data["Close"].iloc[0]

        # 🔧 PATCH ROBUSTA
        if hasattr(close_value, "item"):
            close_value = close_value.item()

        return close_value


# =========================
# 5. Funzione di alto livello
# =========================

def get_price_summary(isin: str, d: date, provider: MarketDataProvider) -> str:
    sec = get_security(isin)
    if sec is None:
        return f"Nessun titolo trovato per ISIN {isin}."

    price = provider.get_price_on(isin, d)
    if price is None:
        return f"Nessun dato disponibile per {sec.name} alla data {d}."

    return (
        f"Titolo: {sec.name} (ISIN {isin})\n"
        f"Data: {d}\n"
        f"Prezzo di chiusura: {price:.4f}"
    )


# =========================
# 6. Esempio d’uso
# =========================

if __name__ == "__main__":
    from datetime import date

    print("=== TITOLI IN PORTAFOGLIO ===")
    for s in list_securities():
        print(f"- {s.isin} | {s.name} | {s.category}")

    print("\n=== SCHEDA TITOLO IE00B4L5Y983 ===")
    print(summarize_security("IE00B4L5Y983"))

    provider = YahooFinanceProvider()
    d = date(2024, 12, 30)

    print("\n=== PREZZO STORICO IE00B4L5Y983 ===")
    print(get_price_summary("IE00B4L5Y983", d, provider))
