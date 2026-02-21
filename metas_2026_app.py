import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "metas_2026.db"
TABLE = "metas_2026"

# -----------------------
# Datos base (seed)
# -----------------------
SEED_ROWS = [
    # Operación / Producción
    ("Producción", "Informe diario 100% automatizado", "Q1: Dashboard operativo completo", "% informes sin captura manual", "Q1", 0.0, 100.0),
    ("Producción", "Consumo estable por tonelada", "Q2: rangos definidos por mezcla", "gal diésel / ton", "Q2", 0.0, 0.0),
    ("Producción", "Cero quiebres operativos", "Q3: alertas automáticas", "# días con paradas", "Q3", 0.0, 0.0),
    ("Producción", "Producción trazable", "Q4: historial auditable", "% días con data completa", "Q4", 0.0, 100.0),

    # Diésel
    ("Diésel", "Control 100% por flujo", "Q1: Recepción → Hyundai → Equipos", "Diferencia (gal)", "Q1", 0.0, 0.0),
    ("Diésel", "Reducir pérdidas", "Q2: análisis mensual", "% variación mensual", "Q2", 0.0, 0.0),
    ("Diésel", "Consumo por equipo", "Q3: ranking equipos", "gal / hora / equipo", "Q3", 0.0, 0.0),
    ("Diésel", "Auditoría automática", "Q4: ajustes documentados", "# ajustes manuales", "Q4", 0.0, 0.0),

    # AC30
    ("AC30", "Control por tanque y proveedor", "Q1: registros centralizados", "gal reales vs teóricos", "Q1", 0.0, 0.0),
    ("AC30", "Consumo según diseño", "Q2: desviación < ±3%", "% desviación", "Q2", 0.0, 3.0),
    ("AC30", "Proyección inventario", "Q3: días de operación", "días disponibles", "Q3", 0.0, 0.0),
    ("AC30", "Cero quiebres", "Q4: alertas anticipadas", "# quiebres", "Q4", 0.0, 0.0),

    # Calidad
    ("Calidad", "Cumplimiento de diseños", "Q1: checklist digital", "% cumplimiento", "Q1", 0.0, 100.0),
    ("Calidad", "Reducir reprocesos", "Q2: análisis causas", "# reprocesos", "Q2", 0.0, 0.0),
    ("Calidad", "Integración producción", "Q3: dashboard conjunto", "% muestras válidas", "Q3", 0.0, 100.0),
    ("Calidad", "Mejora continua", "Q4: reporte trimestral", "desviación promedio", "Q4", 0.0, 0.0),

    # Automatización / Tecnología
    ("Tecnología", "Dashboard único", "Q1: Opción B completa", "módulos activos", "Q1", 0.0, 0.0),
    ("Tecnología", "DB centralizada", "Q2: API Flask", "errores API / mes", "Q2", 0.0, 0.0),
    ("Tecnología", "Tickets automáticos", "Q3: 80% OCR", "% OCR exitoso", "Q3", 0.0, 80.0),
    ("Tecnología", "Backup automático", "Q4: validación mensual", "% backups OK", "Q4", 0.0, 100.0),

    # Costos
    ("Costos", "Costo real por ton", "Q1: cálculo integrado", "$ / ton", "Q1", 0.0, 0.0),
    ("Costos", "Comparador proveedores", "Q2: ranking automático", "ahorro potencial", "Q2", 0.0, 0.0),
    ("Costos", "Mejora margen", "Q3: mezcla rentable", "margen %", "Q3", 0.0, 0.0),
    ("Costos", "Reducción anual", "Q4: objetivo logrado", "% reducción", "Q4", 0.0, 0.0),

    # Negocios paralelos
    ("Expansión", "Planta piloto (emulsiones)", "Q1: costos definidos", "$ / ton", "Q1", 0.0, 0.0),
    ("Expansión", "Producción estable (modificado)", "Q2: batch controlado", "rendimiento", "Q2", 0.0, 0.0),
    ("Expansión", "Proyecto solar", "Q3: ROI calculado", "meses payback", "Q3", 0.0, 0.0),
    ("Expansión", "Reducción energía", "Q4: impacto medido", "% ahorro", "Q4", 0.0, 0.0),

    # Finanzas / Trading
    ("Finanzas", "Consistencia trading", "Q1: diario activo", "% trades plan", "Q1", 0.0, 0.0),
    ("Finanzas", "Control emocional", "Q2: checklist diario", "violaciones", "Q2", 0.0, 0.0),
    ("Finanzas", "Plan inversión largo plazo", "Q3: cartera definida", "CAGR", "Q3", 0.0, 0.0),
    ("Finanzas", "Crecimiento neto", "Q4: patrimonio", "$ acumulado", "Q4", 0.0, 0.0),

    # NestVault
    ("NestVault", "MVP funcional", "Q1: flujo completo", "módulos listos", "Q1", 0.0, 0.0),
    ("NestVault", "Marco legal", "Q2: contratos base", "estado validación", "Q2", 0.0, 0.0),
    ("NestVault", "UI operativa", "Q3: usuarios piloto", "usuarios", "Q3", 0.0, 0.0),
    ("NestVault", "Lanzamiento", "Q4: MVP público", "estado", "Q4", 0.0, 1.0),
]

