import os
import re
import pandas as pd
import streamlit as st

RUTA_PDF_DEFAULT = os.path.join(os.path.dirname(__file__), "Diseno_curricular GESTION DE REDES.pdf")

CORRECCIONES_PDF = {}

COMPETENCIAS_ADICIONALES = [
    ("ETAPA PR\u00c1CTICA", 864),
]

NORMALIZACION_COMPETENCIAS = [
    ("administrar hardware y software de seguridad en la red",
     "ADMINISTRACI\u00d3N DE HARDWARE Y SOFTWARE DE SEGURIDAD EN LA RED."),
    ("aplicaci\u00f3n de conocimientos de las ciencias naturales",
     "APLICACI\u00d3N DE CONOCIMIENTOS DE LAS CIENCIAS NATURALES DE ACUERDO CON"),
    ("aplicar pr\u00e1cticas de protecci\u00f3n ambiental, seguridad y salud en el trabajo",
     "APLICAR PR\u00c1CTICAS DE PROTECCI\u00d3N AMBIENTAL, SEGURIDAD Y SALUD EN EL TRABAJO"),
    ("administrar infraestructura tecnol\u00f3gica de red",
     "GESTI\u00d3N DE LA INFRAESTRUCTURA TECNOL\u00d3GICA DE RED."),
    ("configurar dispositivos de c\u00f3mputo",
     "CONFIGURACI\u00d3N DE EQUIPOS DE C\u00d3MPUTO."),
    ("configurar dispositivos activos de interconexi\u00f3n",
     "CONFIGURACI\u00d3N DE DISPOSITIVOS ACTIVOS DE INTERCONEXI\u00d3N."),
    ("desarrollar procesos de comunicaci\u00f3n eficaces y efectivos",
     "FORMA EFICAZ Y EFECTIVA, TENIENDO EN CUENTA SITUACIONES DE"),
    ("ejercer derechos fundamentales del trabajo",
     "Ejercer derechos fundamentales del trabajo en el marco de la constituci\u00f3n pol\u00edtica y los convenios"),
    ("enrique low murtra-interactuar en el contexto productivo y social",
     "INTERACTUAR EN EL CONTEXTO PRODUCTIVO Y SOCIAL DE ACUERDO CON PRINCIPIOS"),
    ("generar h\u00e1bitos saludables",
     "IMPLEMENTAR H\u00c1BITOS SALUDABLES MEDIANTE LA ACTIVIDAD F\u00cdSICA, DE"),
    ("cultura emprendedora y empresarial",
     "EMPLEAR ELEMENTOS DE CULTURA EMPRENDEDORA Y EMPRESARIAL DE"),
    ("interactuar en lengua inglesa",
     "SOCIALES Y LABORALES SEG\u00daN LOS CRITERIOS ESTABLECIDOS POR EL MARCO COM\u00daN"),
    ("implementar red inal\u00e1mbrica local",
     "IMPLEMENTACI\u00d3N DE LA RED INAL\u00c1MBRICA LOCAL."),
    ("implementar tecnolog\u00edas de voz sobre ip",
     "IMPLEMENTACI\u00d3N DE TECNOLOG\u00cdAS DE VOZ SOBRE IP."),
    ("orientar investigaci\u00f3n formativa seg\u00fan referentes t\u00e9cnicos",
     "DESARROLLO DE PROCESOS DE INVESTIGACI\u00d3N EFECTIVOS, TENIENDO EN"),
    ("razonar cuantitativamente frente a situaciones susceptibles",
     "RAZONAR CUANTITATIVAMENTE FRENTE A SITUACIONES SUSCEPTIBLES DE SER"),
    ("resultado de aprendizaje de la inducci\u00f3n",
     "RESULTADO DE APRENDIZAJE DE LA INDUCCI\u00d3N."),
    ("utilizar herramientas inform\u00e1ticas",
     "APLICACI\u00d3N DE TECNOLOG\u00cdAS DE LA INFORMACI\u00d3N Y LA COMUNICACI\u00d3N"),
]

