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
    category: str          # "AZIONE", "ETF AZIONARIO", "ETF OBBLIGAZIONARIO", "ETC"
    asset_class: str       # "Equity", "Bond", "Commodity"
    notes: str = ""        # descrizione sintetica / focus


# Dizionario dei titoli estratti dal rendiconto
SECURITIES: Dict[str, Security] = {
    # AZIONI
    "IT0003128367": Security(
        isin="IT0003128367",
        name="ENEL",
        category="AZIONE",
        asset_class="Equity",
        notes="Utility elettrica italiana, large cap, area Euro."
    ),
    "IT0000062072": Security(
        isin="IT0000062072",
        name="GENERALI",
        category="AZIONE",
        asset_class="Equity",
        notes="Assicurazioni, large cap italiana, area Euro."
    ),

    # ETF AZIONARI
    "LU0908500753": Security(
        isin="LU0908500753",
        name="Amundi Core STOXX Europe 600 UCITS ETF Acc",
        category="ETF AZIONARIO",
        asset_class="Equity",
        notes="Azionario Europa sviluppata, replica STOXX Europe 600, ad accumulazione."
    ),
    "IE00BKM4GZ66": Security(
        isin="IE00BKM4GZ66",
        name="iShares Core MSCI Emerging Markets IMI UCITS ETF",
        category="ETF AZIONARIO",
        asset_class="Equity",
        notes="Azionario Paesi Emergenti, replica MSCI EM IMI, molto diversificato."
    ),
    "IE00B4L5Y983": Security(
        isin="IE00B4L5Y983",
        name="iShares Core MSCI World UCITS ETF",
        category="ETF AZIONARIO",
        asset_class="Equity",
        notes="Azionario globale Paesi sviluppati, replica MSCI World."
    ),

    # ETF OBBLIGAZIONARI
    "IE00BFZPF439": Security(
        isin="IE00BFZPF439",
        name="Invesco AT1 Capital Bond UCITS ETF EUR Hedged Dist",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni bancarie AT1 (CoCo), rischio elevato, distribuzione cedole."
    ),
    "IE00B9M6RS56": Security(
        isin="IE00B9M6RS56",
        name="iShares JPM $ Emerging Markets Bond EUR Hedged",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni Paesi Emergenti in USD, coperto in EUR."
    ),
    "IE00BJK55C48": Security(
        isin="IE00BJK55C48",
        name="iShares EUR High Yield Corporate Bond ETF",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni corporate high yield in EUR."
    ),
    "IE00BYXYYK40": Security(
        isin="IE00BYXYYK40",
        name="iShares JPMorgan USD Emerging Markets Bond ETF",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni Paesi Emergenti in USD, non coperto in EUR."
    ),
    "LU1645380368": Security(
        isin="LU1645380368",
        name="UBS ETF Euro Inflation Linked 1-10",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni area Euro indicizzate all'inflazione, scadenze 1-10 anni."
    ),
    "IE00BH04GL39": Security(
        isin="IE00BH04GL39",
        name="Vanguard Eurozone Government Bond UCITS ETF",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni governative area Euro."
    ),
    "LU1109943388": Security(
        isin="LU1109943388",
        name="Xtrackers II EUR High Yield Corporate Bond ETF",
        category="ETF OBBLIGAZIONARIO",
        asset_class="Bond",
        notes="Obbligazioni corporate high yield in EUR."
    ),

    # ETC
    "IE00B579F325": Security(
        isin="IE00B579F325",
        name="Source Physical Gold ETC (EUR)",
        category="ETC",
        asset_class="Commodity",
        notes="ETC fisico sull'oro, esposto al prezzo dell'oro in EUR."
    ),
}


# =========================
# 2. Mapping ISIN → ticker
# =========================

