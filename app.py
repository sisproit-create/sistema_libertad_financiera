import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ===============================
# Import Macro Checklist (Auto)
# ===============================
try:
    import checklist_macro_auto as macro
except Exception as e:
    macro = None
    import_error = e

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

    # ✅ Macro snapshot
    "macro_mode",
    "macro_rule",
    "macro_es",
    "macro_vix",
    "macro_dxy",
    "macro_high_impact_news",
    "macro_es_src",
    "macro_vix_src",
    "macro_dxy_src",

    # ✅ Checklists
    "checklist_diario_ok",
    "checklist_sesion_ok",
    "checklist_ok",
    "checklist_intradia_ok",

    # ✅ Capital / Riesgo exacto (Opciones)
    "fondo_inversion",
    "limite_riesgo_diario",
    "limite_riesgo_trade",
    "contratos",
    "prima_entrada",
    "prima_stop",
    "costo_entrada_usd",
    "riesgo_usd",
    "acepto_perder_financiero",
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

# ===============================
# 0) Macro Checklist (Auto)
# ===============================
st.markdown("## 🌍 Macro Checklist (Auto)")

if macro is None:
    st.error(
        "No pude importar `checklist_macro_auto.py`.\n\n"
        "✅ Solución:\n"
        "- Asegúrate de que `checklist_macro_auto.py` esté en la misma carpeta que `app.py`\n"
        "- Revisa que no tenga errores\n"
    )
    st.code(str(import_error))
    st.stop()


@st.cache_data(ttl=300)  # cache 5 min
def get_macro_snapshot():
    """
    Snapshot macro robusto: nunca debe tumbar el dashboard.
    Si Yahoo falla con ES=F, usa fallback SPY.
    Si VIX o DXY fallan, usa fallbacks o valores neutros.
    """
    errors = []

    def safe_signal(primary: str, fallback: str | None = None, label_name: str = ""):
        nonlocal errors
        try:
            return macro.get_yahoo_signal(primary, macro.DEADBAND_PCT), primary
        except Exception as e:
            errors.append(f"{label_name or primary} falló con {primary}: {e}")
            if fallback:
                try:
                    return macro.get_yahoo_signal(fallback, macro.DEADBAND_PCT), fallback
                except Exception as e2:
                    errors.append(f"{label_name or primary} fallback falló con {fallback}: {e2}")

            # Último recurso: señal neutra (no tumba la app)
            neutral = macro.Signal(label="⏸️", change_pct=0.0, last=0.0, prev=0.0)
            return neutral, "N/A"

    # Señales con fallback
    es, es_src = safe_signal("ES=F", fallback="SPY", label_name="Futuros ES")
    vix, vix_src = safe_signal("^VIX", fallback="VIXY", label_name="VIX")
    dxy, dxy_src = safe_signal("DX-Y.NYB", fallback="UUP", label_name="DXY")

    # Noticias alto impacto (ForexFactory) con try/except
    try:
        has_high, events = macro.high_impact_news_ff(macro.LOOKAHEAD_HOURS)
    except Exception as e:
        has_high, events = False, []
        errors.append(f"Calendario (ForexFactory) falló: {e}")

    # Modo macro
    try:
        macro_mode, macro_rule = macro.determine_macro_mode(es, vix, dxy, has_high)
    except Exception as e:
        macro_mode, macro_rule = "🟡 Neutral", "Regla anti-sabotaje: SOLO setups A+."
        errors.append(f"determine_macro_mode falló: {e}")

    return {
        "es": es, "vix": vix, "dxy": dxy,
        "es_src": es_src, "vix_src": vix_src, "dxy_src": dxy_src,
        "has_high": has_high, "events": events,
        "macro_mode": macro_mode, "macro_rule": macro_rule,
        "lookahead_hours": macro.LOOKAHEAD_HOURS,
        "errors": errors,
    }


colA, colB = st.columns([1, 1])
with colA:
    if st.button("🔄 Actualizar Macro (forzar)"):
        st.cache_data.clear()

snap = get_macro_snapshot()