# -----------------------
# DB helpers
# -----------------------
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT NOT NULL,
                meta_anual TEXT NOT NULL,
                meta_trimestral TEXT NOT NULL,
                kpi TEXT NOT NULL,
                trimestre TEXT NOT NULL,
                valor_actual REAL NOT NULL DEFAULT 0,
                objetivo REAL NOT NULL DEFAULT 0,
                nota TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            )
            """
        )
        # seed si está vacío
        cur = conn.execute(f"SELECT COUNT(*) FROM {TABLE}")
        n = cur.fetchone()[0]
        if n == 0:
            conn.executemany(
                f"""
                INSERT INTO {TABLE}
                (area, meta_anual, meta_trimestral, kpi, trimestre, valor_actual, objetivo, nota, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, '', ?)
                """,
                [(a, ma, mt, k, t, va, obj, datetime.now().isoformat()) for (a, ma, mt, k, t, va, obj) in SEED_ROWS]
            )

def load_rows(area=None, trimestre=None):
    q = f"SELECT * FROM {TABLE} WHERE 1=1"
    params = []
    if area and area != "Todas":
        q += " AND area = ?"
        params.append(area)
    if trimestre and trimestre != "Todos":
        q += " AND trimestre = ?"
        params.append(trimestre)
    q += " ORDER BY area, trimestre, id"
    with get_conn() as conn:
        df = pd.read_sql_query(q, conn, params=params)
    return df

def save_rows(df: pd.DataFrame):
    now = datetime.now().isoformat()
    with get_conn() as conn:
        for _, r in df.iterrows():
            conn.execute(
                f"""
                UPDATE {TABLE}
                SET area = ?,
                    meta_anual = ?,
                    meta_trimestral = ?,
                    kpi = ?,
                    trimestre = ?,
                    valor_actual = ?,
                    objetivo = ?,
                    nota = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    str(r["area"]),
                    str(r["meta_anual"]),
                    str(r["meta_trimestral"]),
                    str(r["kpi"]),
                    str(r["trimestre"]),
                    float(r["valor_actual"]) if r["valor_actual"] != "" else 0.0,
                    float(r["objetivo"]) if r["objetivo"] != "" else 0.0,
                    str(r.get("nota", "")),
                    now,
                    int(r["id"]),
                )
            )
        conn.commit()

