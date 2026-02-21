import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

STORAGE_FILE = "diario_trading.csv"

st.set_page_config(
    page_title="Diario de Trading",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Diario de Trading – Hoy")

# -------------------------
# Barra lateral
# -------------------------
st.sidebar.header("Configuración del día")

fecha = st.sidebar.date_input("Fecha de la sesión", value=date.today())
session_id = st.sidebar.text_input("Nombre de sesión / etiqueta (opcional)", "")

st.sidebar.markdown("---")
st.sidebar.markdown("**Tips:**")
st.sidebar.markdown("- Llena el diario ANTES de operar.
- Respeta el plan que escribas aquí.
- Si no hay invalidación clara, NO hay trade.")

# -------------------------
# 1️⃣ Contexto del día
# -------------------------
st.header("1️⃣ Contexto del día (MACRO / NOTICIAS)")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📰 Noticias relevantes del día")
    noticia_1 = st.text_input("Noticia 1", "")
    noticia_2 = st.text_input("Noticia 2", "")
    noticia_3 = st.text_input("Noticia 3", "")

with col2:
    st.subheader("🎭 Tono del mercado")
    tono_mercado = st.radio(
        "¿El tono del mercado hoy es?",
        options=["Riesgo-ON (alcista)", "Riesgo-OFF (bajista)", "Neutro / indeciso"]
    )

    impacto_vol = st.radio(
        "Impacto esperado en volatilidad:",
        options=["Alta", "Media", "Baja"]
    )

# -------------------------
# 2️⃣ Plan de Trading del Día
# -------------------------
st.header("2️⃣ Plan de Trading del Día (Niveles + Invalidación clara)")

st.caption("📌 Regla: si no puedes escribir **exactamente** dónde quedas equivocado (invalidación), no es trade.")

tab_spy, tab_slv, tab_btc = st.tabs(["SPY", "SLV", "BTC"])

with tab_spy:
    st.subheader("SPY — Niveles + invalidación (ejemplos)")
    col_spy1, col_spy2 = st.columns(2)

    with col_spy1:
        spy_calls_nivel = st.text_input("Calls solo si rompe / sostiene arriba de:", placeholder="Ej: Reclaim y hold arriba de VWAP / 0DTE: nivel X.XX", key="spy_calls_nivel")
        spy_puts_nivel = st.text_input("Puts solo si pierde:", placeholder="Ej: Pierde low premarket o low del día X.XX", key="spy_puts_nivel")
        spy_zona_ruido = st.text_input("Zona donde NO operar (ruido):", placeholder="Ej: Entre VWAP y rango premarket", key="spy_zona_ruido")

    with col_spy2:
        spy_premarket = st.text_input("Tendencia premarket:", placeholder="Ej: Alcista / bajista / rango", key="spy_premarket")
        spy_contexto = st.text_area("Contexto técnico (rápido):", placeholder="Ej: Por encima de VWAP + estructura HH/HL en 5m", key="spy_contexto")

    st.markdown("**Invalidación (obligatorio)**")
    col_spy_inv1, col_spy_inv2 = st.columns(2)
    with col_spy_inv1:
        spy_calls_inval = st.text_input(
            "Invalidación Calls (SPY):",
            placeholder="Ej: Si vuelve y cierra 5m debajo de VWAP / pierde low de la vela de ruptura",
            key="spy_calls_inval"
        )
    with col_spy_inv2:
        spy_puts_inval = st.text_input(
            "Invalidación Puts (SPY):",
            placeholder="Ej: Si recupera VWAP y cierra 5m arriba / rompe high del pullback",
            key="spy_puts_inval"
        )

    st.expander("📎 Ejemplos concretos (SPY) — guías rápidas", expanded=False).markdown(
        """- **Calls (ejemplo intradía estructurado):** Entrada solo si SPY **reclama VWAP** y **cierra 5m arriba** + rompe high del rango (o high premarket).  
  - **Invalidación:** 1) Cierre 5m debajo de VWAP, o 2) pierde el **low** de la vela que rompió el rango.

- **Puts (ejemplo):** Entrada solo si SPY **pierde low premarket** (o low del día) con cierre 5m abajo + retesteo fallido.  
  - **Invalidación:** Reclaim de VWAP con cierre 5m arriba, o rompe el **high** del retesteo fallido."""
    )

with tab_slv:
    st.subheader("SLV — Niveles + invalidación (ejemplos)")
    col_slv1, col_slv2 = st.columns(2)

    with col_slv1:
        slv_calls_nivel = st.text_input("Calls si mantiene arriba de:", placeholder="Ej: Arriba de VWAP + reclaim de X.XX", key="slv_calls_nivel")
        slv_puts_nivel = st.text_input("Puts si pierde (SLV):", placeholder="Ej: Pierde soporte X.XX / low del rango", key="slv_puts_nivel")
        slv_objetivo = st.text_input("Objetivo (SLV):", placeholder="Ej: High del día anterior / resistencia X.XX", key="slv_objetivo")

    with col_slv2:
        slv_stop = st.text_input("Stop (SLV):", placeholder="Ej: Debajo de VWAP / debajo de low de retesteo", key="slv_stop")
        slv_nota = st.text_area(
            "Razón por la que SLV tiene mejor setup hoy:",
            "",
            key="slv_nota"
        )

    st.markdown("**Invalidación (obligatorio)**")
    col_slv_inv1, col_slv_inv2 = st.columns(2)
    with col_slv_inv1:
        slv_calls_inval = st.text_input(
            "Invalidación Calls (SLV):",
            placeholder="Ej: Cierre 5m debajo de VWAP o pierde low del pullback",
            key="slv_calls_inval"
        )
    with col_slv_inv2:
        slv_puts_inval = st.text_input(
            "Invalidación Puts (SLV):",
            placeholder="Ej: Recupera VWAP y cierra 5m arriba / rompe high del retesteo",
            key="slv_puts_inval"
        )

    st.expander("📎 Ejemplos concretos (SLV) — guías rápidas", expanded=False).markdown(
        """- **Calls (ejemplo):** SLV en tendencia → esperar **pullback a VWAP** y entrada en rebote con confirmación (cierre 5m arriba + volumen).  
  - **Invalidación:** Cierre 5m debajo de VWAP o pierde el low del pullback.

- **Puts (ejemplo):** SLV pierde soporte (low premarket / low del día) y retestea sin poder recuperar.  
  - **Invalidación:** Recupera el soporte (cierre 5m arriba) o reclaim de VWAP."""
    )

with tab_btc:
    st.subheader("BTC — Niveles + invalidación (ejemplos)")
    col_btc1, col_btc2 = st.columns(2)

    with col_btc1:
        btc_largos_nivel = st.text_input("Longs (BTC) solo si rompe / sostiene arriba de:", placeholder="Ej: Nivel clave + cierre 15m arriba", key="btc_largos_nivel")
        btc_cortos_nivel = st.text_input("Shorts (BTC) solo si pierde:", placeholder="Ej: Pierde soporte + cierre 15m abajo", key="btc_cortos_nivel")
        btc_zona_ruido = st.text_input("Zona donde NO operar (BTC):", placeholder="Ej: Rango medio entre soporte y resistencia", key="btc_zona_ruido")

    with col_btc2:
        btc_contexto = st.text_area("Contexto técnico (BTC):", placeholder="Ej: Estructura en 1H, tendencia, liquidez, rango", key="btc_contexto")
        btc_timeframe = st.selectbox("Timeframe principal para decisión:", options=["5m", "15m", "1H", "4H"], index=1)

    st.markdown("**Invalidación (obligatorio)**")
    col_btc_inv1, col_btc_inv2 = st.columns(2)
    with col_btc_inv1:
        btc_largos_inval = st.text_input(
            "Invalidación Long (BTC):",
            placeholder="Ej: Cierre 15m de vuelta debajo del nivel / pierde low del retesteo",
            key="btc_largos_inval"
        )
    with col_btc_inv2:
        btc_cortos_inval = st.text_input(
            "Invalidación Short (BTC):",
            placeholder="Ej: Reclaim del nivel con cierre 15m arriba / rompe high del retesteo",
            key="btc_cortos_inval"
        )

    st.expander("📎 Ejemplos concretos (BTC) — guías rápidas", expanded=False).markdown(
        """- **Long (ejemplo):** BTC rompe resistencia de rango y **cierra 15m arriba**, luego retestea y sostiene.  
  - **Invalidación:** Cierre 15m de vuelta **debajo** del nivel o pierde el low del retesteo.

- **Short (ejemplo):** BTC pierde soporte y **cierra 15m abajo**, retestea y falla en recuperar.  
  - **Invalidación:** Reclaim del soporte con cierre 15m arriba o rompe el high del retesteo."""
    )

# -------------------------
# 3️⃣ Gestión del Riesgo
# -------------------------
st.header("3️⃣ Gestión del Riesgo (muy importante)")

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    capital_total = st.number_input(
        "Capital total de la cuenta ($)",
        min_value=0.0, step=100.0, format="%.2f"
    )
with col_r2:
    max_riesgo_trade = st.number_input(
        "Máximo riesgo por trade ($)",
        min_value=0.0, step=10.0, format="%.2f"
    )
with col_r3:
    max_monto_trade = st.number_input(
        "Monto máximo permitido por trade hoy ($)",
        min_value=0.0, step=10.0, format="%.2f"
    )

st.caption("💡 Puedes usar 2–5% del capital como referencia para el riesgo por trade.")

regla_oro_opciones = [
    "NO sobreoperar",
    "Tomar ganancias en 20–30%",
    "Cortar pérdida sin dudar",
    "Solo operar si se cumple el plan",
    "No muevo el stop (contrato)",
    "Si me siento molesto, no opero"
]

regla_oro = st.multiselect(
    "Regla de oro del día (elige 2–3 preferiblemente):",
    options=regla_oro_opciones
)

# -------------------------
# 4️⃣ Emociones al iniciar el día
# -------------------------
st.header("4️⃣ Mis Emociones al iniciar el día")

emociones_opciones = [
    "Tranquilo",
    "Ansioso",
    "Emocionado",
    "Impaciente",
    "Cansado",
    "Enfocado",
    "Molesto",
    "Con urgencia por recuperar"
]

emociones = st.multiselect(
    "Marca cómo te sientes antes de operar:",
    options=emociones_opciones
)

comentario_emocional = st.text_area(
    "Comentario / reflexión:",
    placeholder="Ej: Dormí bien, me siento tranquilo pero atento a no sobreoperar..."
)

# -------------------------
# 5️⃣ Reglas mentales (tu perfil) + Checklist pre-trade
# -------------------------
st.header("5️⃣ Reglas mentales + Checklist pre-trade (tu ventaja)")

with st.expander("📌 Mis reglas NO negociables (leer antes de operar)", expanded=True):
    st.markdown(
        """**Marco mental**
- El mercado **no premia justicia**, premia probabilidades.
- No necesito entender el movimiento, solo **gestionarlo**.
- El stop es **costo operativo**, no castigo.

**Reglas**
1) **Prohibido “recuperar”**: trade malo → se registra, se cierra, se enfría.  
2) **El stop es un contrato**: no se mueve por emoción.  
3) **Si hay enojo/urgencia/demostrar** → no opero (ideal 0 trades emocionales).

**Frase ancla (di en voz baja):**  
> “Este trade es una apuesta probabilística, no un juicio moral.”"""
    )

st.subheader("✅ Checklist rápido (si alguna es NO → no hay trade)")

c1, c2, c3, c4 = st.columns(4)
with c1:
    chk_inval = st.checkbox("Tengo invalidación clara", value=False)
with c2:
    chk_acepto = st.checkbox("Acepto la pérdida antes de entrar", value=False)
with c3:
    chk_no_rec = st.checkbox("No estoy buscando recuperar", value=False)
with c4:
    chk_calma = st.checkbox("Estoy calmado (sin urgencia)", value=False)

estado_trade = "✅ OK para operar (si se cumple el setup)" if all([chk_inval, chk_acepto, chk_no_rec, chk_calma]) else "⛔ Hoy NO se opera hasta corregir checklist"
st.info(f"Estado: {estado_trade}")

gatillos = st.multiselect(
    "Detonantes a vigilar hoy (si aparecen → pausa 10–20 min + reevaluar):",
    options=[
        "Mecha absurda me sacó",
        "Stop por milímetros",
        "Movimiento “sin sentido”",
        "Spread/comisión me irrita",
        "Quiero demostrar / tener razón",
        "Siento injusticia"
    ]
)

plan_enfriamiento = st.text_area(
    "Plan de enfriamiento (si aparece un detonante):",
    placeholder="Ej: Cierro plataforma 15 min, respiro 4-7-8, reviso checklist, si sigo molesto: no opero."
)

# -------------------------
# BOTÓN: Guardar registro
# -------------------------
st.markdown("---")

if st.button("💾 Guardar diario de hoy"):
    registro = {
        "fecha": fecha.isoformat(),
        "session_id": session_id,
        "timestamp_guardado": datetime.now().isoformat(),

        # Noticias
        "noticia_1": noticia_1,
        "noticia_2": noticia_2,
        "noticia_3": noticia_3,
        "tono_mercado": tono_mercado,
        "impacto_volatilidad": impacto_vol,

        # SPY
        "spy_calls_nivel": spy_calls_nivel,
        "spy_puts_nivel": spy_puts_nivel,
        "spy_premarket": spy_premarket,
        "spy_zona_ruido": spy_zona_ruido,
        "spy_contexto": spy_contexto,
        "spy_calls_inval": spy_calls_inval,
        "spy_puts_inval": spy_puts_inval,

        # SLV
        "slv_calls_nivel": slv_calls_nivel,
        "slv_objetivo": slv_objetivo,
        "slv_stop": slv_stop,
        "slv_puts_nivel": slv_puts_nivel,
        "slv_nota": slv_nota,
        "slv_calls_inval": slv_calls_inval,
        "slv_puts_inval": slv_puts_inval,

        # BTC
        "btc_largos_nivel": btc_largos_nivel,
        "btc_cortos_nivel": btc_cortos_nivel,
        "btc_zona_ruido": btc_zona_ruido,
        "btc_contexto": btc_contexto,
        "btc_timeframe": btc_timeframe,
        "btc_largos_inval": btc_largos_inval,
        "btc_cortos_inval": btc_cortos_inval,

        # Riesgo
        "capital_total": capital_total,
        "max_riesgo_trade": max_riesgo_trade,
        "max_monto_trade": max_monto_trade,
        "regla_oro": ", ".join(regla_oro),

        # Emociones
        "emociones": ", ".join(emociones),
        "comentario_emocional": comentario_emocional,

        # Checklist mental
        "check_inval_clara": chk_inval,
        "check_acepto_perdida": chk_acepto,
        "check_no_recuperar": chk_no_rec,
        "check_calmado": chk_calma,
        "estado_trade": estado_trade,
        "gatillos": ", ".join(gatillos),
        "plan_enfriamiento": plan_enfriamiento,
    }

    # Guardar en CSV
    if os.path.exists(STORAGE_FILE):
        df_old = pd.read_csv(STORAGE_FILE)
        df_new = pd.concat([df_old, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_new = pd.DataFrame([registro])

    df_new.to_csv(STORAGE_FILE, index=False, encoding="utf-8-sig")
    st.success("✅ Diario guardado correctamente en 'diario_trading.csv'.")

    st.dataframe(df_new.tail(5))

# -------------------------
# Sección opcional: Historial
# -------------------------
st.markdown("## 📊 Historial reciente")

if os.path.exists(STORAGE_FILE):
    df_hist = pd.read_csv(STORAGE_FILE)
    df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
    df_hist = df_hist.sort_values(by="fecha", ascending=False)

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        fecha_min = st.date_input("Desde fecha:", value=df_hist["fecha"].min().date())
    with col_h2:
        fecha_max = st.date_input("Hasta fecha:", value=df_hist["fecha"].max().date())

    mask = (df_hist["fecha"].dt.date >= fecha_min) & (df_hist["fecha"].dt.date <= fecha_max)
    df_filtrado = df_hist[mask]

    st.write(f"Registros entre {fecha_min} y {fecha_max}: {len(df_filtrado)}")
    st.dataframe(df_filtrado)
else:
    st.info("Aún no hay registros guardados. Guarda tu primer diario para ver el historial aquí.")
