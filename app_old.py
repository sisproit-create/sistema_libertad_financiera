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
st.sidebar.markdown("- Llena el diario ANTES de operar.\n- Respeta el plan que escribas aquí.")

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
st.header("2️⃣ Plan de Trading del Día (Niveles + Reglas)")

st.subheader("SPY")
col_spy1, col_spy2 = st.columns(2)
with col_spy1:
    spy_calls_nivel = st.text_input("Calls solo si rompe / sostiene arriba de:", "")
    spy_puts_nivel = st.text_input("Puts solo si pierde:", "")
with col_spy2:
    spy_premarket = st.text_input("Tendencia premarket:", "")
    spy_zona_ruido = st.text_input("Zona donde NO operar (ruido):", "")

st.markdown("---")

st.subheader("QQQ")
col_qqq1, col_qqq2 = st.columns(2)
with col_qqq1:
    qqq_calls_nivel = st.text_input("Calls si rompe:", "")
with col_qqq2:
    qqq_puts_nivel = st.text_input("Puts si pierde (QQQ):", "")
qqq_momentum = st.text_input("Momentum actual:", "")

st.markdown("---")

st.subheader("SLV (activo estrella del día)")
col_slv1, col_slv2 = st.columns(2)
with col_slv1:
    slv_calls_nivel = st.text_input("Calls si mantiene arriba de:", "")
    slv_objetivo = st.text_input("Objetivo:", "")
with col_slv2:
    slv_stop = st.text_input("Stop:", "")
    slv_puts_nivel = st.text_input("Puts si pierde (SLV):", "")

slv_nota = st.text_area(
    "Razón por la que SLV tiene mejor setup hoy:",
    ""
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

st.caption(
    "💡 Puedes usar 2–5% del capital como referencia para el riesgo por trade."
)

regla_oro_opciones = [
    "NO sobreoperar",
    "Tomar ganancias en 20–30%",
    "Cortar pérdida sin dudar",
    "Solo operar si se cumple el plan"
]

regla_oro = st.multiselect(
    "Regla de oro del día (elige 2 preferiblemente):",
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
    "Enfocado"
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
# BOTÓN: Guardar registro
# -------------------------
st.markdown("---")

if st.button("💾 Guardar diario de hoy"):
    # Construir registro como dict
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

        # QQQ
        "qqq_calls_nivel": qqq_calls_nivel,
        "qqq_puts_nivel": qqq_puts_nivel,
        "qqq_momentum": qqq_momentum,

        # SLV
        "slv_calls_nivel": slv_calls_nivel,
        "slv_objetivo": slv_objetivo,
        "slv_stop": slv_stop,
        "slv_puts_nivel": slv_puts_nivel,
        "slv_nota": slv_nota,

        # Riesgo
        "capital_total": capital_total,
        "max_riesgo_trade": max_riesgo_trade,
        "max_monto_trade": max_monto_trade,
        "regla_oro": ", ".join(regla_oro),

        # Emociones
        "emociones": ", ".join(emociones),
        "comentario_emocional": comentario_emocional,
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

    # Filtro por fecha
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        fecha_min = st.date_input(
            "Desde fecha:",
            value=df_hist["fecha"].min().date()
        )
    with col_h2:
        fecha_max = st.date_input(
            "Hasta fecha:",
            value=df_hist["fecha"].max().date()
        )

    mask = (df_hist["fecha"].dt.date >= fecha_min) & (df_hist["fecha"].dt.date <= fecha_max)
    df_filtrado = df_hist[mask]

    st.write(f"Registros entre {fecha_min} y {fecha_max}: {len(df_filtrado)}")
    st.dataframe(df_filtrado)
else:
    st.info("Aún no hay registros guardados. Guarda tu primer diario para ver el historial aquí.")