# -----------------------
# KPI logic (estado)
# -----------------------
def calc_progress_and_status(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    def pct(row):
        obj = float(row["objetivo"])
        val = float(row["valor_actual"])
        if obj == 0:
            return None
        return (val / obj) * 100.0

    out["progreso_%"] = out.apply(lambda r: pct(r), axis=1)

    def status(row):
        p = row["progreso_%"]
        if p is None or pd.isna(p):
            return "⚪ Sin objetivo"
        if p >= 100:
            return "🟢 En meta"
        if p >= 80:
            return "🟡 En riesgo"
        return "🔴 Crítico"

    out["estado"] = out.apply(status, axis=1)
    return out

# -----------------------
# UI
# -----------------------
st.set_page_config(page_title="Metas 2026", layout="wide")
st.title("🎯 Metas 2026 – Anual / Trimestral / KPI")

init_db()

# Sidebar filtros
with st.sidebar:
    st.header("Filtros")
    areas = ["Todas"]
    with get_conn() as conn:
        areas_db = [r[0] for r in conn.execute(f"SELECT DISTINCT area FROM {TABLE} ORDER BY area").fetchall()]
    areas += areas_db

    area_sel = st.selectbox("Área", areas, index=0)
    tri_sel = st.selectbox("Trimestre", ["Todos", "Q1", "Q2", "Q3", "Q4"], index=0)

    st.divider()
    st.caption("Estados")
    st.write("🟢 En meta")
    st.write("🟡 En riesgo (80–99%)")
    st.write("🔴 Crítico (<80%)")
    st.write("⚪ Sin objetivo (objetivo=0)")

df = load_rows(area=area_sel, trimestre=tri_sel)
df_view = calc_progress_and_status(df)

# Resumen superior
c1, c2, c3, c4 = st.columns(4)
total = len(df_view)
en_meta = (df_view["estado"] == "🟢 En meta").sum()
en_riesgo = (df_view["estado"] == "🟡 En riesgo").sum()
critico = (df_view["estado"] == "🔴 Crítico").sum()

c1.metric("Total metas", f"{total}")
c2.metric("🟢 En meta", f"{en_meta}")
c3.metric("🟡 En riesgo", f"{en_riesgo}")
c4.metric("🔴 Crítico", f"{critico}")

st.divider()
st.subheader("📋 Tabla editable")

# Columnas editables
editable_cols = ["id", "area", "meta_anual", "meta_trimestral", "kpi", "trimestre", "valor_actual", "objetivo", "nota"]
df_edit = df_view[editable_cols].copy()

edited = st.data_editor(
    df_edit,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "area": st.column_config.TextColumn("Área"),
        "meta_anual": st.column_config.TextColumn("Meta anual"),
        "meta_trimestral": st.column_config.TextColumn("Meta trimestral"),
        "kpi": st.column_config.TextColumn("KPI"),
        "trimestre": st.column_config.SelectboxColumn("Trimestre", options=["Q1", "Q2", "Q3", "Q4"]),
        "valor_actual": st.column_config.NumberColumn("Valor actual", step=1.0),
        "objetivo": st.column_config.NumberColumn("Objetivo", step=1.0),
        "nota": st.column_config.TextColumn("Nota"),
    },
    key="editor_metas_2026"
)

# Botones de acciones
a1, a2, a3 = st.columns([1, 1, 2])
with a1:
    if st.button("💾 Guardar cambios", type="primary"):
        try:
            # Si el usuario agregó filas nuevas (id vacío), las insertamos
            new_rows = edited[edited["id"].isna()] if "id" in edited.columns else pd.DataFrame()
            existing = edited[~edited["id"].isna()].copy()

            # Guardar existentes
            if len(existing) > 0:
                save_rows(existing)

            # Insertar nuevas
            if len(new_rows) > 0:
                now = datetime.now().isoformat()
                with get_conn() as conn:
                    for _, r in new_rows.iterrows():
                        conn.execute(
                            f"""
                            INSERT INTO {TABLE}
                            (area, meta_anual, meta_trimestral, kpi, trimestre, valor_actual, objetivo, nota, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                str(r.get("area", "")),
                                str(r.get("meta_anual", "")),
                                str(r.get("meta_trimestral", "")),
                                str(r.get("kpi", "")),
                                str(r.get("trimestre", "Q1")),
                                float(r.get("valor_actual", 0) or 0),
                                float(r.get("objetivo", 0) or 0),
                                str(r.get("nota", "")),
                                now,
                            )
                        )
                    conn.commit()

            st.success("Cambios guardados.")
            st.rerun()
        except Exception as e:
            st.error(f"Error guardando: {e}")

with a2:
    if st.button("🔄 Recargar"):
        st.rerun()

with a3:
    # Exportar lo que se ve
    export_df = calc_progress_and_status(load_rows(area=area_sel, trimestre=tri_sel))
    csv = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar CSV (lo filtrado)",
        data=csv,
        file_name=f"metas_2026_{area_sel}_{tri_sel}.csv".replace(" ", "_"),
        mime="text/csv"
    )

st.divider()
st.subheader("📈 Vista de progreso (rápida)")

view_cols = ["area", "trimestre", "kpi", "valor_actual", "objetivo", "progreso_%", "estado", "updated_at"]
st.dataframe(df_view[view_cols], use_container_width=True)

# Agregado por área (promedio de progreso donde hay objetivo)
df_prog = df_view.dropna(subset=["progreso_%"]).copy()
if len(df_prog) > 0:
    agg = (
        df_prog.groupby("area", as_index=False)["progreso_%"]
        .mean()
        .sort_values("progreso_%", ascending=False)
    )
    st.caption("Promedio de progreso por área (solo metas con objetivo > 0).")
    st.bar_chart(agg.set_index("area")["progreso_%"])
else:
    st.info("Aún no hay metas con objetivo definido (objetivo > 0). Define objetivos para activar el progreso.")
