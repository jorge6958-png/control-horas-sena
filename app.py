import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    parsear_pdf, procesar_reporte, asignar_competencias,
    construir_tabla_competencias, construir_tabla_instructores,
    RUTA_PDF_DEFAULT, NOMBRES_LIMPIEZA
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
    st.header("📂 Cargar archivos")

    pdf_file = st.file_uploader("PDF del programa de formación", type=["pdf"])
    xls_file = st.file_uploader("Reporte XLS / CSV", type=["xls", "xlsx", "csv"])

    usar_pdf_default = st.checkbox(
        "Usar PDF precargado",
        value=os.path.exists(RUTA_PDF_DEFAULT)
    )

    procesar = st.button("🔍 Procesar", type="primary")

# ─── PROCESAMIENTO ─────────────────────────────────────────
if not procesar:
    st.info(
        "\U0001f448 Carga un **PDF del programa de formación** y un **reporte XLS/CSV** "
        "en el panel lateral, luego haz clic en **Procesar**."
    )
    st.stop()

if pdf_file:
    pdf_path = os.path.join("/tmp", pdf_file.name)
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    df_pdf = parsear_pdf(pdf_path)
    st.sidebar.success(f"✅ PDF cargado: {pdf_file.name}")
elif usar_pdf_default and os.path.exists(RUTA_PDF_DEFAULT):
    df_pdf = parsear_pdf(RUTA_PDF_DEFAULT)
    st.sidebar.success("✅ PDF precargado")
else:
    st.error("Carga un PDF del programa de formación o activa el precargado.")
    st.stop()

if xls_file:
    xls_path = os.path.join("/tmp", xls_file.name)
    with open(xls_path, "wb") as f:
        f.write(xls_file.getbuffer())
    df_detalle, info_ficha = procesar_reporte(xls_path)
    st.sidebar.success(f"✅ Reporte cargado: {xls_file.name}")
else:
    st.error("Carga un reporte XLS/CSV.")
    st.stop()

df_detalle = asignar_competencias(df_detalle, df_pdf)
df_comp = construir_tabla_competencias(df_detalle, df_pdf)
df_instr = construir_tabla_instructores(df_detalle)

# ─── INFO DE LA FICHA ────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Código Ficha", info_ficha.get("Código Ficha", "—"))
with col2:
    st.metric("Programa", info_ficha.get("Nombre Programa", "—"))
with col3:
    st.metric("Centro", info_ficha.get("Centro", "—"))
with col4:
    st.metric("Municipio", info_ficha.get("Municipio", "—"))

st.markdown("---")

# ─── INDICADOR GENERAL ────────────────────────────────────
total_plan = df_comp["horas_planeadas"].sum()
total_rep = df_comp["horas_reportadas"].sum()
total_sin_etapa = df_comp[
    ~df_comp["competencia"].str.contains("ETAPA PRÁCTICA", case=False)
]
plan_sin_etapa = total_sin_etapa["horas_planeadas"].sum()
rep_sin_etapa = total_sin_etapa["horas_reportadas"].sum()
pct_sin_etapa = (rep_sin_etapa / plan_sin_etapa * 100) if plan_sin_etapa > 0 else 0
pct_general = (total_rep / total_plan * 100) if total_plan > 0 else 0

col_a, col_b, col_c, col_d = st.columns(4)

delta_pct = pct_sin_etapa - 100
with col_a:
    st.markdown(
        f"""
        <div style="text-align:center;padding:20px;background:#f0f2f6;border-radius:10px">
            <h1 style="font-size:3em;margin:0">{pct_sin_etapa:.1f}%</h1>
            <p style="font-size:0.9em;color:#555">Ejecución (sin Etapa Práctica)</p>
            <p style="font-size:1.1em">{rep_sin_etapa:,}h / {plan_sin_etapa:,}h</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_b:
    st.markdown(
        f"""
        <div style="text-align:center;padding:20px;background:#e8f5e9;border-radius:10px">
            <h1 style="font-size:3em;margin:0;color:#2e7d32">{pct_general:.1f}%</h1>
            <p style="font-size:0.9em;color:#555">Ejecución General</p>
            <p style="font-size:1.1em">{total_rep:,}h / {total_plan:,}h</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_c:
    faltantes = total_plan - total_rep
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

df_display = df_comp.copy()
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
    ~df_comp["competencia"].str.contains("ETAPA PRÁCTICA", case=False)
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

completas = len(df_comp[df_comp["porcentaje"] >= 100])
incompletas = len(df_comp[(df_comp["porcentaje"] > 0) & (df_comp["porcentaje"] < 100)])
sin_reporte = len(df_comp[df_comp["porcentaje"] == 0])

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

competencias_incompletas = df_comp[
    (df_comp["porcentaje"] > 0) & (df_comp["porcentaje"] < 100)
]
for _, row in competencias_incompletas.iterrows():
    faltan = int(row["horas_planeadas"] - row["horas_reportadas"])
    alertas.append(
        f"**{row['nombre_limpio']}** — "
        f"{row['porcentaje']:.1f}% ejecutado, faltan {faltan}h"
    )

competencias_sin_reporte = df_comp[
    (df_comp["porcentaje"] == 0) & (~df_comp["competencia"].str.contains("ETAPA PRÁCTICA", case=False))
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
    f"📊 Reporte procesado: {xls_file.name} | "
    f"{len(df_comp)} competencias, "
    f"{total_instructores} instructores"
)
