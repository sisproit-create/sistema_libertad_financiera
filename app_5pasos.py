import streamlit as st
import pandas as pd
from datetime import datetime
import os

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
# ZONA OPERATIVA
# ===============================
st.markdown("## 🎯 Zona Operativa")

activo = st.selectbox("📈 Activo", ["SPY", "SLV", "BTC"])
direccion = st.selectbox("➡️ Dirección", ["Long", "Short"])

col1, col2, col3 = st.columns(3)
with col1:
    entrada = st.number_input("🎯 Entrada", step=0.01)
with col2:
    stop = st.number_input("🛑 Stop", step=0.01)
with col3:
    target = st.number_input("💰 Target", step=0.01)

# ===============================
# 💰 RIESGO (VISIBLE Y CONTROLABLE)
# ===============================
st.markdown("## 💰 Riesgo del Trade")

position_size = st.number_input(
    "📦 Tamaño de posición (shares / contratos)",
    min_value=1,
    step=1,
    value=100
)

riesgo_usd = abs(entrada - stop) * position_size
riesgo_limite = 100.0

st.info(
    f"""
    **Cálculo del riesgo:**
    
    Riesgo = |Entrada − Stop| × Tamaño  
    Riesgo = |{entrada} − {stop}| × {position_size}  
    **Riesgo total = ${riesgo_usd:.2f}**
    """
)

riesgo_ok = riesgo_usd <= riesgo_limite

if riesgo_ok:
    st.success("✅ Riesgo dentro del límite permitido")
else:
    st.error(f"🚫 Riesgo excede el límite (${riesgo_limite:.2f}) → ajusta STOP o TAMAÑO")

# ===============================
# ESTADO EMOCIONAL
# ===============================
st.markdown("## 🚦 Estado Emocional")

estado_emocional = st.radio(
    "¿Cómo estás ahora mismo?",
    ["🟢 Calmo y enfocado", "🟡 Tenso / dudando", "🔴 Molesto / ansioso"]
)

estado_ok = estado_emocional == "🟢 Calmo y enfocado"

if estado_emocional == "🔴 Molesto / ansioso":
    st.error("🚫 NO OPERAR. Autoprotección.")
elif estado_emocional == "🟡 Tenso / dudando":
    st.warning("⚠️ Solo setups A+")

# ===============================
# GUARDAR TRADE
# ===============================
st.markdown("---")

puede_guardar = all([
    checklist_ok,
    estado_mental_ok,
    riesgo_ok,
    estado_ok,
    entrada > 0,
    stop > 0,
    target > 0
])

def guardar_trade():
    df = pd.read_csv(CSV_FILE)
    nuevo = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "activo": activo,
        "direccion": direccion,
        "entrada": entrada,
        "stop": stop,
        "target": target,
        "position_size": position_size,
        "riesgo_usd": riesgo_usd,
        "estado_emocional": estado_emocional,
        "checklist_ok": checklist_ok
    }
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

if puede_guardar:
    if st.button("💾 Guardar Trade"):
        guardar_trade()
        st.success("✅ Trade guardado con disciplina")
else:
    st.button("🚫 Guardar Trade (bloqueado)", disabled=True)
    st.caption("Completa checklist, estado 🟢 y riesgo válido para habilitar.")

# ===============================
# HISTORIAL
# ===============================
st.markdown("## 📑 Últimos Trades")
df_show = pd.read_csv(CSV_FILE)
st.dataframe(df_show.tail(15), use_container_width=True)