# Avisos técnicos
if snap.get("errors"):
    with st.expander("⚠️ Macro: avisos técnicos (Yahoo / calendario)"):
        for msg in snap["errors"]:
            st.write(f"- {msg}")

st.caption(f"Fuentes: ES={snap.get('es_src')} | VIX={snap.get('vix_src')} | DXY={snap.get('dxy_src')}")

# Guardamos en session_state para gates + guardado
st.session_state["macro_mode"] = snap["macro_mode"]
st.session_state["macro_rule"] = snap["macro_rule"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Futuros ES", snap["es"].label, f"{snap['es'].change_pct:+.2f}%")
m2.metric("VIX", snap["vix"].label, f"{snap['vix'].change_pct:+.2f}%")
m3.metric("DXY", snap["dxy"].label, f"{snap['dxy'].change_pct:+.2f}%")
m4.metric("High Impact", "sí" if snap["has_high"] else "no", f"próx {snap['lookahead_hours']}h")

st.info(f"**Conclusión macro:** {snap['macro_mode']}")
st.caption(f"**Regla anti-sabotaje (macro):** {snap['macro_rule']}")

if snap["has_high"]:
    with st.expander("📅 Ver eventos High Impact detectados"):
        for e in snap["events"]:
            st.write(f"- {e['date']} {e['time']} | {e['title']} ({e['country']} / {e['impact']})")

st.markdown("---")

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="📊 Sistema Operativo de Trading",
    layout="centered"
)

CSV_FILE = "diario_trading.csv"

COLUMNS = [
    "fecha", "activo", "direccion",
    "entrada", "stop", "target",
    "position_size", "riesgo_usd",
    "estado_emocional", "checklist_ok"
]

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

# ===============================
# HEADER
# ===============================
st.title("📊 Sistema Operativo de Trading")
st.caption("Ejecutar el proceso. El dinero es consecuencia.")

# ===============================
# BLOQUE FIJO – SISTEMA OPERATIVO
# ===============================
with st.expander("🧠 SISTEMA OPERATIVO (Mantra + Checklist Diario)", expanded=True):

    st.markdown("### 🧠 MANTRA OPERATIVO")
    st.success("**“Yo ejecuto mi proceso con disciplina absoluta; el resultado no depende de mí.”**")

    st.markdown("---")

    # Imagen del sistema (si existe)
    IMAGE_PATH = "sistema_libertad_financiera.png"
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, use_container_width=True)
    else:
        st.info("📌 (Imagen del sistema no encontrada, puedes añadirla luego)")

    st.markdown("---")

    st.markdown("### ✅ CHECKLIST DIARIO DE TRADING (5 pasos)")
    st.caption("Este checklist se revisa **ANTES** de abrir gráficos u órdenes.")

    st.markdown("**1️⃣ ESTADO MENTAL**")
    c1 = st.checkbox("Dormí bien")
    c2 = st.checkbox("No estoy molesto, apurado ni eufórico")
    c3 = st.checkbox("Puedo cerrar hoy en rojo sin cambiar el plan")

    estado_mental_ok = all([c1, c2, c3])
    if not estado_mental_ok:
        st.error("🚫 Si fallas aquí → NO OPERAS")

    st.markdown("**2️⃣ CONTEXTO DE MERCADO**")
    c4 = st.checkbox("Sé si el mercado está en tendencia o rango")
    c5 = st.checkbox("Identifiqué niveles clave (VWAP / High-Low)")
    c6 = st.checkbox("Revisé noticias importantes")

    st.markdown("**3️⃣ SETUP CLARO**")
    c7 = st.checkbox("El setup es uno que ya he operado antes")
    c8 = st.checkbox("Tengo entrada, stop y target definidos")

    st.markdown("**4️⃣ RIESGO CONTROLADO**")
    c9 = st.checkbox("Acepto perder ANTES de entrar")

    st.markdown("**5️⃣ DISCIPLINA**")
    c10 = st.checkbox("No moveré el stop por emoción")
    c11 = st.checkbox("Si rompo una regla → cierro sesión")

    checklist_ok = all([c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11])

# ===============================
# 1) Checklist Diario (ANTES de operar)
# ===============================
st.markdown("## ☀️ Checklist Diario (Antes de Operar)")

