import streamlit as st
import json
import os
from datetime import date

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Dashboard Personal 2026", layout="wide")

DATA_FILE = "tasks_data.json"

# =========================
# DEFAULT TASKS
# =========================
DEFAULT_TASKS = {
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

# =========================
# DATA FUNCTIONS
# =========================
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def normalize_tasks(data):
    normalized = {}
    for cat, tasks in data.items():
        normalized[cat] = []
        for t in tasks:
            normalized[cat].append({
                "text": t.get("text", ""),
                "done": t.get("done", False),
                "notes": t.get("notes", ""),
                "priority": t.get("priority", "Media"),
                "due": t.get("due", None)
            })
    return normalized

def sync_default_tasks(existing):
    for cat, task_list in DEFAULT_TASKS.items():
        if cat not in existing:
            existing[cat] = []

        existing_texts = {t["text"] for t in existing[cat]}

        for txt in task_list:
            if txt not in existing_texts:
                existing[cat].append({
                    "text": txt,
                    "done": False,
                    "notes": "",
                    "priority": "Media",
                    "due": None
                })
    return existing

# =========================
# INIT SESSION
# =========================
if "tasks" not in st.session_state:
    loaded = normalize_tasks(load_tasks())
    st.session_state.tasks = sync_default_tasks(loaded)
    save_tasks(st.session_state.tasks)

# =========================
# UI
# =========================
st.title("📊 Dashboard Personal 2026")

modo_edicion = st.toggle("✏️ Modo edición", value=False)

for category, tasks in st.session_state.tasks.items():
    st.subheader(category)

    for idx, task in enumerate(tasks):
        cols = st.columns([0.05, 0.45, 0.15, 0.15, 0.15, 0.05])

        with cols[0]:
            task["done"] = st.checkbox(
                label="Completar tarea",
                value=task["done"],
                key=f"{category}_{idx}_done",
                label_visibility="collapsed"
            )

        with cols[1]:
            if modo_edicion:
                task["text"] = st.text_input(
                    "Texto tarea",
                    value=task["text"],
                    key=f"{category}_{idx}_text",
                    label_visibility="collapsed"
                )
            else:
                st.write(task["text"])

        with cols[2]:
            if modo_edicion:
                task["priority"] = st.selectbox(
                    "Prioridad",
                    ["Alta", "Media", "Baja"],
                    index=["Alta", "Media", "Baja"].index(task["priority"]),
                    key=f"{category}_{idx}_prio",
                    label_visibility="collapsed"
                )
            else:
                st.write(task["priority"])

        with cols[3]:
            if modo_edicion:
                task["due"] = st.date_input(
                    "Fecha",
                    value=date.fromisoformat(task["due"]) if task["due"] else None,
                    key=f"{category}_{idx}_due",
                    label_visibility="collapsed"
                )
                task["due"] = task["due"].isoformat() if task["due"] else None
            else:
                st.write(task["due"] if task["due"] else "")

        with cols[4]:
            if modo_edicion:
                task["notes"] = st.text_area(
                    "Notas",
                    value=task["notes"],
                    key=f"{category}_{idx}_notes",
                    label_visibility="collapsed"
                )
            else:
                if task["notes"]:
                    st.caption(task["notes"])

        with cols[5]:
            if modo_edicion:
                if st.button("🗑️", key=f"{category}_{idx}_del"):
                    tasks.pop(idx)
                    save_tasks(st.session_state.tasks)
                    st.rerun()

    if modo_edicion:
        if st.button(f"➕ Añadir tarea en {category}", key=f"add_{category}"):
            tasks.append({
                "text": "Nueva tarea",
                "done": False,
                "notes": "",
                "priority": "Media",
                "due": None
            })
            save_tasks(st.session_state.tasks)
            st.rerun()

    st.divider()

save_tasks(st.session_state.tasks)
