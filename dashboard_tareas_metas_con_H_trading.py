import streamlit as st
import json
import os
from datetime import date
from uuid import uuid4

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Dashboard Personal 2026", layout="wide")

DATA_FILE = "tasks_data.json"

# =========================
# DEFAULT TASKS (SOLO PRIMERA VEZ)
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
        "Transmutar impulsos sexuales en energía productiva.",
    ],
    "B. Salud y bienestar personal": [
        "Seguimiento a exámenes pendientes por autorización.",
        "Continuar salud dental.",
        "Actividad física mínimo 3 días por semana.",
        "Comprar comida saludable.",
        "Crear hábito de levantarme a las 5:30 a.m.",
    ],
    "C. Lectura y aprendizaje": [
        "Terminar El código del dinero.",
        "Leer Hábitos Atómicos.",
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
    # =========================
    # H — SISTEMA DE LIBERTAD FINANCIERA
    # =========================

    "H1_IDENTIDAD_OPERATIVA": [
        "Soy una persona disciplinada y constante en el trading",
        "Mi objetivo financiero es alcanzar un millón de dólares",
        "Mi tarea diaria es ejecutar mi proceso de trading sin improvisar",
        "Opero con un capital inicial de 800 USD, enfocado en duplicarlo con consistencia, no con prisa",
        "Repito el proceso hasta que la constancia sea un hábito automático",
        "Cuando el hábito está consolidado, incremento el capital y repito exactamente el mismo proceso",
        "Mi prioridad es control emocional, disciplina y respeto del proceso",
        "El dinero es la consecuencia natural de ejecutar correctamente el sistema"
    ],

    "H2_MANTRA_OPERATIVO_DIARIO": [
        "Hoy solo tengo una tarea: ejecutar mi proceso de trading con disciplina",
        "No persigo dinero, persigo consistencia",
        "Mi capital crece como resultado de hacer bien el proceso, una y otra vez",
        "Mantengo control emocional, sigo mis reglas y respeto mis invalidaciones",
        "La constancia es mi ventaja",
        "La constancia me lleva al millón"
    ],

    "H3_ACTIVACION_DIARIA_FILTRO_DE_PERMISO": [
        "Leí el mantra operativo",
        "Revisé el checklist diario",
        "Estoy emocionalmente estable para operar",
        "El mercado cumple mis condiciones",
        "Estoy dispuesto a cerrar sesión aunque pierda"
    ],

    "H4_EJECUCION_CONTROLADA_REGLAS_DURANTE_SESION": [
        "Operé solo Setups permitidos (A / B / C)",
        "Respeté el riesgo diario máximo",
        "Operé dentro del horario definido",
        "No improvisé operaciones",
        "No intenté recuperar pérdidas"
    ],

    "H5_CIERRE_DE_SESION_OBLIGATORIO": [
        "Cerré la plataforma al finalizar la sesión",
        "No hice overtrading",
        "No abrí operaciones tardías",
        "No revisé el mercado después de cerrar"
    ],

    "H6_EVALUACION_DIARIA_NO_MONETARIA": [
        "Seguí el proceso correctamente",
        "Respeté todas mis reglas",
        "Mantuve control emocional durante la sesión"
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
def save_tasks(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_tasks():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _new_task(text: str, done: bool = False, notes: str = "", priority: str = "Media", due=None):
    """Crea una tarea con ID único estable (evita reuso de keys al borrar)."""
    return {
        "id": uuid4().hex,
        "text": text,
        "done": done,
        "notes": notes,
        "priority": priority,
        "due": due
    }

def build_default_structure():
    data = {}
    for cat, tasks in DEFAULT_TASKS.items():
        data[cat] = []
        for t in tasks:
            data[cat].append(_new_task(t))
    return data

def normalize_tasks(data):
    """
    Migración automática:
    - Si una tarea viene como string -> dict.
    - Si falta 'id' -> genera uuid4.
    - Asegura llaves obligatorias.
    """
    if not isinstance(data, dict):
        return build_default_structure()

    for cat, tasks in data.items():
        if not isinstance(tasks, list):
            data[cat] = []
            continue

        normalized_list = []
        for task in tasks:
            if isinstance(task, str):
                task = _new_task(task)

            if not isinstance(task, dict):
                continue

            if not task.get("id"):
                task["id"] = uuid4().hex

            task.setdefault("text", "")
            task.setdefault("done", False)
            task.setdefault("notes", "")
            task.setdefault("priority", "Media")
            task.setdefault("due", None)

            normalized_list.append(task)

        data[cat] = normalized_list

    return data

# =========================
# INIT (CLAVE)
# =========================
if "tasks" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.tasks = normalize_tasks(load_tasks())
        # Persistir IDs inmediatamente (migración)
        save_tasks(st.session_state.tasks)
    else:
        st.session_state.tasks = build_default_structure()
        save_tasks(st.session_state.tasks)

# =========================
# UI
# =========================
st.title("📊 Dashboard de Tareas y Metas")

modo_edicion = st.toggle("✏️ Modo edición", value=False)

for category, tasks in st.session_state.tasks.items():
    st.subheader(category)

    for idx, task in enumerate(tasks):
        task_id = task["id"]  # ✅ ID estable

        cols = st.columns([0.05, 0.4, 0.15, 0.15, 0.2, 0.05])

        with cols[0]:
            task["done"] = st.checkbox(
                "done",
                value=task["done"],
                key=f"{category}_{task_id}_done",
                label_visibility="collapsed"
            )

        with cols[1]:
            if modo_edicion:
                task["text"] = st.text_input(
                    "text",
                    task["text"],
                    key=f"{category}_{task_id}_text",
                    label_visibility="collapsed"
                )
            else:
                st.write(task["text"])

        with cols[2]:
            if modo_edicion:
                opciones = ["Alta", "Media", "Baja"]
                current = task.get("priority", "Media")
                if current not in opciones:
                    current = "Media"

                task["priority"] = st.selectbox(
                    "prio",
                    opciones,
                    index=opciones.index(current),
                    key=f"{category}_{task_id}_prio",
                    label_visibility="collapsed"
                )
            else:
                st.write(task["priority"])

        with cols[3]:
            if modo_edicion:
                fecha = date.fromisoformat(task["due"]) if task["due"] else None
                new_date = st.date_input(
                    "due",
                    value=fecha,
                    key=f"{category}_{task_id}_due",
                    label_visibility="collapsed"
                )
                task["due"] = new_date.isoformat() if new_date else None
            else:
                st.write(task["due"] or "")

        with cols[4]:
            if modo_edicion:
                task["notes"] = st.text_area(
                    "notes",
                    task["notes"],
                    key=f"{category}_{task_id}_notes",
                    label_visibility="collapsed"
                )
            else:
                if task["notes"]:
                    st.caption(task["notes"])

        with cols[5]:
            if modo_edicion:
                if st.button("🗑️", key=f"{category}_{task_id}_del"):
                    tasks.pop(idx)
                    save_tasks(st.session_state.tasks)
                    st.rerun()

    if modo_edicion:
        if st.button(f"➕ Añadir tarea en {category}", key=f"add_{category}"):
            tasks.append(_new_task("Nueva tarea"))
            save_tasks(st.session_state.tasks)
            st.rerun()

    st.divider()

# Guardar al final (persistencia)
save_tasks(st.session_state.tasks)
