from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import requests
import yfinance as yf
from dateutil import tz

# =========================
# Configuración
# =========================
TZ_LOCAL = tz.gettz("America/Bogota")   # Cambia si quieres: "America/Panama", "America/New_York", etc.
DEADBAND_PCT = 0.10                    # Zona muerta para ⏸️ (en %)
LOOKAHEAD_HOURS = 24                   # Ventana: ahora -> próximas N horas para eventos High Impact

# ForexFactory (fuente pública del calendario semanal en JSON)
FF_URL_JSON = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
CACHE_PATH = Path("ff_calendar_cache.json")
CACHE_TTL_MIN = 15                     # Cache local para evitar rate limit

COUNTRIES = {"USD"}                    # País/moneda objetivo en ForexFactory
IMPACT_LEVELS = {"High"}               # Solo alto impacto


# =========================
# Modelos / Helpers
# =========================
@dataclass
class Signal:
    label: str        # "⬆️" / "⬇️" / "⏸️"
    change_pct: float
    last: float
    prev: float


def arrow_from_change(change_pct: float, deadband_pct: float) -> str:
    if change_pct > deadband_pct:
        return "⬆️"
    if change_pct < -deadband_pct:
        return "⬇️"
    return "⏸️"


def get_yahoo_signal(ticker: str, deadband_pct: float) -> Signal:
    """
    Robusto:
    1) intenta history 1d (5d/1mo/3mo) para tener last/prev
    2) si falla, intenta fast_info (último precio) y previous_close
    """
    t = yf.Ticker(ticker)

    # Intentos de histórico (a veces 5d falla, pero 1mo/3mo funciona)
    for period in ("5d", "1mo", "3mo"):
        try:
            hist = t.history(period=period, interval="1d", auto_adjust=False)
            if hist is not None and not hist.empty and len(hist) >= 2:
                last = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                change_pct = ((last - prev) / prev) * 100.0
                label = arrow_from_change(change_pct, deadband_pct=deadband_pct)
                return Signal(label=label, change_pct=change_pct, last=last, prev=prev)
        except Exception:
            pass

    # Fallback: fast_info (cuando history viene vacío)
    try:
        fi = getattr(t, "fast_info", {}) or {}
        last = fi.get("last_price") or fi.get("lastPrice") or fi.get("regular_market_price")
        prev = fi.get("previous_close") or fi.get("previousClose")

        if last is not None and prev is not None and float(prev) != 0.0:
            last = float(last)
            prev = float(prev)
            change_pct = ((last - prev) / prev) * 100.0
            label = arrow_from_change(change_pct, deadband_pct=deadband_pct)
            return Signal(label=label, change_pct=change_pct, last=last, prev=prev)
    except Exception:
        pass

    raise RuntimeError(
        f"Sin datos suficientes para {ticker}. "
        f"Yahoo devolvió histórico vacío (posible rate limit/feriado/outage)."
    )


def safe_signal(
    primary: str,
    fallback: str | None,
    deadband_pct: float,
) -> tuple[Signal, str]:
    """
    Obtiene señal con fallback.
    Devuelve: (Signal, source_used)
    - Si primary falla -> intenta fallback
    - Si ambos fallan -> retorna señal neutra para no tumbar el script
    """
    try:
        return get_yahoo_signal(primary, deadband_pct), primary
    except Exception:
        if fallback:
            try:
                return get_yahoo_signal(fallback, deadband_pct), fallback
            except Exception:
                pass

    # Último recurso: neutro
    neutral = Signal(label="⏸️", change_pct=0.0, last=0.0, prev=0.0)
    return neutral, "N/A"


# =========================
# ForexFactory Calendar (auto)
# =========================
def _cache_is_fresh(path: Path, ttl_min: int) -> bool:
    if not path.exists():
        return False
    age = datetime.now(TZ_LOCAL) - datetime.fromtimestamp(path.stat().st_mtime, TZ_LOCAL)
    return age <= timedelta(minutes=ttl_min)


def fetch_ff_calendar_json() -> list[dict]:
    """
    Descarga el calendario semanal de ForexFactory (JSON) y usa cache local.
    """
    if _cache_is_fresh(CACHE_PATH, CACHE_TTL_MIN):
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    r = requests.get(FF_URL_JSON, timeout=20)
    r.raise_for_status()
    data = r.json()

    CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def _parse_ff_datetime(date_str: str, time_str: str) -> datetime | None:
    """
    ForexFactory suele dar:
      date: 'MM-DD-YYYY'
      time: '8:30am', 'All Day', 'Tentative'
    """
    if not date_str:
        return None

    # "All Day" / "Tentative" -> asignamos mediodía para comparaciones
    if not time_str or time_str.strip().lower() in {"all day", "tentative"}:
        try:
            d = datetime.strptime(date_str.strip(), "%m-%d-%Y")
            return d.replace(hour=12, minute=0, tzinfo=TZ_LOCAL)
        except Exception:
            return None

    t = time_str.strip().lower().replace(" ", "")
    m = re.match(r"^(\d{1,2}):(\d{2})(am|pm)$", t)
    if not m:
        return None

    hh = int(m.group(1))
    mm = int(m.group(2))
    ap = m.group(3)

    if ap == "pm" and hh != 12:
        hh += 12
    if ap == "am" and hh == 12:
        hh = 0

    try:
        d = datetime.strptime(date_str.strip(), "%m-%d-%Y")
        return datetime(d.year, d.month, d.day, hh, mm, tzinfo=TZ_LOCAL)
    except Exception:
        return None