ISIN_TO_TICKER: Dict[str, str] = {
    # AZIONI (Borsa Italiana)
    "IT0003128367": "ENEL.MI",
    "IT0000062072": "G.MI",

    # ETF AZIONARI
    "LU0908500753": "CEU6.MI",   # Amundi STOXX Europe 600
    "IE00BKM4GZ66": "EIMI.MI",   # iShares Core MSCI EM IMI
    "IE00B4L5Y983": "SWDA.MI",   # iShares Core MSCI World

    # ETF OBBLIGAZIONARI
    "IE00BFZPF439": "AT1H.L",    # Invesco AT1 Capital Bond EUR Hedged (LSE)
    "IE00B9M6RS56": "EMBE.MI",   # iShares JPM $ EM Bond EUR Hedged
    "IE00BJK55C48": "IHYG.MI",   # iShares EUR High Yield Corp
    "IE00BYXYYK40": "SEMB.MI",   # iShares JPM USD EM Bond
    "LU1645380368": "EI1U.DE",   # UBS Euro Inflation Linked 1–10 (XETRA)
    "IE00BH04GL39": "VEGB.MI",   # Vanguard Eurozone Gov Bond
    "LU1109943388": "XHYG.DE",   # Xtrackers EUR High Yield Corp (XETRA)

    # ETC ORO
    "IE00B579F325": "SGLD.MI",   # Source Physical Gold ETC
}


# =========================
# 3. Interfaccia dell'agente
# =========================

def list_securities() -> List[Security]:
    """Restituisce la lista completa dei titoli in portafoglio."""
    return list(SECURITIES.values())


def get_security(isin: str) -> Optional[Security]:
    """Restituisce il titolo corrispondente all'ISIN, se presente."""
    return SECURITIES.get(isin)


def summarize_security(isin: str) -> str:
    """Restituisce una descrizione testuale sintetica del titolo."""
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
    """
    Interfaccia astratta per un provider di dati di mercato.
    Va implementata collegandosi a una vera API (es. yfinance, EOD, ecc.).
    """

    def get_price_on(self, isin: str, d: date) -> Optional[float]:
        """Restituisce il prezzo di chiusura alla data d per il titolo con ISIN dato."""
        raise NotImplementedError


# Implementazione di esempio con yfinance
try:
    import yfinance as yf
except ImportError:
    yf = None


class YahooFinanceProvider(MarketDataProvider):
    """
    Implementazione di esempio usando yfinance.
    Richiede:
        pip install yfinance
    """

    def get_price_on(self, isin: str, d: date) -> Optional[float]:
        if yf is None:
            raise RuntimeError("yfinance non è installato. Esegui: pip install yfinance")

        ticker = ISIN_TO_TICKER.get(isin)
        if ticker is None:
            raise ValueError(f"Nessun ticker associato all'ISIN {isin} nel mapping ISIN_TO_TICKER.")

        ds = d.isoformat()
        # yfinance: l'end è esclusivo, quindi usiamo il giorno successivo
        from datetime import timedelta
        de = (d + timedelta(days=1)).isoformat()

        data = yf.download(ticker, start=ds, end=de)
        if data.empty:
            return None

        return float(data["Close"].iloc[0])


# =========================
# 5. Funzione di alto livello per l'agente
# =========================

def get_price_summary(isin: str, d: date, provider: MarketDataProvider) -> str:
    """
    Restituisce una stringa con il prezzo del titolo alla data indicata.
    """
    sec = get_security(isin)
    if sec is None:
        return f"Nessun titolo trovato per ISIN {isin}."

    price = provider.get_price_on(isin, d)
    if price is None:
        return (
            f"Nessun dato di prezzo disponibile per {sec.name} (ISIN {isin}) "
            f"alla data {d.isoformat()}."
        )

    return (
        f"Titolo: {sec.name} (ISIN {isin})\n"
        f"Data: {d.isoformat()}\n"
        f"Prezzo di chiusura: {price:.4f}"
    )


# =========================
# 6. Esempio d'uso da riga di comando
# =========================

if __name__ == "__main__":
    from datetime import date

    print("=== TITOLI IN PORTAFOGLIO ===")
    for s in list_securities():
        print(f"- {s.isin} | {s.name} | {s.category}")

    print("\n=== SCHEDA TITOLO IE00B4L5Y983 ===")
    print(summarize_security("IE00B4L5Y983"))

    provider = YahooFinanceProvider()
    d = date(2024, 12, 30)  # esempio
    print("\n=== PREZZO STORICO IE00B4L5Y983 ===")
    print(get_price_summary("IE00B4L5Y983", d, provider))