col1, col2 = st.columns([0.75, 0.25], vertical_alignment="center")

with col1:
    d1 = st.checkbox("Agradecí y revisé mis metas hoy", key="d1")

with col2:
    st.link_button(
        "📊 Ver Dashboard",
        "https://estructura-kyljsyag88cneuncfnuobp.streamlit.app/"
    )

# ✅ Checkbox + "pestaña" (botón) que despliega el Marco Mental
col_left, col_right = st.columns([0.86, 0.14], vertical_alignment="center")
with col_left:
    d2 = st.checkbox("Leí el marco mental de trading", key="d2")

with col_right:
    # Streamlit moderno: popover (mejor UX)
    if hasattr(st, "popover"):
        with st.popover("📌 Ver", use_container_width=True):
            st.markdown("""
### 🔒 Protección contra improvisación
✅ Mi tarea diaria es ejecutar mi proceso de trading sin improvisar  
✅ Hoy solo tengo una tarea: ejecutar mi proceso de trading con disciplina  
✅ Mantengo control emocional, sigo mis reglas y respeto mis invalidaciones  
✅ No improvisé operaciones  
✅ Seguí el proceso correctamente  
✅ Respeté todas mis reglas  

### 🔒 Protección contra codicia
✅ No persigo dinero, persigo consistencia  
✅ El dinero es la consecuencia natural de ejecutar correctamente el sistema  
✅ Mi prioridad es control emocional, disciplina y respeto del proceso  

### 🔒 Protección contra venganza / recuperación emocional
✅ No intenté recuperar pérdidas  
✅ Estoy dispuesto a cerrar sesión aunque pierda  
✅ No hice overtrading  
✅ No abrí operaciones tardías  

### 🔒 Protección contra pérdida de control
✅ Respeté el riesgo diario máximo  
✅ Operé dentro del horario definido  
✅ Cerré la plataforma al finalizar la sesión  
✅ No revisé el mercado después de cerrar  
✅ Mantuve control emocional durante la sesión  
✅ Estoy emocionalmente estable para operar
""")
    else:
        # Fallback (si tu Streamlit es viejo): expander
        with st.expander("📌 Ver"):
            st.markdown("""
### 🔒 Protección contra improvisación
✅ Mi tarea diaria es ejecutar mi proceso de trading sin improvisar  
✅ Hoy solo tengo una tarea: ejecutar mi proceso de trading con disciplina  
✅ Mantengo control emocional, sigo mis reglas y respeto mis invalidaciones  
✅ No improvisé operaciones  
✅ Seguí el proceso correctamente  
✅ Respeté todas mis reglas  

### 🔒 Protección contra codicia
✅ No persigo dinero, persigo consistencia  
✅ El dinero es la consecuencia natural de ejecutar correctamente el sistema  
✅ Mi prioridad es control emocional, disciplina y respeto del proceso  

### 🔒 Protección contra venganza / recuperación emocional
✅ No intenté recuperar pérdidas  
✅ Estoy dispuesto a cerrar sesión aunque pierda  
✅ No hice overtrading  
✅ No abrí operaciones tardías  

### 🔒 Protección contra pérdida de control
✅ Respeté el riesgo diario máximo  
✅ Operé dentro del horario definido  
✅ Cerré la plataforma al finalizar la sesión  
✅ No revisé el mercado después de cerrar  
✅ Mantuve control emocional durante la sesión  
✅ Estoy emocionalmente estable para operar
""")

d3 = st.checkbox("Acepto que el mercado no me debe nada (solo probabilidades)", key="d3")
d4 = st.checkbox("No estoy operando para recuperar ni demostrar", key="d4")

checklist_diario_ok = all([d1, d2, d3, d4])

if not checklist_diario_ok:
    st.warning("⚠️ Completa el checklist diario para habilitar la operación y el guardado de trades.")

st.markdown("---")

