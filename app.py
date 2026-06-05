import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    cargar_competencias, detectar_programa,
    procesar_reporte, asignar_competencias,
    construir_tabla_competencias, construir_tabla_instructores
)
import os

st.set_page_config(
    page_title="Control de Horas - SENA",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Control de Horas - Programas de Formación SENA")
st.markdown("---")

# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.subheader("📂 Cargar archivos")

    xls_file = st.file_uploader(
        "Reporte de Instructores por Ficha (XLS/CSV)",
        type=["xls", "xlsx", "csv"],
    )

    procesar = st.button("🔍 Procesar", type="primary")

# ─── VALIDACIÓN ────────────────────────────────────────────
if not procesar:
    st.info(
        "Carga el reporte de instructores y haz clic en **Procesar**."
    )
    st.stop()

if not xls_file:
    st.error("Carga el reporte de instructores.")
    st.stop()

# ─── PROCESAR REPORTE ─────────────────────────────────────
with st.spinner("Procesando reporte de instructores..."):
    xls_path = os.path.join("/tmp", xls_file.name)
    with open(xls_path, "wb") as f:
        f.write(xls_file.getbuffer())
    df_detalle, info_ficha = procesar_reporte(xls_path)

if "Nombre Programa" not in info_ficha or not info_ficha["Nombre Programa"]:
    st.error("El reporte no contiene el nombre del programa.")
    st.stop()

try:
    programa = detectar_programa(info_ficha["Nombre Programa"])
except ValueError as e:
    st.error(str(e))
    st.stop()

df_competencias = cargar_competencias(programa)

with st.spinner("Procesando reporte de instructores..."):
    df_detalle = asignar_competencias(df_detalle, df_competencias)
    df_comp = construir_tabla_competencias(df_detalle, df_competencias)
    df_instr = construir_tabla_instructores(df_detalle)

st.sidebar.success(f"✅ Programa: {programa}")
st.sidebar.success(f"✅ Reporte: {xls_file.name}")

# ─── INFO DE LA FICHA ────────────────────────────────────
ficha_info = [
    ("Código Ficha", info_ficha.get("Código Ficha", "—")),
    ("Programa", info_ficha.get("Nombre Programa", programa)),
    ("Municipio", info_ficha.get("Municipio", "—")),
]
cols = st.columns(3)
for col, (label, value) in zip(cols, ficha_info):
    col.markdown(
        f"<p style='margin:0;font-size:0.75em;color:#555'>{label}</p>"
        f"<p style='margin:0;font-size:0.95em;font-weight:600;word-break:break-word'>{value}</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─── INDICADOR GENERAL ────────────────────────────────────
df_comp_lectiva = df_comp[
    ~df_comp["nombre"].str.contains("ETAPA PRÁCTICA", case=False)
]
plan_total = df_comp_lectiva["horas_planeadas"].sum()
rep_total = df_comp_lectiva["horas_reportadas"].sum()
pct_ejecucion = (rep_total / plan_total * 100) if plan_total > 0 else 0

col_a, col_c, col_d = st.columns(3)
with col_a:
    st.markdown(
        f"""
        <div style="text-align:center;padding:20px;background:#f0f2f6;border-radius:10px">
            <h1 style="font-size:3em;margin:0">{pct_ejecucion:.1f}%</h1>
            <p style="font-size:0.9em;color:#555">Ejecución Lectiva</p>
            <p style="font-size:1.1em">{rep_total:,}h / {plan_total:,}h</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_c:
    faltantes = plan_total - rep_total
    st.markdown(
        f"""
        <div style="text-align:center;padding:20px;background:#fff3e0;border-radius:10px">
            <h1 style="font-size:2.5em;margin:0;color:#e65100">{faltantes:,}h</h1>
            <p style="font-size:0.9em;color:#555">Horas pendientes</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_d:
    total_instructores = df_instr["instructor"].nunique() if not df_instr.empty else 0
    activos = df_instr[df_instr["estado"] == "Activo"]["instructor"].nunique() if not df_instr.empty else 0
    st.markdown(
        f"""
        <div style="text-align:center;padding:20px;background:#e3f2fd;border-radius:10px">
            <h1 style="font-size:2.5em;margin:0;color:#1565c0">{total_instructores}</h1>
            <p style="font-size:0.9em;color:#555">Instructores ({activos} activos)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─── TABLA POR COMPETENCIA ────────────────────────────────
st.subheader("📋 Horas por competencia")

df_display = df_comp_lectiva.copy()
df_display["competencia"] = df_display["nombre_limpio"]
df_display["planeadas"] = df_display["horas_planeadas"].astype(int)
df_display["reportadas"] = df_display["horas_reportadas"].astype(int)
df_display["diferencia"] = df_display["diferencia"].astype(int)
df_display["% ejec."] = df_display["porcentaje"].apply(lambda x: f"{x:.1f}%")
df_display["Estado"] = df_display["porcentaje"].apply(
    lambda x: "✅ Completa" if x >= 100 else ("⚠️ Incompleta" if x > 0 else "🔴 Sin reporte")
)

tabla_comp = df_display[[
    "competencia", "planeadas", "reportadas",
    "diferencia", "% ejec.", "Estado", "instructores_detalle"
]].rename(columns={
    "competencia": "Competencia",
    "planeadas": "Planeadas",
    "reportadas": "Reportadas",
    "diferencia": "Diferencia",
    "instructores_detalle": "Instructores",
})

st.dataframe(
    tabla_comp,
    use_container_width=True,
    column_config={
        "Diferencia": st.column_config.NumberColumn(
            "Diferencia", format="+%d"
        ),
    },
    hide_index=True,
)

# ─── GRÁFICO: Planeado vs Reportado ──────────────────────
st.subheader("📈 Comparativo planeado vs reportado")

df_chart = df_comp[
    ~df_comp["nombre"].str.contains("ETAPA PRÁCTICA", case=False)
].copy()
df_chart["competencia_display"] = df_chart["nombre_limpio"]
df_chart = df_chart.sort_values("horas_planeadas", ascending=True)

fig = go.Figure()
fig.add_trace(go.Bar(
    y=df_chart["competencia_display"],
    x=df_chart["horas_planeadas"],
    name="Planeadas",
    orientation="h",
    marker_color="#1f77b4",
    text=df_chart["horas_planeadas"].astype(int),
    textposition="outside",
))
fig.add_trace(go.Bar(
    y=df_chart["competencia_display"],
    x=df_chart["horas_reportadas"],
    name="Reportadas",
    orientation="h",
    marker_color="#ff7f0e",
    text=df_chart["horas_reportadas"].astype(int),
    textposition="outside",
))

fig.update_layout(
    barmode="group",
    height=max(400, len(df_chart) * 30),
    xaxis_title="Horas",
    yaxis_title="",
    margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig, use_container_width=True)

# ─── GRÁFICO DE PASTEL: Ejecución general ─────────────────
st.subheader("🎯 Distribución de ejecución")

completas = len(df_comp_lectiva[df_comp_lectiva["porcentaje"] >= 100])
incompletas = len(df_comp_lectiva[(df_comp_lectiva["porcentaje"] > 0) & (df_comp_lectiva["porcentaje"] < 100)])
sin_reporte = len(df_comp_lectiva[df_comp_lectiva["porcentaje"] == 0])

fig_pie = go.Figure(data=[go.Pie(
    labels=["Completas (≥100%)", "Incompletas (>0%)", "Sin reporte (0%)"],
    values=[completas, incompletas, sin_reporte],
    marker_colors=["#2e7d32", "#e65100", "#bdbdbd"],
    textinfo="label+percent",
)])
fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_pie, use_container_width=True)

# ─── TABLA POR INSTRUCTOR ─────────────────────────────────
st.subheader("👤 Horas por instructor")

if not df_instr.empty:
    df_instr_display = df_instr.copy()
    df_instr_display["total_horas"] = df_instr_display["total_horas"].astype(int)

    st.dataframe(
        df_instr_display[[
            "instructor", "estado", "total_horas", "registros", "competencias"
        ]].rename(columns={
            "instructor": "Instructor",
            "estado": "Estado",
            "total_horas": "Total horas",
            "registros": "Registros",
            "competencias": "Competencias",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No hay datos de instructores.")

# ─── ALERTAS ─────────────────────────────────────────────
st.markdown("---")
st.subheader("⚠️ Alertas")

alertas = []

competencias_incompletas = df_comp_lectiva[
    (df_comp_lectiva["porcentaje"] > 0) & (df_comp_lectiva["porcentaje"] < 100)
]
for _, row in competencias_incompletas.iterrows():
    faltan = int(row["horas_planeadas"] - row["horas_reportadas"])
    alertas.append(
        f"**{row['nombre_limpio']}** — "
        f"{row['porcentaje']:.1f}% ejecutado, faltan {faltan}h"
    )

competencias_sin_reporte = df_comp[
    (df_comp["porcentaje"] == 0) & (~df_comp["nombre"].str.contains("ETAPA PRÁCTICA", case=False))
]
for _, row in competencias_sin_reporte.iterrows():
    alertas.append(
        f"**{row['nombre_limpio']}** — "
        f"{int(row['horas_planeadas'])}h planeadas, **sin reporte**"
    )

instructores_inactivos = df_instr[df_instr["estado"] == "Inactivo"] if not df_instr.empty else pd.DataFrame()
for _, row in instructores_inactivos.iterrows():
    alertas.append(
        f"**{row['instructor']}** — "
        f"Instructor **inactivo** con {int(row['total_horas'])}h reportadas"
    )

if alertas:
    for alerta in alertas:
        st.warning(alerta)
else:
    st.success("No se detectaron alertas. Todo en orden ✅")

# ─── FOOTER ───────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"📊 Programa: {programa} | Reporte: {xls_file.name} | "
    f"{len(df_comp_lectiva)} competencias, "
    f"{total_instructores} instructores"
)
