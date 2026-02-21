import yfinance as yf
import pandas as pd
import numpy as np


# =========================
# MENÚS
# =========================

def pedir(texto, default):
    valor = input(f"{texto} [{default}]: ").strip()
    return valor if valor else default


def menu_intervalo():
    print("\nSelecciona el intervalo:")
    print("1) 1 minuto")
    print("2) 5 minutos")
    print("3) 15 minutos")
    print("4) 30 minutos")
    print("5) 1 hora")
    print("6) 1 día")

    opcion = input("Opción [1-6] (Enter=5m): ").strip()

    if opcion == "1":
        return "1m"
    elif opcion == "2" or opcion == "":
        return "5m"   # defecto
    elif opcion == "3":
        return "15m"
    elif opcion == "4":
        return "30m"
    elif opcion == "5":
        return "1h"
    elif opcion == "6":
        return "1d"
    else:
        print("Opción no válida. Se usará 5m.")
        return "5m"


# =========================
# DESCARGA Y ANÁLISIS
# =========================

def descargar_datos(ticker: str, period: str, interval: str) -> pd.DataFrame:
    data = yf.download(ticker, period=period, interval=interval, progress=False)

    if data is None or data.empty:
        raise ValueError(
            f"No se obtuvieron datos para {ticker} con period={period} e interval={interval}.\n"
            f"Prueba con un periodo más largo o un intervalo diferente."
        )

    if "Close" not in data.columns:
        raise ValueError(
            f"La data descargada no contiene columna 'Close'. Columnas: {list(data.columns)}"
        )

    return data


def analizar_impulso(df: pd.DataFrame) -> dict:
    df = df.sort_index().copy()

    # 1) Calcular retorno
    df["ret"] = df["Close"].pct_change()

    # 2) Eliminar filas con NaN (primera vela, huecos, etc.)
    df = df.dropna()

    if df.empty:
        raise ValueError("No hay suficientes datos (menos de 2 velas válidas) para calcular retornos.")

    # 3) Clasificar el signo del retorno
    umbral_plano = 0.0001  # 0.01 %
    df["signo"] = np.select(
        [df["ret"] > umbral_plano, df["ret"] < -umbral_plano],
        [1, -1],
        default=0
    )

    total = len(df)
    alc = (df["signo"] == 1).sum()
    baj = (df["signo"] == -1).sum()
    pla = (df["signo"] == 0).sum()

    intensidad_up = df.loc[df["signo"] == 1, "ret"].mean() * 100
    intensidad_down = df.loc[df["signo"] == -1, "ret"].mean() * 100
    intensidad_down_abs = df.loc[df["signo"] == -1, "ret"].abs().mean() * 100

    # 4) Calcular rachas
    signos = df["signo"].values
    r_up, r_down = [], []

    if len(signos) > 0:
        temp_len = 1
        temp_sign = signos[0]

        for s in signos[1:]:
            if s == temp_sign and s != 0:
                temp_len += 1
            else:
                if temp_sign == 1:
                    r_up.append(temp_len)
                elif temp_sign == -1:
                    r_down.append(temp_len)
                temp_len = 1
                temp_sign = s

        # cerrar última racha
        if temp_sign == 1:
            r_up.append(temp_len)
        elif temp_sign == -1:
            r_down.append(temp_len)

    def stats(lista):
        if not lista:
            return (0, 0, 0)
        arr = np.array(lista)
        return arr.mean(), arr.max(), arr.sum()

    avg_up, max_up, total_up = stats(r_up)
    avg_down, max_down, total_down = stats(r_down)

    return {
        "velas": total,
        "pct_alc": alc / total * 100,
        "pct_baj": baj / total * 100,
        "pct_plan": pla / total * 100,
        "int_up": intensidad_up,
        "int_baj": intensidad_down,
        "int_baj_abs": intensidad_down_abs,
        "racha_up_avg": avg_up,
        "racha_up_max": max_up,
        "racha_down_avg": avg_down,
        "racha_down_max": max_down,
        "pct_tiempo_up": total_up / total * 100 if total > 0 else 0,
        "pct_tiempo_down": total_down / total * 100 if total > 0 else 0,
    }


def imprimir(ticker, period, interval, r):
    print(f"\n=== RESULTADOS PARA {ticker} ===")
    print(f"Periodo: {period} | Intervalo: {interval}")
    print(f"Velas analizadas: {r['velas']}")
    print()
    print(f"Alcistas: {r['pct_alc']:.2f}%")
    print(f"Bajistas: {r['pct_baj']:.2f}%")
    print(f"Planas:   {r['pct_plan']:.2f}%")
    print()
    print("Intensidad promedio por vela:")
    print(f"  UP:         {r['int_up']:.4f}%")
    print(f"  DOWN:       {r['int_baj']:.4f}%")
    print(f"  DOWN (abs): {r['int_baj_abs']:.4f}%")
    print()
    print("Rachas:")
    print(f"  UP media:   {r['racha_up_avg']:.2f} velas")
    print(f"  UP máxima:  {r['racha_up_max']}")
    print(f"  DOWN media: {r['racha_down_avg']:.2f} velas")
    print(f"  DOWN máx.:  {r['racha_down_max']}")
    print()
    print(f"% tiempo en impulsos alcistas: {r['pct_tiempo_up']:.2f}%")
    print(f"% tiempo en impulsos bajistas: {r['pct_tiempo_down']:.2f}%")
    print("\n==========================================\n")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("=== ANALIZADOR DE IMPULSO (SPY / CUALQUIER TICKER) ===")

    while True:
        ticker = pedir("Ticker (SPY, QQQ, NVDA, BTC-USD...)", "SPY").upper()
        period = pedir("Periodo (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)", "30d")
        interval = menu_intervalo()

        # recomendación mínima rápida:
        # si eliges 1m, evita periodos muy largos
        try:
            df = descargar_datos(ticker, period, interval)
            resultados = analizar_impulso(df)
            imprimir(ticker, period, interval, resultados)
        except Exception as e:
            print("\nERROR:", e, "\n")

        otra = input("¿Analizar otro? (s/n): ").strip().lower()
        if otra != "s":
            break