# ===============================
# Selección de trade
# ===============================
activo = st.selectbox("📈 Activo", ["SPY", "SLV", "BTC"], key="activo")
tipo_trade = st.selectbox("🧩 Tipo de Trade", ["Intraday (solo sesión actual)", "Swing"], key="tipo_trade")
direccion = st.selectbox("➡️ Dirección", ["Call / Long", "Put / Short"], key="direccion")

# ===============================
# 2) Checklist de Sesión
# ===============================
st.markdown("## 🕒 Checklist de Sesión")

s1 = st.checkbox("Mi tipo de trade (Intraday/Swing) está claro", key="s1")
s2 = st.checkbox("Este trade respeta el timeframe elegido", key="s2")
s3 = st.checkbox("La invalidación corresponde al tipo de trade (intraday vs swing)", key="s3")

checklist_sesion_ok = all([s1, s2, s3])

if not checklist_sesion_ok:
    st.info("ℹ️ Completa el checklist de sesión para que el sistema habilite guardar el trade.")

# Timeframe por tipo
if "Intraday" in tipo_trade:
    timeframe_choices = ["1m", "5m", "15m", "30m", "1h"]
    default_tf = "5m"
else:
    timeframe_choices = ["1h", "4h", "1D"]
    default_tf = "1D"

timeframe = st.selectbox(
    "⏱ Timeframe de decisión (para invalidación)",
    timeframe_choices,
    index=timeframe_choices.index(default_tf),
    key="timeframe"
)

# ===============================
# CONTEXTO
# ===============================
contexto_intradia = ""
st.markdown("---")
st.subheader("🔧 Contexto")

if "Intraday" in tipo_trade:
    st.info("Trade válido **solo durante la sesión actual**, basado en estructura del día (VWAP / High-Low del día).")
    contexto_intradia = st.text_area(
        "🧭 Contexto intradía (obligatorio)",
        placeholder="Ej: Por debajo de VWAP, tendencia bajista del día. Busco put en retesteo VWAP hacia low del día.",
        key="contexto_intra"
    )
else:
    st.caption("Swing: define contexto en marco mayor (niveles, tendencia, invalidación de swing).")
    contexto_intradia = st.text_area(
        "🧭 Contexto (opcional pero recomendado)",
        placeholder="Ej: Swing en soporte semanal; invalidación debajo del nivel X en cierre diario.",
        key="contexto_swing"
    )

# ===============================
# Entrada/Stop/Target
# ===============================
st.markdown("---")
st.subheader("🎯 Plan del trade")

setup_clasificacion = st.radio(
    "🅰️ Clasificación del Setup",
    ["A", "B", "C"],
    horizontal=True,
    help="A = alta convicción | B = aceptable | C = solo estudio / NO operar"
)

col1, col2, col3 = st.columns(3)
with col1:
    entrada = st.number_input("🎯 Entrada", step=0.01, key="entrada")
with col2:
    stop = st.number_input("🛑 Stop (precio)", step=0.01, key="stop_precio")
with col3:
    target = st.number_input("💰 Target", step=0.01, key="target")

# ===============================
# Invalidación (ejemplos + input)
# ===============================
st.markdown("### ❌ Invalidación – ejemplos por activo")

if activo == "SLV":
    if direccion == "Call / Long":
        st.success(
            "✅ **SLV Long intraday – invalidación correcta**\n\n"
            "- Pierde el **low del día** y **no lo recupera en 2 velas de 5m**, **o**\n"
            "- Cierra 5m **debajo de VWAP** con **volumen**."
        )
    else:
        st.success(
            "✅ **SLV Put/Short intraday – invalidación correcta**\n\n"
            "- Reclaim de **VWAP** con **cierre 5m arriba** + volumen, **o**\n"
            "- Rompe el **high del retesteo** y se mantiene 2 velas."
        )
elif activo == "SPY":
    if direccion == "Call / Long":
        st.success(
            "✅ **SPY Call/Long intraday – invalidación**\n\n"
            "- Cierre 5m **debajo de VWAP**, **o**\n"
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
            "- Cierre 15m **debajo del nivel clave**, **o**\n"
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
    placeholder="Escribe la condición exacta que MATA la idea (hoy si es intraday).",
    key="invalidacion"
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
        ],
        key="regla_sel"
    )
    if regla_sel == "Otra (escríbela)":
        regla_tiempo = st.text_input(
            "Escribe tu regla de tiempo",
            placeholder="Ej: Si en 20 min no rompe el nivel → cierro.",
            key="regla_custom"
        )
    else:
        regla_tiempo = regla_sel

    regla_tiempo_ok = len(regla_tiempo.strip()) > 10
    st.caption("👉 Intraday muere hoy: si el tiempo no juega a favor, se cierra.")

