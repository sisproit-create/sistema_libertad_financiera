import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="📊 Plan Diario de Trading", layout="centered")

# ===============================
# Config
# ===============================
CSV_FILE = "diario_trading.csv"

COLUMNS = [
    "fecha",
    "activo",
    "tipo_trade",
    "direccion",
    "contexto_intradia",
    "entrada",
    "stop",
    "target",
    "invalidacion",
    "regla_tiempo",
    "timeframe",
    "estado_emocional",
    "checklist_ok",
    "checklist_intradia_ok",
]

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

# ===============================
# Sidebar - Reglas Mentales
# ===============================
st.sidebar.markdown("""
## 🧠 Reglas de Oro

- El mercado no premia justicia, premia probabilidades.
- El stop es un **costo operativo**, no un castigo.
- **Nunca “recuperes”** desde emoción.
- Si no sé exactamente dónde estoy equivocado (invalidación), **no entro**.

> *“Este trade es una apuesta probabilística, no un juicio moral.”*
""")

st.sidebar.markdown("---")
st.sidebar.markdown("📘 **Llena el diario ANTES de operar.**")
st.sidebar.markdown("🧩 **Regla intraday:** *Si necesita dormir para funcionar, no es intraday.*")

# ===============================
# UI principal
# ===============================
st.title("📊 Dashboard – Plan Diario de Trading (Anti-sabotaje emocional)")

activo = st.selectbox("📈 Activo", ["SPY", "SLV", "BTC"])
tipo_trade = st.selectbox("🧩 Tipo de Trade", ["Intraday (solo sesión actual)", "Swing"])
direccion = st.selectbox("➡️ Dirección", ["Call / Long", "Put / Short"])

# Timeframe típico por activo
if "Intraday" in tipo_trade:
    timeframe_choices = ["1m", "5m", "15m", "30m"]
    default_tf = "5m"
else:  # Swing
    timeframe_choices = ["1h", "4h", "1D"]
    default_tf = "1D"

timeframe = st.selectbox(
    "⏱ Timeframe de decisión (para invalidación)",
    timeframe_choices,
    index=timeframe_choices.index(default_tf)
)

# ===============================
# CONTEXTO INTRADÍA (solo si Intraday)
# ===============================
contexto_intradia = ""
st.markdown("---")
st.subheader("🔧 Contexto")

if "Intraday" in tipo_trade:
    st.info("Trade válido **solo durante la sesión actual**, basado en estructura del día (VWAP / High-Low del día).")
    contexto_intradia = st.text_area(
        "🧭 Contexto intradía (obligatorio)",
        placeholder="Ej: Por debajo de VWAP, tendencia bajista del día. Busco put en retesteo VWAP hacia low del día."
    )
else:
    st.caption("Swing: define contexto en marco mayor (niveles, tendencia, invalidación de swing).")
    contexto_intradia = st.text_area(
        "🧭 Contexto (opcional pero recomendado)",
        placeholder="Ej: Swing en soporte semanal; invalidación debajo del nivel X en cierre diario."
    )

# ===============================
# Entrada/Stop/Target
# ===============================
st.markdown("---")
st.subheader("🎯 Plan del trade")

col1, col2, col3 = st.columns(3)
with col1:
    entrada = st.number_input("🎯 Entrada", step=0.01)
with col2:
    stop = st.number_input("🛑 Stop (precio)", step=0.01)
with col3:
    target = st.number_input("💰 Target", step=0.01)

# ===============================
# Ejemplos de INVALIDACIÓN (intraday real)
# ===============================
st.markdown("### ❌ Invalidación (intraday real) – ejemplos por activo")

if activo == "SLV":
    if direccion == "Call / Long":
        st.success(
            "✅ **SLV Long intraday – invalidación correcta**\n\n"
            "- Pierde el **low del día** y **no lo recupera en 2 velas de 5m**, **o**\n"
            "- Cierra 5m **debajo de VWAP** con **volumen** (confirmación)."
        )
    else:
        st.success(
            "✅ **SLV Put/Short intraday – invalidación correcta**\n\n"
            "- Reclaim de **VWAP** con **cierre 5m arriba** + volumen (te saca), **o**\n"
            "- Rompe el **high del retesteo** y se mantiene 2 velas."
        )
