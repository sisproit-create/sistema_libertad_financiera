
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="📊 Plan Diario de Trading", layout="centered")

CSV_FILE = "diario_trading.csv"

if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "fecha","activo","tipo_trade","direccion",
        "entrada","stop","target",
        "invalidacion","estado_emocional","checklist_ok"
    ])
    df_init.to_csv(CSV_FILE, index=False)

st.sidebar.markdown("""
## 🧠 Reglas de Oro
- El mercado no premia justicia, premia probabilidades.
- El stop es un costo operativo.
- No recupero desde emoción.
""")

st.sidebar.markdown("📘 Llena el diario ANTES de operar.")

st.title("📊 Dashboard – Plan Diario de Trading")

activo = st.selectbox("📈 Activo", ["SPY","SLV","BTC"])
tipo_trade = st.selectbox("🧩 Tipo de Trade", ["Intraday","Swing"])
direccion = st.selectbox("➡️ Dirección", ["Call / Long","Put / Short"])

col1,col2,col3 = st.columns(3)
with col1:
    entrada = st.number_input("🎯 Entrada", step=0.01)
with col2:
    stop = st.number_input("🛑 Stop", step=0.01)
with col3:
    target = st.number_input("💰 Target", step=0.01)

st.markdown("### ❌ Invalidación (obligatoria)")
invalidacion = st.text_area("Describe cuándo el trade queda inválido")

invalidacion_ok = len(invalidacion.strip()) > 15

st.subheader("🧠 Checklist emocional")
c1 = st.checkbox("Tengo invalidación clara")
c2 = st.checkbox("Acepto la pérdida antes de entrar")
c3 = st.checkbox("No estoy molesto ni buscando recuperar")
c4 = st.checkbox("Este trade sigue mi sistema")

checklist_ok = all([c1,c2,c3,c4])

st.subheader("🚦 Estado emocional")
estado = st.radio("Estado actual",["🟢 Calmo","🟡 Tenso","🔴 Molesto"])
estado_ok = estado == "🟢 Calmo"

puede_guardar = invalidacion_ok and checklist_ok and estado_ok

def guardar():
    df = pd.read_csv(CSV_FILE)
    df.loc[len(df)] = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        activo,tipo_trade,direccion,
        entrada,stop,target,
        invalidacion,estado,checklist_ok
    ]
    df.to_csv(CSV_FILE,index=False)

if not puede_guardar:
    st.button("🚫 Guardar (bloqueado)",disabled=True)
else:
    if st.button("💾 Guardar Trade"):
        guardar()
        st.success("Trade guardado con disciplina")

st.markdown("## 📑 Últimos trades")
st.dataframe(pd.read_csv(CSV_FILE).tail(10))
