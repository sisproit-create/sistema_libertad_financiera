import streamlit as st
import json
import os
from datetime import datetime, date
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="✅ Dashboard de Tareas y Metas", layout="wide")

# =========================
# Persistencia
# =========================
DATA_DIR = Path(".")
STATE_FILE = DATA_DIR / "checklist_state.json"
LOG_FILE = DATA_DIR / "checklist_log.csv"

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def append_log(row: dict):
    exists = LOG_FILE.exists()
    df = pd.DataFrame([row])
    df.to_csv(LOG_FILE, mode="a", header=not exists, index=False)

state = load_state()
today = date.today().isoformat()

# Reinicio automático diario (sin borrar el historial)
if state.get("date") != today:
    state = {"date": today, "checks": {}}
    save_state(state)

checks = state.get("checks", {})

# =========================
# Definición de tareas
# =========================
TASKS = {
    "A. Gratitud y enfoque diario": [
        "Agradecer por lo feliz y maravilloso que me siento con esta vida hoy.",
        "Repetir mi mantra: “Soy más de lo que aparento, toda la fuerza y el poder del mundo están en mi interior.”",
        "Revisar todos los días mis metas y objetivos.",
        "Enfocarme en mis Top 5 ideas de negocio.",
        "Fortalecer mis hábitos de acumulación.",
        "Tener fuerza de voluntad y pensar antes de actuar.",
        "Tener claro lo que quiero y crear planes hacia $1,000,000 USD.",
        "Luchar e idear planes para mantener e incrementar mi acumulación.",
        "Cambiar hábitos que me detienen.",
        "Decidir actuar en serio y superar bloqueos.",
        "Definir deseos, tomar decisiones y mantener disciplina.",
        "Comprometerme a ser un buen conductor.",
        "Transmutar impulsos sexuales en energía productiva (creatividad y logros).",
    ],
    "B. Salud y bienestar personal": [
        "Seguimiento a exámenes pendientes por autorización; planificar operación de la vesícula.",
        "Continuar salud dental; sacar otra cita y seguir tratamiento.",
        "Actividad física (mínimo 3 días/semana).",
        "Comprar comida saludable y jugo verde para la mañana.",
        "Crear hábito de levantarme a las 5:30 a. m.",
        "Alinear buena alimentación con comida sana, rendidora y con ahorro.",
    ],
    "C. Lectura y aprendizaje": [
        "Terminar de leer El código del dinero y luego Hábitos atómicos.",
        "Comprar libros en Colombia (Padre Rico–Padre Pobre, Secretos mente millonaria, Mi primer millón, E-Myth).",
        "Leer libro de Cemento Asfáltico.",
        "Retomar clases de inglés.",
    ],
    "D. Negocios y proyectos clave": [
        "Seguir el plan de negocio de préstamos cripto y diseñar el MVP.",
        "Buscar CTO/cofundador para NestVault.",
        "Conseguir cliente nuevo para CONSIHSA.",
        "Planificar envío de dinero a hijos en EE. UU.",
        "Buscar escuelas para Nicole en Panamá.",
        "Registrar y legalizar papeles de divorcio.",
    ],
    "E. Facturación y finanzas operativas": [
        "Facturación del mes de SISPRO y envío de facturas.",
        "Dar seguimiento a negocio con Aleco y facturar venta.",
        "Dar seguimiento a Multifin (eventual cambio de servidor).",
        "Resolver problema de facturación con SISPRO o abrir nueva empresa.",
        "Evaluar apertura de nueva empresa o fundación (facturación / protección de activos / planificación patrimonial).",
    ],
    "F. Operaciones y mejoras de procesos": [
        "Mejorar y terminar la lógica del control de combustible con el nuevo tanque y proceso.",
        "Automatizar el cuadro actualizado de toneladas por proyecto.",
        "Actualizar script e incluir reporte de costo de producción, combustible y AC30.",
        "Generar script que calcule cuándo solicitar más AC30 según toneladas programadas.",
        "Centralizar bases de datos en la nube para acceso compartido.",
        "Supervisar planta e idear mejoras o automatizaciones.",
        "Instalar memorias nuevas en cámaras de laboratorio y oficina.",
        "Revisar correos que pierden licencia y reasignar (KING NOVA).",
        "Estructurar uso de laboratorio, manejo de pruebas y procedimientos.",
    ],
    "G. Otros compromisos y pendientes": [
        "Dar seguimiento a la reparación del auto (pintar retrovisores).",
        "Dar seguimiento a publicación y venta del auto en Marketplace y Encuentra24.",
    ],
    "H. Inversión y Trading — Gestión Mental y Reglas Personales": [
        "Vigilar patrón: injusticia → NO operar hasta enfriar.",
        "Marco mental: el mercado no premia justicia; solo probabilidades.",
        "Frase ancla: “Este trade es una apuesta probabilística, no un juicio moral.”",
        "Reglas: prohibido recuperar; stop es contrato; 1 trade emocional máximo (ideal 0).",
        "Tipo recomendado: intraday estructurado / swing con invalidación clara; evitar scalping caótico y trading por noticias sin plan.",
        "Checklist pre-trade: invalidación clara, acepto pérdida, no molesto, setup estructural.",
        "Recordatorio: mi edge aparece cuando sigo reglas, no cuando busco tener razón.",
    ],
    "I. Inversión patrimonial personal": [
        "Comprar apartamento en Punta Pacífica, Panamá.",
        "Buscar apartamento adecuado en el momento oportuno.",
        "Recordatorio: aunque no sea nuevo, tendrá la vista que quiero.",
        "Invertir lo justo, remodelar poco a poco e incrementar valor.",
        "Mantener esta meta como parte del plan patrimonial.",
        "Comprar Mercedes Clase G63 con ganancias como símbolo de progreso.",
    ],
    "J. Relaciones personales": [
        "Construir una relación sana con la persona que está llegando a mi vida.",
        "Permitir que las cosas evolucionen de forma orgánica y sin forzar.",
    ],
}

