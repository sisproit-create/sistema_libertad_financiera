# pip install yfinance pandas requests python-dateutil

from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from dateutil import tz
import requests
import yfinance as yf

BOGOTA = tz.gettz("America/Bogota")

@dataclass
class Signal:
    label: str   # "⬆️" / "⬇️" / "⏸️"
    change_pct: float
    last: float
    prev: float

def arrow_from_change(change_pct: float, deadband_pct: float = 0.05) -> str:
    """
    deadband_pct: umbral en % para considerar "⏸️"
    ejemplo 0.05 = 0.05% (muy sensible)
    """
    if change_pct > deadband_pct:
        return "⬆️"
    if change_pct < -deadband_pct:
        return "⬇️"
    return "⏸️"

def get_yahoo_signal(ticker: str, deadband_pct: float) -> Signal:
    t = yf.Ticker(ticker)
    # 2 últimos cierres/últimos puntos (interval=1d) para señal rápida
    hist = t.history(period="5d", interval="1d")
    if hist is None or hist.empty or len(hist) < 2:
        raise RuntimeError(f"Sin datos suficientes para {ticker}")

    last = float(hist["Close"].iloc[-1])
    prev = float(hist["Close"].iloc[-2])

    change_pct = ((last - prev) / prev) * 100.0
    label = arrow_from_change(change_pct, deadband_pct=deadband_pct)
    return Signal(label=label, change_pct=change_pct, last=last, prev=prev)

def high_impact_news_today_tradingeconomics(country: str = "United States") -> bool:
    """
    Requiere TradingEconomics API key.
    Guarda tu key en variable de entorno: TRADING_ECONOMICS_KEY
    """
    key = os.getenv("TRADING_ECONOMICS_KEY", "").strip()
    if not key:
        # Si no hay key, no adivinamos: devolvemos False pero avisamos en consola.
        print("⚠️ Falta TRADING_ECONOMICS_KEY. No se puede confirmar noticias alto impacto por API.")
        return False

    # Fecha de hoy en Bogotá (para tu operativa)
    today = datetime.now(BOGOTA).date().isoformat()

    # Endpoint oficial (calendar)
    # Docs: https://tradingeconomics.com/api/calendar.aspx  (ver en navegador)
    url = f"https://api.tradingeconomics.com/calendar/country/{country}/{today}"
    params = {"c": key}

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    # Heurística: marcar alto impacto si Importance es "High" o si el evento es clave
    # (Dependiendo del payload, los campos pueden variar: "Importance", "Event", etc.)
    high_keywords = {"FOMC", "Fed", "CPI", "PCE", "NFP", "Nonfarm", "Powell", "Rate", "Interest Rate", "GDP"}
    for ev in data if isinstance(data, list) else []:
        imp = str(ev.get("Importance", "")).lower()
        event_name = str(ev.get("Event", "")).strip()

        if "high" in imp:
            return True
        if any(k.lower() in event_name.lower() for k in high_keywords):
            return True

    return False

def main():
    # Ajusta sensibilidad (0.05% = muy sensible; 0.15% más estable)
    deadband = 0.10

    es = get_yahoo_signal("ES=F", deadband_pct=deadband)       # futuros ES :contentReference[oaicite:5]{index=5}
    vix = get_yahoo_signal("^VIX", deadband_pct=deadband)      # VIX (Yahoo)
    dxy = get_yahoo_signal("DX-Y.NYB", deadband_pct=deadband)  # DXY :contentReference[oaicite:6]{index=6}

    high_news = high_impact_news_today_tradingeconomics(country="United States")

    print("Checklist macro:")
    print(f"Futuros ES: {es.label}  ({es.change_pct:+.2f}%)  last={es.last:.2f} prev={es.prev:.2f}")
    print(f"VIX:        {vix.label} ({vix.change_pct:+.2f}%)  last={vix.last:.2f} prev={vix.prev:.2f}")
    print(f"DXY:        {dxy.label} ({dxy.change_pct:+.2f}%)  last={dxy.last:.2f} prev={dxy.prev:.2f}")
    print(f"Noticias alto impacto confirmadas (sí/no): {'sí' if high_news else 'no'}")

if __name__ == "__main__":
    main()
