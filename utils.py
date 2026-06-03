import os
import re
import pandas as pd
import streamlit as st

RUTA_PDF_DEFAULT = os.path.join(os.path.dirname(__file__), "TG en Implementacion de Infraestructura de TICs - 228116.pdf")

CORRECCIONES_PDF = {
    "ELABORA LA PROPUESTA T\u00c9CNICA DE SERVICIOS DE LA INFRAESTRUCTURA DE":
        "COMPETENCIA TECNOLOG\u00cdAS DE LA INFORMACI\u00d3N Y LAS COMUNICACIONES (T.I.C)",
}

COMPETENCIAS_ADICIONALES = [
    ("ETAPA PR\u00c1CTICA", 864),
]

NORMALIZACION_COMPETENCIAS = [
    ("mantener equipos de c\u00f3mputo seg\u00fan procedimiento t\u00e9cnico",
     "MANTENER LOS DISPOSITIVOS DE INFRAESTRUCTURA DE LAS T.I.C"),
    ("montar instalaciones el\u00e9ctricas internas de acuerdo con normativa",
     "INSTALACI\u00d3N DE REDES EL\u00c9CTRICAS INTERNAS"),
    ("configurar dispositivos de c\u00f3mputo de acuerdo con especificaciones del dise\u00f1o",
     "CONFIGURACI\u00d3N DE LOS COMPONENTES DE LA INFRAESTRUCTURA TECNOL\u00d3GICA (T.I)"),
    ("implementar la red f\u00edsica de datos seg\u00fan dise\u00f1o y est\u00e1ndares t\u00e9cnicos",
     "IMPLEMENTACI\u00d3N DE LA RED DE DATOS"),
    ("controlar el centro de datos de acuerdo con procedimiento t\u00e9cnico",
     "IMPLEMENTAR Y MANTENER EL CENTRO DE DATOS DE INFRAESTRUCTURA T.I"),
    ("interactuar en lengua inglesa de forma oral y escrita",
     "INGLES"),
    ("ejercer derechos fundamentales del trabajo",
     "DERECHOS FUNDAMENTALES DEL TRABAJO"),
    ("utilizar herramientas inform\u00e1ticas de acuerdo con las necesidades",
     "TIC"),
    ("aplicar pr\u00e1cticas  de protecci\u00f3n ambiental, seguridad y salud en el trabajo",
     "PROTECCI\u00d3N PARA LA SALUD Y EL MEDIO AMBIENTE"),
    ("enrique low murtra-interactuar en el contexto productivo y social",
     "\u00c9TICA PARA LA CONSTRUCCI\u00d3N DE UNA CULTURA DE PAZ"),
    ("aplicaci\u00f3n de conocimientos de las ciencias naturales",
     "FISICA"),
    ("orientar investigaci\u00f3n formativa seg\u00fan referentes t\u00e9cnicos",
     "INVESTIGACI\u00d3N"),
    ("desarrollar procesos de comunicaci\u00f3n eficaces y efectivos",
     "COMUNICACI\u00d3N"),
    ("razonar cuantitativamente frente a situaciones susceptibles",
     "MATEM\u00c1TICAS"),
    ("resultado de aprendizaje de la inducci\u00f3n",
     "INDUCCI\u00d3N"),
    ("trabajar en alturas de acuerdo con normativa de seguridad",
     "TRABAJO EN ALTURAS"),
]

NOMBRES_LIMPIEZA = {
    "MANTENER LOS DISPOSITIVOS DE INFRAESTRUCTURA DE LAS T.I.C": "Mantener dispositivos T.I.C",
    "INSTALACI\u00d3N DE REDES EL\u00c9CTRICAS INTERNAS": "Redes el\u00e9ctricas internas",
    "CONFIGURACI\u00d3N DE LOS COMPONENTES DE LA INFRAESTRUCTURA TECNOL\u00d3GICA (T.I)": "Configuraci\u00f3n componentes T.I",
    "IMPLEMENTACI\u00d3N DE LA RED DE DATOS": "Implementaci\u00f3n red de datos",
    "IMPLEMENTAR Y MANTENER EL CENTRO DE DATOS DE INFRAESTRUCTURA T.I": "Centro de datos",
    "INGLES": "Ingl\u00e9s",
    "DERECHOS FUNDAMENTALES DEL TRABAJO": "Derechos fundamentales",
    "TIC": "TIC",
    "PROTECCI\u00d3N PARA LA SALUD Y EL MEDIO AMBIENTE": "Protecci\u00f3n salud y ambiente",
    "\u00c9TICA PARA LA CONSTRUCCI\u00d3N DE UNA CULTURA DE PAZ": "\u00c9tica / Cultura de paz",
    "FISICA": "F\u00edsica",
    "INVESTIGACI\u00d3N": "Investigaci\u00f3n",
    "COMUNICACI\u00d3N": "Comunicaci\u00f3n",
    "MATEM\u00c1TICAS": "Matem\u00e1ticas",
    "INDUCCI\u00d3N": "Inducci\u00f3n",
    "TRABAJO EN ALTURAS": "Trabajo en alturas",
    "ACTIVIDAD F\u00cdSICA Y H\u00c1BITOS DE VIDA SALUDABLE": "Actividad f\u00edsica",
    "CULTURA EMPRENDEDORA Y EMPRESARIAL": "Cultura emprendedora",
    "COMPETENCIA TECNOLOG\u00cdAS DE LA INFORMACI\u00d3N Y LAS COMUNICACIONES (T.I.C)": "Competencia T.I.C",
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
        df_rep.columns = ["competencia", "horas_reportadas"]

        instr_estados = coincidentes.groupby("competencia_normalizada").apply(
            lambda g: "; ".join(
                f"{row['instructor']} ({row['estado']})"
                for _, row in g.iterrows()
            ),
            include_groups=False,
        ).reset_index()
        instr_estados.columns = ["competencia", "instructores_detalle"]
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