# ===============================
# ✅ Capital + Riesgo exacto (Opciones)
# ===============================
st.markdown("---")
st.subheader("💰 Capital + Riesgo exacto (Opciones)")

colA, colB, colC = st.columns(3)
with colA:
    fondo_inversion = st.number_input("💼 Fondo de inversión disponible ($)", min_value=0.0, step=100.0, format="%.2f", key="fondo_inv")
with colB:
    limite_riesgo_diario = st.number_input("📅 Límite de riesgo diario ($)", min_value=0.0, step=10.0, format="%.2f", key="lim_diario")
with colC:
    limite_riesgo_trade = st.number_input("🎯 Límite de riesgo por trade ($)", min_value=0.0, step=10.0, format="%.2f", key="lim_trade")

st.markdown("### 🧾 Parámetros del trade (comprando opciones)")

col1, col2, col3 = st.columns(3)
with col1:
    contratos = st.number_input("📦 # Contratos", min_value=1, step=1, value=1, key="contracts")
with col2:
    prima_entrada = st.number_input("💲 Prima de entrada (por contrato)", min_value=0.00, step=0.01, format="%.2f", key="premium_in")
with col3:
    prima_stop = st.number_input("🛑 Stop en prima (por contrato)", min_value=0.00, step=0.01, format="%.2f", key="premium_stop")

# Cálculos (asumiendo LONG)
costo_entrada_usd = float(contratos) * 100.0 * float(prima_entrada)
riesgo_usd = float(contratos) * 100.0 * max(float(prima_entrada) - float(prima_stop), 0.0)

# Validaciones
capital_ok = (fondo_inversion > 0) and (limite_riesgo_diario > 0) and (limite_riesgo_trade > 0)
trade_ok = (contratos >= 1) and (prima_entrada > 0)

# Para compras (LONG), el stop debe estar por debajo de la entrada
stop_prima_ok = prima_stop < prima_entrada if trade_ok else False

# Reglas financieras
fondo_ok = (costo_entrada_usd <= fondo_inversion) if (capital_ok and trade_ok) else False
riesgo_ok_trade = (riesgo_usd <= limite_riesgo_trade) if (capital_ok and trade_ok and stop_prima_ok) else False
riesgo_ok_diario = (riesgo_usd <= limite_riesgo_diario) if (capital_ok and trade_ok and stop_prima_ok) else False
riesgo_ok = riesgo_ok_trade and riesgo_ok_diario

st.info(
    f"📌 **Costo de entrada:** ${costo_entrada_usd:,.2f}\n\n"
    f"🧮 **Riesgo exacto hasta stop:** ${riesgo_usd:,.2f}\n\n"
    f"⚠️ **Peor caso (prima a 0):** ${costo_entrada_usd:,.2f}"
)

if trade_ok and not stop_prima_ok:
    st.error("🚫 Stop inválido: para compras (LONG), la prima de stop debe ser MENOR que la prima de entrada.")

if capital_ok and trade_ok and not fondo_ok:
    st.error("🚫 No cuadra: el costo de entrada excede tu fondo de inversión.")

if capital_ok and trade_ok and stop_prima_ok and not riesgo_ok_trade:
    st.error("🚫 El riesgo hasta el stop excede tu límite de riesgo por trade.")

if capital_ok and trade_ok and stop_prima_ok and not riesgo_ok_diario:
    st.error("🚫 El riesgo hasta el stop excede tu límite de riesgo diario.")

acepto_perder_financiero = st.checkbox(
    "✅ Acepto esta pérdida ANTES de entrar. Si toca stop, cierro sin negociar.",
    value=False,
    key="acepto_perder_fin"
)