elif activo == "SPY":
    if direccion == "Call / Long":
        st.success(
            "✅ **SPY Call/Long intraday – invalidación**\n\n"
            "- Cierre 5m **debajo de VWAP** tras entrada, **o**\n"
            "- Pierde el **low** de ruptura/retest y no lo recupera en 2 velas."
        )
    else:
        st.success(
            "✅ **SPY Put/Short intraday – invalidación**\n\n"
            "- Reclaim de **VWAP** con cierre 5m arriba, **o**\n"
            "- Rompe el **high** del retesteo y no vuelve a bajar en 2 velas."
        )
else:  # BTC
    if direccion == "Call / Long":
        st.success(
            "✅ **BTC Long intraday – invalidación**\n\n"
            "- Cierre 15m **debajo del nivel clave** (y no lo recupera), **o**\n"
            "- Pierde el low del retesteo y falla el rebote en 2 velas."
        )
    else:
        st.success(
            "✅ **BTC Short intraday – invalidación**\n\n"
            "- Reclaim del nivel clave con cierre 15m arriba, **o**\n"
            "- Rompe el high del retesteo y sostiene 2 velas."
        )

invalidacion = st.text_area(
    "❌ Invalidación del trade (OBLIGATORIO)",
    placeholder="Escribe la condición exacta que MATA la idea (hoy, si es intraday)."
)
invalidacion_ok = len(invalidacion.strip()) > 15

# ===============================
# Regla de TIEMPO (intraday)
# ===============================
regla_tiempo = ""
regla_tiempo_ok = True

if "Intraday" in tipo_trade:
    st.markdown("### ⏱ Regla de tiempo (obligatoria para intraday)")
    regla_sel = st.selectbox(
        "Elige una regla de tiempo",
        [
            "Si en 30–45 min no avanza hacia el target → cierro",
            "Si el impulso no aparece en 3–4 velas → salgo",
            "Otra (escríbela)"
        ]
    )
    if regla_sel == "Otra (escríbela)":
        regla_tiempo = st.text_input("Escribe tu regla de tiempo", placeholder="Ej: Si en 20 min no rompe el nivel → cierro.")
    else:
        regla_tiempo = regla_sel

    regla_tiempo_ok = len(regla_tiempo.strip()) > 10
    st.caption("👉 Esto separa intraday de swing. Intraday muere hoy: si el tiempo no juega a favor, se cierra.")

# ===============================
# Checklist emocional (core)
# ===============================
st.markdown("---")
st.subheader("🧠 Checklist emocional (obligatorio)")

c1 = st.checkbox("Tengo invalidación clara y objetiva")
c2 = st.checkbox("Acepto la pérdida ANTES de entrar (stop = costo operativo)")
c3 = st.checkbox("No estoy molesto ni buscando recuperar")
c4 = st.checkbox("Este trade sigue mi sistema, no mi emoción")

checklist_ok = all([c1, c2, c3, c4])

# ===============================
# Checklist intraday (extra)
# ===============================
checklist_intradia_ok = True
if "Intraday" in tipo_trade:
    st.subheader("⚡ Checklist intraday (ajustado)")
    i1 = st.checkbox("Este trade muere hoy sí o sí (no depende de mañana)")
    i2 = st.checkbox("Mi stop depende de la estructura del DÍA (VWAP / High-Low), no de esperanza")
    i3 = st.checkbox("Acepto salir plano si el tiempo no juega a favor")
    i4 = st.checkbox("Estoy tranquilo; no necesito que 'funcione'")

    checklist_intradia_ok = all([i1, i2, i3, i4])

    if not checklist_intradia_ok:
        st.warning("⚠️ Si alguna es NO → no es intraday → no operas.")

# ===============================
# Estado emocional (hard gate)
# ===============================
st.markdown("---")
st.subheader("🚦 Estado emocional")

estado = st.radio(
    "¿Cómo estás ahora mismo?",
    ["🟢 Calmo y enfocado", "🟡 Tenso / dudando", "🔴 Molesto / ansioso"]
)

estado_ok = estado == "🟢 Calmo y enfocado"