NOMBRES_LIMPIEZA = {
    "ADMINISTRACI\u00d3N DE HARDWARE Y SOFTWARE DE SEGURIDAD EN LA RED.": "Seguridad en la red",
    "APLICACI\u00d3N DE CONOCIMIENTOS DE LAS CIENCIAS NATURALES DE ACUERDO CON": "Ciencias naturales",
    "APLICAR PR\u00c1CTICAS DE PROTECCI\u00d3N AMBIENTAL, SEGURIDAD Y SALUD EN EL TRABAJO": "Protecci\u00f3n salud y ambiente",
    "GESTI\u00d3N DE LA INFRAESTRUCTURA TECNOL\u00d3GICA DE RED.": "Gesti\u00f3n infraestructura de red",
    "CONFIGURACI\u00d3N DE EQUIPOS DE C\u00d3MPUTO.": "Configuraci\u00f3n equipos de c\u00f3mputo",
    "CONFIGURACI\u00d3N DE DISPOSITIVOS ACTIVOS DE INTERCONEXI\u00d3N.": "Configuraci\u00f3n dispositivos activos",
    "FORMA EFICAZ Y EFECTIVA, TENIENDO EN CUENTA SITUACIONES DE": "Comunicaci\u00f3n",
    "Ejercer derechos fundamentales del trabajo en el marco de la constituci\u00f3n pol\u00edtica y los convenios": "Derechos fundamentales",
    "INTERACTUAR EN EL CONTEXTO PRODUCTIVO Y SOCIAL DE ACUERDO CON PRINCIPIOS": "\u00c9tica / Cultura de paz",
    "IMPLEMENTAR H\u00c1BITOS SALUDABLES MEDIANTE LA ACTIVIDAD F\u00cdSICA, DE": "Actividad f\u00edsica",
    "EMPLEAR ELEMENTOS DE CULTURA EMPRENDEDORA Y EMPRESARIAL DE": "Cultura emprendedora",
    "SOCIALES Y LABORALES SEG\u00daN LOS CRITERIOS ESTABLECIDOS POR EL MARCO COM\u00daN": "Ingl\u00e9s",
    "IMPLEMENTACI\u00d3N DE LA RED INAL\u00c1MBRICA LOCAL.": "Red inal\u00e1mbrica local",
    "IMPLEMENTACI\u00d3N DE TECNOLOG\u00cdAS DE VOZ SOBRE IP.": "Voz sobre IP",
    "DESARROLLO DE PROCESOS DE INVESTIGACI\u00d3N EFECTIVOS, TENIENDO EN": "Investigaci\u00f3n",
    "RAZONAR CUANTITATIVAMENTE FRENTE A SITUACIONES SUSCEPTIBLES DE SER": "Matem\u00e1ticas",
    "RESULTADO DE APRENDIZAJE DE LA INDUCCI\u00d3N.": "Inducci\u00f3n",
    "APLICACI\u00d3N DE TECNOLOG\u00cdAS DE LA INFORMACI\u00d3N Y LA COMUNICACI\u00d3N": "TIC",
    "ETAPA PR\u00c1CTICA": "Etapa Pr\u00e1ctica",
}


def parsear_pdf(ruta_pdf):
    import pdfplumber

    with pdfplumber.open(ruta_pdf) as pdf:
        text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    lines = text.split("\n")

    competencies = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if "4.3 NOMBRE DE LA" in line:
            rest = line[line.index("4.3 NOMBRE DE LA") + len("4.3 NOMBRE DE LA"):].strip()
            name_parts = []

            if rest and "COMPETENCIA" not in rest.upper() and len(rest) > 3:
                name_parts.append(rest)

            j = i + 1
            while j < len(lines):
                lj = lines[j].strip()
                if lj.upper().strip() == "COMPETENCIA":
                    j += 1
                    break
                if re.match(r"4\.[1-5]", lj):
                    break
                if lj and not lj.upper().startswith("COMPETENCIA"):
                    name_parts.append(lj)
                j += 1

            comp_name = " ".join(name_parts).strip()
            comp_name = comp_name.replace("\ufffd", "").strip()

            if comp_name in CORRECCIONES_PDF:
                comp_name = CORRECCIONES_PDF[comp_name]

            for k in range(j, min(j + 15, len(lines))):
                lk = lines[k].strip()
                if "4.4 DURACI\u00d3N M\u00c1XIMA" in lk:
                    for offset in range(0, 4):
                        if k + offset < len(lines):
                            match = re.search(r"(\d+)\s*horas?", lines[k + offset].strip(), re.IGNORECASE)
                            if match:
                                hours = int(match.group(1))
                                if comp_name and len(comp_name) >= 3:
                                    competencies.append((comp_name, hours))
                                break
                    break

            i = j

        i += 1

    for name, hours in COMPETENCIAS_ADICIONALES:
        competencies.append((name, hours))

    df = pd.DataFrame(
        [
            {"competencia": c[0].rstrip("."), "horas_planeadas": c[1]}
            for c in competencies
        ]
    )
    return df