st.caption("🧠 Recordatorio: **El stop es un costo operativo.** Romperlo = pagar doble (dinero + disciplina).")

gate_financiero_ok = all([
    capital_ok,
    trade_ok,
    stop_prima_ok,
    fondo_ok,
    riesgo_ok,
    acepto_perder_financiero
])

if gate_financiero_ok:
    st.success("✅ Gate financiero ACTIVO: riesgo aceptado y calculado con precisión.")
else:
    st.warning("⚠️ Gate financiero incompleto: si no está listo, no se guarda el trade.")

# ===============================
# Checklist emocional (core)
# ===============================
st.markdown("---")
st.subheader("🧠 Checklist emocional (obligatorio)")

c1 = st.checkbox("Tengo invalidación clara y objetiva", key="c1")
# Cambiamos el antiguo c2 para no duplicar el concepto financiero exacto
c2 = st.checkbox("Respeto el stop sin moverlo (stop = costo operativo)", key="c2_stop_operativo")
c3 = st.checkbox("No estoy molesto ni buscando recuperar", key="c3")
c4 = st.checkbox("Este trade sigue mi sistema, no mi emoción", key="c4")

checklist_ok = all([c1, c2, c3, c4])

# ===============================
# Checklist intraday (extra)
# ===============================
checklist_intradia_ok = True
if "Intraday" in tipo_trade:
    st.subheader("⚡ Checklist intraday (ajustado)")
    i1 = st.checkbox("Este trade muere hoy sí o sí (no depende de mañana)", key="i1")
    i2 = st.checkbox("Mi stop depende de la estructura del DÍA (VWAP / High-Low), no de esperanza", key="i2")
    i3 = st.checkbox("Acepto salir plano si el tiempo no juega a favor", key="i3")
    i4 = st.checkbox("Estoy tranquilo; no necesito que 'funcione'", key="i4")

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
    ["🟢 Calmo y enfocado", "🟡 Tenso / dudando", "🔴 Molesto / ansioso"],
    key="estado"
)

estado_ok = estado == "🟢 Calmo y enfocado"

if estado == "🔴 Molesto / ansioso":
    st.error("🚫 NO OPERAR. Esto es autoprotección.")
elif estado == "🟡 Tenso / dudando":
    st.warning("⚠️ Si estás 🟡, solo operar setups A+ (si no es A+, no se guarda).")
else:
    st.success("✅ Estado mental adecuado")

# ===============================
# Gate A+ (emocional) y Gate A+ (macro Neutral)
# ===============================
a_plus_ok = True

# Gate por estado emocional 🟡
if estado == "🟡 Tenso / dudando":
    a_plus_ok = st.checkbox("Confirmo que este es un setup A+ (por estar 🟡)", key="a_plus_yellow")

# Gate por macro Neutral
macro_requires_aplus = (st.session_state.get("macro_mode", "").startswith("🟡 Neutral"))
if macro_requires_aplus:
    st.warning("🟡 Macro = Neutral → SOLO setups A+ (regla anti-sabotaje automática).")
    a_plus_macro = st.checkbox("Confirmo que es un setup A+ (por Macro Neutral)", key="a_plus_macro")
    a_plus_ok = a_plus_ok and a_plus_macro

# ===============================
# Validaciones finales para guardar
# ===============================
contexto_ok = True
if "Intraday" in tipo_trade:
    contexto_ok = len(contexto_intradia.strip()) > 15

puede_guardar = all([
    checklist_diario_ok,
    checklist_sesion_ok,
    invalidacion_ok,
    checklist_ok,
    checklist_intradia_ok,
    estado_ok,
    a_plus_ok,
    regla_tiempo_ok,
    contexto_ok,
    gate_financiero_ok,  # ✅ nuevo gate financiero
])

st.markdown("---")