# Subtareas Top 5 (A)
TOP5 = [
    "Préstamos cripto con respaldo inmobiliario.",
    "Comprar propiedades en EE. UU., Panamá y Colombia, y ser Realtor.",
    "Negocio en ciberseguridad.",
    "Comprar y reformar propiedades.",
    "Desarrollo de software y automatización de procesos.",
]

# =========================
# Header
# =========================
st.title("✅ Dashboard de Tareas y Metas – Checklist")
st.caption(f"Fecha: {today}  |  Guarda estado diario en {STATE_FILE.name} y log en {LOG_FILE.name}")

# =========================
# Controles globales
# =========================
colA, colB, colC, colD = st.columns([1, 1, 1, 2])
with colA:
    show_only_pending = st.toggle("Mostrar solo pendientes", value=False)
with colB:
    expand_all = st.toggle("Expandir todo", value=False)
with colC:
    compact = st.toggle("Vista compacta", value=False)
with colD:
    q = st.text_input("🔎 Buscar", placeholder="Ej: VWAP, dental, NestVault, facturación...").strip().lower()

st.divider()

# =========================
# Helpers
# =========================
def key_for(section: str, task: str) -> str:
    return f"{section}::{task}"

def passes_search(section: str, task: str) -> bool:
    if not q:
        return True
    return (q in section.lower()) or (q in task.lower())

def is_checked(section: str, task: str) -> bool:
    return bool(checks.get(key_for(section, task), False))

def set_checked(section: str, task: str, value: bool):
    checks[key_for(section, task)] = bool(value)

def section_progress(section: str, tasks: list[str]) -> tuple[int, int]:
    total = 0
    done = 0
    for t in tasks:
        if not passes_search(section, t):
            continue
        total += 1
        if is_checked(section, t):
            done += 1
    return done, total

# =========================
# Render secciones
# =========================
overall_done = 0
overall_total = 0

for section, tasks in TASKS.items():
    done, total = section_progress(section, tasks)
    overall_done += done
    overall_total += total

st.subheader("📊 Progreso general")
if overall_total > 0:
    st.progress(overall_done / overall_total)
st.write(f"Completadas: **{overall_done} / {overall_total}**")

st.divider()

for section, tasks in TASKS.items():
    done, total = section_progress(section, tasks)
    if show_only_pending and total > 0 and done == total:
        continue

    exp = st.expander(f"{section}  —  {done}/{total}", expanded=expand_all)

    with exp:
        if section == "A. Gratitud y enfoque diario":
            st.markdown("**Top 5 ideas de negocio (marcar si las revisaste hoy):**")
            for idea in TOP5:
                if not passes_search("Top 5", idea):
                    continue
                k = key_for("A.Top5", idea)
                val = bool(checks.get(k, False))
                new_val = st.checkbox(idea, value=val, key=k)
                checks[k] = new_val
            st.divider()

        # Render tareas principales
        for t in tasks:
            if not passes_search(section, t):
                continue
            if show_only_pending and is_checked(section, t):
                continue

            k = key_for(section, t)
            val = bool(checks.get(k, False))

            if compact:
                new_val = st.checkbox(t, value=val, key=k)
            else:
                new_val = st.checkbox(f"☐ {t}", value=val, key=k)

            checks[k] = new_val

# =========================
# Guardar / Reset / Export
# =========================
st.divider()
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

with col1:
    if st.button("💾 Guardar estado"):
        state["checks"] = checks
        save_state(state)
        st.success("Estado guardado.")

with col2:
    if st.button("🧾 Guardar log (snapshot)"):
        # snapshot con conteo
        # count everything (including Top5)
        all_keys = list(checks.keys())
        done_count = sum(1 for k in all_keys if checks.get(k))
        append_log({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": today,
            "done": done_count,
            "total": len(all_keys),
            "notes": ""
        })
        st.success("Snapshot guardado en el log.")

with col3:
    if st.button("🔄 Reiniciar checklist del día"):
        state = {"date": today, "checks": {}}
        checks = state["checks"]
        save_state(state)
        st.warning("Checklist reiniciado para hoy. (El log no se borra)")

with col4:
    st.caption("Tip: usa Buscar para filtrar tareas por palabra clave. Ej: 'VWAP', 'dental', 'NestVault'.")

# Auto-save al final de cada run para no perder checks
state["checks"] = checks
save_state(state)