def procesar_reporte(ruta_archivo):
    ext = os.path.splitext(ruta_archivo)[1].lower()

    if ext in (".xls",):
        import xlrd
        wb = xlrd.open_workbook(ruta_archivo)
        sheet = wb.sheet_by_index(0)

        info_ficha = {}
        for i in range(1, min(8, sheet.nrows)):
            label = str(sheet.cell_value(i, 0)).strip()
            raw = sheet.cell_value(i, 1) if sheet.ncols > 1 else ""
            if isinstance(raw, float) and raw == int(raw):
                raw = int(raw)
            valor = str(raw).strip()
            if label and valor:
                info_ficha[label] = valor

        filas = []
        for i in range(11, sheet.nrows):
            nombre = str(sheet.cell_value(i, 0)).strip()
            apellido = str(sheet.cell_value(i, 1)).strip()
            estado = str(sheet.cell_value(i, 2)).strip()
            competencia = str(sheet.cell_value(i, 3)).strip()
            fecha_ini = str(sheet.cell_value(i, 4)).strip()
            fecha_fin = str(sheet.cell_value(i, 5)).strip()
            horas_str = str(sheet.cell_value(i, 6)).strip()

            if not nombre or not competencia:
                continue

            try:
                horas = round(float(horas_str)) if horas_str else 0
            except ValueError:
                horas = 0

            filas.append({
                "nombre": nombre,
                "apellido": apellido,
                "instructor": f"{nombre} {apellido}",
                "estado": estado,
                "competencia_xls": competencia,
                "fecha_inicio": fecha_ini,
                "fecha_fin": fecha_fin,
                "horas": horas,
            })

    elif ext in (".xlsx",):
        import openpyxl
        wb = openpyxl.load_workbook(ruta_archivo, read_only=True, data_only=True)
        ws = wb.active

        info_ficha = {}
        for i in range(1, min(8, ws.max_row + 1)):
            c0 = str(ws.cell(i, 1).value or "").strip()
            raw = ws.cell(i, 2).value
            if isinstance(raw, float) and raw == int(raw):
                raw = int(raw)
            c1 = str(raw or "").strip()
            if c0 and c1:
                info_ficha[c0] = c1

        filas = []
        for i in range(11, ws.max_row + 1):
            nombre = str(ws.cell(i, 1).value or "").strip()
            apellido = str(ws.cell(i, 2).value or "").strip()
            estado = str(ws.cell(i, 3).value or "").strip()
            competencia = str(ws.cell(i, 4).value or "").strip()
            fecha_ini = str(ws.cell(i, 5).value or "").strip()
            fecha_fin = str(ws.cell(i, 6).value or "").strip()
            horas_str = str(ws.cell(i, 7).value or "").strip()

            if not nombre or not competencia:
                continue

            try:
                horas = round(float(horas_str)) if horas_str else 0
            except ValueError:
                horas = 0

            filas.append({
                "nombre": nombre,
                "apellido": apellido,
                "instructor": f"{nombre} {apellido}",
                "estado": estado,
                "competencia_xls": competencia,
                "fecha_inicio": fecha_ini,
                "fecha_fin": fecha_fin,
                "horas": horas,
            })

    elif ext in (".csv",):
        df_csv = pd.read_csv(ruta_archivo, encoding="utf-8", sep=None, engine="python")
        info_ficha = {}
        filas = []

        for i, row in df_csv.iterrows():
            valores = [str(v).strip() for v in row]
            if i < 8 and len(valores) >= 2 and valores[0]:
                info_ficha[valores[0]] = valores[1]
                continue
            if i < 10:
                continue

            if len(valores) >= 7:
                nombre = valores[0]
                apellido = valores[1]
                estado = valores[2]
                competencia = valores[3]
                fecha_ini = valores[4]
                fecha_fin = valores[5]
                horas_str = valores[6]
            else:
                continue

            if not nombre or not competencia:
                continue

            try:
                horas = round(float(horas_str)) if horas_str else 0
            except ValueError:
                horas = 0

            filas.append({
                "nombre": nombre,
                "apellido": apellido,
                "instructor": f"{nombre} {apellido}",
                "estado": estado,
                "competencia_xls": competencia,
                "fecha_inicio": fecha_ini,
                "fecha_fin": fecha_fin,
                "horas": horas,
            })
    else:
        raise ValueError(f"Formato no soportado: {ext}. Usa .xls, .xlsx o .csv")

    df_detalle = pd.DataFrame(filas)
    return df_detalle, info_ficha