def guardar_trade():
    df = pd.read_csv(CSV_FILE)

    nuevo = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "activo": activo,
        "tipo_trade": tipo_trade,
        "direccion": direccion,
        "setup_clasificacion": setup_clasificacion,
        "contexto_intradia": contexto_intradia,
        "entrada": entrada,
        "stop": stop,
        "target": target,
        "invalidacion": invalidacion,
        "regla_tiempo": regla_tiempo,
        "timeframe": timeframe,
        "estado_emocional": estado,

        # Macro snapshot
        "macro_mode": snap.get("macro_mode", ""),
        "macro_rule": snap.get("macro_rule", ""),
        "macro_es": f"{snap['es'].label} ({snap['es'].change_pct:+.2f}%)",
        "macro_vix": f"{snap['vix'].label} ({snap['vix'].change_pct:+.2f}%)",
        "macro_dxy": f"{snap['dxy'].label} ({snap['dxy'].change_pct:+.2f}%)",
        "macro_high_impact_news": "sí" if snap.get("has_high") else "no",
        "macro_es_src": snap.get("es_src", ""),
        "macro_vix_src": snap.get("vix_src", ""),
        "macro_dxy_src": snap.get("dxy_src", ""),

        "checklist_diario_ok": checklist_diario_ok,
        "checklist_sesion_ok": checklist_sesion_ok,
        "checklist_ok": checklist_ok,
        "checklist_intradia_ok": checklist_intradia_ok,

        # ✅ Capital / riesgo exacto
        "fondo_inversion": float(fondo_inversion),
        "limite_riesgo_diario": float(limite_riesgo_diario),
        "limite_riesgo_trade": float(limite_riesgo_trade),
        "contratos": int(contratos),
        "prima_entrada": float(prima_entrada),
        "prima_stop": float(prima_stop),
        "costo_entrada_usd": float(costo_entrada_usd),
        "riesgo_usd": float(riesgo_usd),
        "acepto_perder_financiero": bool(acepto_perder_financiero),
    }

    # Asegurar columnas (retro-compat)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

if not puede_guardar:
    st.button("🚫 Guardar Trade (bloqueado)", disabled=True)

    missing = []
    if not checklist_diario_ok:
        missing.append("Checklist diario")
    if not checklist_sesion_ok:
        missing.append("Checklist de sesión")
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
    if estado == "🟡 Tenso / dudando":
        missing.append("Confirmación de setup A+ (por estar 🟡)")
    if macro_requires_aplus:
        missing.append("Confirmación de setup A+ (por Macro Neutral)")

    # Gate financiero detallado
    if not capital_ok:
        missing.append("Capital/límites (fondo + riesgo diario + riesgo por trade)")
    if not trade_ok:
        missing.append("Opciones: contratos + prima de entrada")
    if trade_ok and not stop_prima_ok:
        missing.append("Stop en prima válido (prima_stop < prima_entrada)")
    if capital_ok and trade_ok and not fondo_ok:
        missing.append("Costo entrada ≤ fondo")
    if capital_ok and trade_ok and stop_prima_ok and not riesgo_ok_trade:
        missing.append("Riesgo ≤ límite por trade")
    if capital_ok and trade_ok and stop_prima_ok and not riesgo_ok_diario:
        missing.append("Riesgo ≤ límite diario")
    if not acepto_perder_financiero:
        missing.append("Aceptar la pérdida (confirmación financiera)")

    st.info("Para habilitar Guardar, completa: " + " | ".join(missing))
else:
    st.caption("🧠 Antes de guardar: si toca stop, **cierro sin negociar**. Costo operativo.")
    if st.button("💾 Guardar Trade"):
        guardar_trade()
        st.success("✅ Trade guardado con disciplina")

# ===============================
# Tabla de últimos registros
# ===============================
st.markdown("## 📑 Últimos Trades Registrados")
df_show = pd.read_csv(CSV_FILE)
st.dataframe(df_show.tail(20), use_container_width=True)

st.markdown("---")
st.subheader("📤 Exportar Trades")

def generar_excel():
    df = pd.read_csv(CSV_FILE)
    nombre_archivo = f"diario_trading_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    df.to_excel(nombre_archivo, index=False)
    return nombre_archivo

if st.button("📊 Generar Excel de Trades"):
    archivo = generar_excel()
    with open(archivo, "rb") as f:
        st.download_button(
            label="⬇️ Descargar Excel",
            data=f,
            file_name=archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


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