if estado == "🔴 Molesto / ansioso":
    st.error("🚫 NO OPERAR. Esto es autoprotección.")
elif estado == "🟡 Tenso / dudando":
    st.warning("⚠️ Si estás 🟡, solo operar setups A+ (si no es A+, no se guarda).")
else:
    st.success("✅ Estado mental adecuado")

# GATE adicional para 🟡 (solo permite si marcas A+)
a_plus_ok = True
if estado == "🟡 Tenso / dudando":
    a_plus_ok = st.checkbox("Confirmo que este es un setup A+ (si no, no opero)")

# ===============================
# Validaciones finales para guardar
# ===============================
contexto_ok = True
if "Intraday" in tipo_trade:
    contexto_ok = len(contexto_intradia.strip()) > 15

puede_guardar = all([
    invalidacion_ok,
    checklist_ok,
    checklist_intradia_ok,
    estado_ok,
    a_plus_ok,
    regla_tiempo_ok,
    contexto_ok
])

st.markdown("---")

def guardar_trade():
    df = pd.read_csv(CSV_FILE)

    nuevo = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "activo": activo,
        "tipo_trade": tipo_trade,
        "direccion": direccion,
        "contexto_intradia": contexto_intradia,
        "entrada": entrada,
        "stop": stop,
        "target": target,
        "invalidacion": invalidacion,
        "regla_tiempo": regla_tiempo,
        "timeframe": timeframe,
        "estado_emocional": estado,
        "checklist_ok": checklist_ok,
        "checklist_intradia_ok": checklist_intradia_ok,
    }

    # Asegura columnas (por si el CSV viejo no las tiene)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

if not puede_guardar:
    st.button("🚫 Guardar Trade (bloqueado)", disabled=True)

    missing = []
    if "Intraday" in tipo_trade and not contexto_ok:
        missing.append("Contexto intradía (obligatorio)")
    if not invalidacion_ok:
        missing.append("Invalidación clara (mínimo 15 caracteres)")
    if "Intraday" in tipo_trade and not regla_tiempo_ok:
        missing.append("Regla de tiempo (intraday)")
    if not checklist_ok:
        missing.append("Checklist emocional completo")
    if "Intraday" in tipo_trade and not checklist_intradia_ok:
        missing.append("Checklist intraday completo")
    if not estado_ok:
        missing.append("Estado emocional 🟢")
    if estado == "🟡 Tenso / dudando" and not a_plus_ok:
        missing.append("Confirmación de setup A+ (por estar 🟡)")

    if missing:
        st.info("Para habilitar Guardar, completa: " + " | ".join(missing))
else:
    if st.button("💾 Guardar Trade"):
        guardar_trade()
        st.success("✅ Trade guardado con disciplina")

# ===============================
# Tabla de últimos registros
# ===============================
st.markdown("## 📑 Últimos Trades Registrados")
df_show = pd.read_csv(CSV_FILE)
st.dataframe(df_show.tail(20), use_container_width=True)

# ===============================
# Templates rápidos intraday SLV Call/Put
# ===============================
with st.expander("📌 Templates rápidos (intraday real)"):
    st.markdown("""
**SLV – Long intraday (ejemplo)**
- Tipo: Intraday (solo sesión actual)
- Entrada: retest VWAP / nivel intradía
- Stop técnico: pérdida low intradía + confirmación (cierre 5m)
- Target: high del día / resistencia intradía
- Invalidación: pierde low del día y no lo recupera en 2 velas 5m, o cierra 5m debajo de VWAP con volumen
- Regla de tiempo: si en 30–45 min no hay avance claro → cerrar

**SLV – Put/Short intraday (ejemplo)**
- Tipo: Intraday (solo sesión actual)
- Entrada: rechazo en VWAP / retest de resistencia intradía
- Stop técnico: reclaim VWAP con cierre 5m arriba + volumen, o rompe high del retesteo y sostiene 2 velas
- Target: low del día / soporte intradía
- Invalidación: reclaim VWAP con cierre 5m arriba + volumen (te saca)
- Regla de tiempo: si el impulso no aparece en 3–4 velas → salir

**Regla final**
> Si necesita dormir para funcionar, no es intraday.
    """)