def normalizar_competencia(texto_xls):
    texto_lower = texto_xls.lower().strip()
    for patron, nombre_pdf in NORMALIZACION_COMPETENCIAS:
        if patron in texto_lower:
            return nombre_pdf
    return ""


def asignar_competencias(df_detalle, df_pdf):
    df_detalle = df_detalle.copy()
    competencias_pdf = set(df_pdf["competencia"].str.upper().str.strip())

    df_detalle["competencia_normalizada"] = df_detalle["competencia_xls"].apply(normalizar_competencia)
    df_detalle["coincide_pdf"] = df_detalle["competencia_normalizada"].str.upper().str.strip().isin(competencias_pdf)

    return df_detalle


def construir_tabla_competencias(df_detalle, df_pdf):
    df_pdf = df_pdf.copy()

    if not df_detalle.empty and "competencia_normalizada" in df_detalle.columns:
        coincidentes = df_detalle[df_detalle["coincide_pdf"]]

        df_rep = coincidentes.groupby("competencia_normalizada").agg(
            horas_reportadas=("horas", "sum"),
        ).reset_index()
        if not df_rep.empty:
            df_rep.columns = ["competencia", "horas_reportadas"]
        else:
            df_rep = pd.DataFrame(columns=["competencia", "horas_reportadas"])

        instr_estados = coincidentes.groupby("competencia_normalizada").apply(
            lambda g: "; ".join(
                f"{row['instructor']} ({row['estado']})"
                for _, row in g.iterrows()
            ),
            include_groups=False,
        ).reset_index()
        if not instr_estados.empty:
            instr_estados.columns = ["competencia", "instructores_detalle"]
        else:
            instr_estados = pd.DataFrame(columns=["competencia", "instructores_detalle"])
    else:
        df_rep = pd.DataFrame(columns=["competencia", "horas_reportadas"])
        instr_estados = pd.DataFrame(columns=["competencia", "instructores_detalle"])

    df_pdf["competencia_key"] = df_pdf["competencia"].str.upper().str.strip()
    df_rep["competencia_key"] = df_rep["competencia"].str.upper().str.strip()
    instr_estados["competencia_key"] = instr_estados["competencia"].str.upper().str.strip()

    df_result = df_pdf.merge(
        df_rep[["competencia_key", "horas_reportadas"]],
        on="competencia_key",
        how="left",
    )
    df_result = df_result.merge(
        instr_estados[["competencia_key", "instructores_detalle"]],
        on="competencia_key",
        how="left",
    )

    df_result["horas_reportadas"] = df_result["horas_reportadas"].fillna(0).astype(int)
    df_result["diferencia"] = df_result["horas_reportadas"] - df_result["horas_planeadas"]
    df_result["porcentaje"] = (
        (df_result["horas_reportadas"] / df_result["horas_planeadas"] * 100).round(1)
    )
    df_result["instructores_detalle"] = df_result["instructores_detalle"].fillna("\u2014")

    df_result["nombre_limpio"] = (
        df_result["competencia"].map(NOMBRES_LIMPIEZA).fillna(df_result["competencia"])
    )

    df_result = df_result.sort_values("horas_planeadas", ascending=False).reset_index(drop=True)

    return df_result


def construir_tabla_instructores(df_detalle):
    if df_detalle.empty:
        return pd.DataFrame()

    competencias_map = {}
    for _, row in df_detalle.iterrows():
        instr = row["instructor"]
        if instr not in competencias_map:
            competencias_map[instr] = set()
        competencias_map[instr].add(row["competencia_xls"])

    df = df_detalle.groupby(["instructor", "estado"]).agg(
        total_horas=("horas", "sum"),
        registros=("horas", "count"),
    ).reset_index()

    df["competencias"] = df["instructor"].map(
        lambda x: "; ".join(sorted(competencias_map.get(x, set())))
    )

    df = df.sort_values("total_horas", ascending=False).reset_index(drop=True)
    return df