def high_impact_news_ff(lookahead_hours: int = LOOKAHEAD_HOURS) -> tuple[bool, list[dict]]:
    """
    Detecta eventos USD + High dentro de la ventana:
      ahora -> próximas lookahead_hours horas

    Retorna:
      (hay_alto_impacto, eventos)
    """
    data = fetch_ff_calendar_json()

    now = datetime.now(TZ_LOCAL)
    end = now + timedelta(hours=lookahead_hours)

    relevant: list[dict] = []
    for ev in data if isinstance(data, list) else []:
        country = str(ev.get("country", "")).strip()
        impact = str(ev.get("impact", "")).strip()
        title = str(ev.get("title", "")).strip()
        date_s = str(ev.get("date", "")).strip()
        time_s = str(ev.get("time", "")).strip()

        if country not in COUNTRIES:
            continue
        if impact not in IMPACT_LEVELS:
            continue

        ev_dt = _parse_ff_datetime(date_s, time_s)
        if ev_dt is None:
            continue

        if now <= ev_dt <= end:
            relevant.append(
                {
                    "title": title,
                    "country": country,
                    "impact": impact,
                    "date": date_s,
                    "time": time_s,
                    "local_dt": ev_dt.isoformat(),
                }
            )

    return (len(relevant) > 0, relevant)


# =========================
# Modo Macro (Risk-On / Neutral / Risk-Off)
# =========================
def determine_macro_mode(es, vix, dxy, has_high):
    """
    Lógica macro anti-sabotaje (versión balanceada)
    """

    # 🚨 1. High impact news = Neutral
    if has_high:
        return "🟡 Neutral", "Evento macro cercano → SOLO setups A+."

    # 🚨 2. VIX en expansión clara
    if vix.change_pct >= 1.5:
        return "🟡 Neutral", "VIX en expansión → mercado inestable → SOLO A+."

    # 🚨 3. Daño estructural reciente (sell-off previo)
    if es.change_pct <= -1.8:
        return "🟡 Neutral", "Sell-off reciente → día de transición → SOLO A+."

    # ⚠️ 4. Señales mixtas
    if es.change_pct < 0 and dxy.change_pct <= 0:
        return "🟡 Neutral", "Índices débiles + dólar flojo → Neutral."

    # ✅ 5. Risk-On limpio
    if es.change_pct > 0 and vix.change_pct <= 0 and dxy.change_pct <= 0:
        return "🟢 Risk-On", "Flujos pro-riesgo alineados."

    # Default seguro
    return "🟡 Neutral", "Condiciones no claras → proteger capital."



# =========================
# Main
# =========================
def main():
    # Señales con fallback (para que NUNCA se caiga si Yahoo falla)
    es, es_src = safe_signal("ES=F", "SPY", DEADBAND_PCT)           # fallback: SPY
    vix, vix_src = safe_signal("^VIX", "VIXY", DEADBAND_PCT)        # fallback: VIXY
    dxy, dxy_src = safe_signal("DX-Y.NYB", "UUP", DEADBAND_PCT)     # fallback: UUP

    # Noticias alto impacto (auto) con protección
    try:
        has_high, events = high_impact_news_ff(LOOKAHEAD_HOURS)
    except Exception:
        has_high, events = False, []

    # Output base
    print("Checklist macro:")
    print(f"Futuros ES: {es.label}  ({es.change_pct:+.2f}%)  src={es_src}")
    print(f"VIX:        {vix.label} ({vix.change_pct:+.2f}%)  src={vix_src}")
    print(f"DXY:        {dxy.label} ({dxy.change_pct:+.2f}%)  src={dxy_src}")
    print(f"Noticias alto impacto confirmadas (sí/no): {'sí' if has_high else 'no'}")

    # Modo macro + disciplina
    macro_mode, discipline_rule = determine_macro_mode(es, vix, dxy, has_high)
    print("\nConclusión macro:")
    print(macro_mode)
    print(f"Regla anti-sabotaje: {discipline_rule}")

    # Listar eventos si existen
    if has_high:
        print(f"\nEventos relevantes (USD, High) en próximas {LOOKAHEAD_HOURS}h:")
        for e in events:
            print(f" - {e['date']} {e['time']} | {e['title']} ({e['country']} / {e['impact']})")


if __name__ == "__main__":
    main()
