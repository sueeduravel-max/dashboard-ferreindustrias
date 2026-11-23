import base64
import os
import time
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

# ---------- Configuración de la página ----------
st.set_page_config(
    page_title="Ferreindustrias S.A.C.",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_FONDO = "#0E1117"
AMARILLO = "#FFC800"


@st.cache_data
def a_base64(ruta, blur=0, oscuro=0.0, version=0):
    img = Image.open(ruta).convert("RGB")
    img.thumbnail((1920, 1080))
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    if oscuro:
        img = ImageEnhance.Brightness(img).enhance(1 - oscuro)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=78)
    return base64.b64encode(buf.getvalue()).decode()


# ---------- Quitar la barra superior y el botón "Deploy/Desplegar" ----------
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&display=swap');

  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stToolbarActions"],
  [data-testid="stAppDeployButton"],
  [data-testid="stMainMenu"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  #MainMenu, footer { display: none !important; }

  html, body { overflow-x: hidden; }
  .block-container { padding-top: 1.2rem; }
</style>
""", unsafe_allow_html=True)


# ---------- Portada ----------
if "entrado" not in st.session_state:
    st.session_state.entrado = False

if not st.session_state.entrado:
    fondo_b64 = a_base64("fondo.jpg", blur=2, oscuro=0.55,
                         version=os.path.getmtime("fondo.jpg"))
    logo_b64 = a_base64("logo.png")

    st.markdown(
        f"""
        <style>
          [data-testid="stApp"],
          [data-testid="stAppViewContainer"],
          [data-testid="stMain"] {{
              background: transparent !important;
          }}
          [data-testid="stApp"]::before {{
              content: "";
              position: fixed;
              inset: 0;
              z-index: 0;
              background: url(data:image/jpeg;base64,{fondo_b64}) center/cover no-repeat;
          }}
          [data-testid="stMainBlockContainer"] {{
              position: relative;
              z-index: 1;
              padding-top: calc(50vh - 115px) !important;
          }}
          .caja-logo {{
              display: flex;
              justify-content: center;
          }}
          .caja-logo img {{
              width: 230px;
              border-radius: 12px;
          }}
          .titulo-portada {{
              font-family: 'Cormorant Garamond', Georgia, serif;
              font-size: clamp(12px, 1.6vw, 18px);
              font-weight: 400;
              letter-spacing: 8px;
              text-transform: uppercase;
              color: #ffffff;
              text-align: center;
              white-space: nowrap;
              margin: 16px 0 24px;
          }}
          .stButton > button {{
              background: {COLOR_FONDO};
              color: #ffffff;
              border: 1px solid {AMARILLO};
              box-shadow: 0 0 14px rgba(255, 200, 0, 0.55);
              letter-spacing: 3px;
              font-weight: 600;
          }}
          .stButton > button:hover {{
              background: #161a22;
              color: #ffffff;
              border-color: {AMARILLO};
              box-shadow: 0 0 22px rgba(255, 200, 0, 0.85);
          }}
                    @keyframes aparecerSuave {{
              from {{ opacity: 0; filter: blur(14px); transform: translate3d(0, 20px, 0); }}
              to   {{ opacity: 1; filter: blur(0);    transform: translate3d(0, 0, 0); }}
          }}
          @keyframes aparecerFondo {{
              from {{ opacity: 0; }}
              to   {{ opacity: 1; }}
          }}

          [data-testid="stApp"]::before {{
              animation: aparecerFondo 1.6s ease-out both;
          }}
          .caja-logo {{
              animation: aparecerSuave 1.6s ease-out 0.3s both;
          }}
          .titulo-portada {{
              animation: aparecerSuave 1.6s ease-out 0.9s both;
          }}
                    [data-testid="stHorizontalBlock"] {{
              animation: aparecerSuave 1.6s ease-out 1.5s both;
          }}
          
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="caja-logo"><img src="data:image/png;base64,{logo_b64}"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="titulo-portada">Aplicación Dashboard</div>',
        unsafe_allow_html=True,
    )

    _, centro, _ = st.columns([5, 2, 5])
    with centro:
        if st.button("ENTRAR", key="btn_entrar", width="stretch"):
            # La portada se difumina y se desliza hacia arriba
            st.markdown(
                """
                <style>
                @keyframes salirPortada {
                    to { opacity: 0; transform: translate3d(0, -80px, 0); filter: blur(14px); }
                }
                @keyframes salirFondo { to { opacity: 0; } }
                [data-testid="stMainBlockContainer"] {
                    animation: salirPortada 0.8s ease-in forwards;
                }
                [data-testid="stApp"]::before {
                    animation: salirFondo 0.8s ease-in forwards;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(0.8)
            st.session_state.entrado = True
            st.session_state.recien_entrado = True
            st.rerun()

    st.stop()


# ---------- Aparición difuminada (cada vez que cambias de sección) ----------
def transicion_suave(clave):
    recien = st.session_state.pop("recien_entrado", False)
    cambio = st.session_state.get("ultima_seccion") != clave
    st.session_state.ultima_seccion = clave

    if not (recien or cambio):
        return  # al mover filtros no se repite la animación

    # Nombre distinto en cada transición: así el navegador reinicia la animación
    st.session_state.n_anim = st.session_state.get("n_anim", 0) + 1
    n = st.session_state.n_anim

    lateral = ""
    if recien:  # el lateral solo entra al venir de la portada
        lateral = f"""
        @keyframes lateral{n} {{
            from {{ opacity: 0; transform: translate3d(-24px, 0, 0); filter: blur(8px); }}
            to   {{ opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }}
        }}
        [data-testid="stSidebarContent"] {{
            animation: lateral{n} 1.2s ease-out both;
        }}
        """

    st.markdown(
        f"""
        <style>
        @keyframes pagina{n} {{
            from {{ opacity: 0; transform: translate3d(0, 40px, 0); filter: blur(12px); }}
            to   {{ opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }}
        }}
        [data-testid="stMainBlockContainer"] {{
            animation: pagina{n} 1.4s ease-out both;
        }}
        {lateral}
        </style>
        """,
        unsafe_allow_html=True,
    )
# ---------- Fin portada ----------

# =====================================================================
#  NUEVO DASHBOARD: BAJA ROTACIÓN DE INVENTARIOS (4 OBJETIVOS)
#  Todo se lee del Excel. Si cambias un número en el Excel y guardas,
#  la web se actualiza sola al recargar la página.
# =====================================================================
import openpyxl
import plotly.graph_objects as go

ARCHIVO_EXCEL = "Elaborado para Dashboard.xlsx"

# ---------- Colores ----------
PALETA = ["#FFC800", "#FF8A00", "#E5484D", "#3B82F6", "#22C55E",
          "#A855F7", "#14B8A6", "#94A3B8", "#F472B6"]
px.defaults.color_discrete_sequence = PALETA
COLOR_ESC = {"As-Is": "#E5484D", "Estándar": "#94A3B8", "To-Be": AMARILLO}
ORDEN_MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
               "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]


# ---------- Lectura del Excel ----------
@st.cache_data
def cargar_libro(version):
    """Lee todas las hojas y guarda cada celda con valor: {'OBJ2': {'K2': ...}}."""
    wb = openpyxl.load_workbook(ARCHIVO_EXCEL, data_only=True)
    libro = {}
    for ws in wb.worksheets:
        libro[ws.title.strip()] = {
            c.coordinate: c.value for fila in ws.iter_rows() for c in fila if c.value is not None
        }
    return libro


LIBRO = cargar_libro(os.path.getmtime(ARCHIVO_EXCEL))


def celda(hoja, ref, defecto=None):
    return LIBRO.get(hoja, {}).get(ref, defecto)


def numero(hoja, ref):
    try:
        return float(str(celda(hoja, ref)).replace(",", "."))
    except (TypeError, ValueError):
        return None


def tabla(hoja, fila_ini, fila_fin, columnas):
    """Arma una tabla. columnas = {"Nombre": "Letra"}. La 1.ª columna no puede estar vacía."""
    filas = []
    for f in range(fila_ini, fila_fin + 1):
        fila = {nombre: celda(hoja, f"{letra}{f}") for nombre, letra in columnas.items()}
        if fila[next(iter(columnas))] is not None:
            filas.append(fila)
    df = pd.DataFrame(filas)
    if "Mes" in df.columns:
        df["Mes"] = df["Mes"].astype(str).str.strip().str.capitalize()
    return df


def texto(valor, unidad):
    if valor is None:
        return "—"
    return f"{valor * 100:.1f}%" if unidad == "%" else f"{valor:.1f} días"


# ---------- Resumen de los 4 objetivos (ubicación de cada dato en el Excel) ----------
P = "Planteamiento"
OBJETIVOS = [
    {
        "n": 1, "corto": "Pronóstico de la demanda", "unidad": "%", "mejor": "mayor",
        "indicador": "Exactitud del pronóstico (FA = 1 − MAPE)",
        "herramienta": celda(P, "P9"), "motivo": celda(P, "J9"), "causa": celda(P, "L9"),
        "objetivo": celda("OBJ1", "C9"),
        "as_is": numero("OBJ1", "D53"), "estandar": numero("OBJ1", "D54"), "to_be": numero("OBJ1", "D55"),
        "conclusion": celda("OBJ1", "C72"), "recomendacion": celda("OBJ1", "C73"),
    },
    {
        "n": 2, "corto": "Duración del inventario", "unidad": "días", "mejor": "menor",
        "indicador": "Duración del inventario (días)",
        "herramienta": celda(P, "P13"), "motivo": celda(P, "J13"), "causa": celda(P, "L13"),
        "objetivo": celda("OBJ2", "K2"),
        "as_is": numero("OBJ2", "L84"), "estandar": numero("OBJ2", "F28"), "to_be": numero("OBJ2", "P84"),
        "conclusion": celda(P, "AF13"), "recomendacion": celda(P, "AI13"),
    },
    {
        "n": 3, "corto": "Exactitud de inventarios", "unidad": "%", "mejor": "mayor",
        "indicador": "Confiabilidad del inventario (1 − % error)",
        "herramienta": celda(P, "P17"), "motivo": celda(P, "J17"), "causa": celda(P, "L17"),
        "objetivo": celda(P, "R17"),
        "as_is": numero("OBJ3", "P52"), "estandar": numero("OBJ3", "M76"), "to_be": numero("OBJ3", "P223"),
        "conclusion": celda(P, "AF17"), "recomendacion": celda(P, "AI17"),
    },
    {
        "n": 4, "corto": "Cumplimiento de pedidos", "unidad": "%", "mejor": "mayor",
        "indicador": "Cumplimiento de pedidos (%)",
        "herramienta": "Programación de despachos (regla EDD)",
        "motivo": celda("OBJ4", "C2"), "causa": celda("OBJ4", "C3"),
        "objetivo": celda("OBJ4", "G1"),
        "as_is": numero("OBJ4", "D90"), "estandar": numero("OBJ4", "L67"), "to_be": numero("OBJ4", "F90"),
        "conclusion": celda("OBJ4", "B92"), "recomendacion": celda("OBJ4", "B56"),
    },
]

for o in OBJETIVOS:
    a, s, t = o["as_is"], o["estandar"], o["to_be"]
    o["cumple"] = (t >= s) if o["mejor"] == "mayor" else (t <= s)
    o["cierre"] = (t - a) / (s - a) * 100 if s != a else 100.0  # % de la brecha que se cerró


# ---------- Gráficos reutilizables ----------
def escala(valores, unidad):
    return [v * 100 for v in valores] if unidad == "%" else list(valores)


def grafico_tres_barras(o, alto=300):
    esc = ["As-Is", "Estándar", "To-Be"]
    vals = escala([o["as_is"], o["estandar"], o["to_be"]], o["unidad"])
    sufijo = "%" if o["unidad"] == "%" else " d"
    fig = go.Figure(go.Bar(
        x=esc, y=vals, marker_color=[COLOR_ESC[e] for e in esc],
        text=[f"{v:.1f}{sufijo}" for v in vals], textposition="outside",
    ))
    fig.update_layout(height=alto, margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                      yaxis=dict(range=[0, max(vals) * 1.25], title=o["unidad"]))
    return fig


def grafico_medidor(o):
    a, s, t = escala([o["as_is"], o["estandar"], o["to_be"]], o["unidad"])
    tope = 100 if o["unidad"] == "%" else max(a, s, t) * 1.3
    sube_bien = o["mejor"] == "mayor"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=t,
        number={"suffix": "%" if o["unidad"] == "%" else " días", "valueformat": ".1f"},
        delta={"reference": a, "valueformat": ".1f",
               "increasing": {"color": "#22C55E" if sube_bien else "#E5484D"},
               "decreasing": {"color": "#E5484D" if sube_bien else "#22C55E"}},
        gauge={"axis": {"range": [0, tope]}, "bar": {"color": AMARILLO},
               "steps": [{"range": [0, a], "color": "#3A1F24"}],
               "threshold": {"line": {"color": "#FFFFFF", "width": 4}, "value": s}},
        title={"text": "To-Be vs. As-Is (línea blanca = estándar)", "font": {"size": 14}},
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=10))
    return fig


def linea_estandar(fig, valor, texto_linea="Estándar"):
    fig.add_hline(y=valor, line_dash="dash", line_color=COLOR_ESC["Estándar"],
                  annotation_text=texto_linea, annotation_position="top left")
    return fig


def filtrar_meses(df, meses):
    d = df[df["Mes"].isin(meses)].copy()
    d["Mes"] = pd.Categorical(d["Mes"], categories=ORDEN_MESES, ordered=True)
    return d.sort_values("Mes")


# ---------- Estilos de las tarjetas ----------
st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #1A1D24;
        border-left: 5px solid #FFC800;
        padding: 12px 16px;
        border-radius: 8px;
    }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    .ficha {
        background-color: #1A1D24; border-radius: 8px; padding: 12px 14px;
        height: 100%; border-top: 3px solid #FFC800;
    }
    .ficha small { color: #9AA0A6; text-transform: uppercase; letter-spacing: 1px; font-size: 0.7rem; }
    .ficha p { margin: 4px 0 0 0; font-size: 0.95rem; }
    .etiqueta { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
    .ok  { background: #14532D; color: #86EFAC; }
    .no  { background: #4C1D1D; color: #FCA5A5; }
    </style>
    """,
    unsafe_allow_html=True,
)


def ficha(titulo, contenido):
    st.markdown(f'<div class="ficha"><small>{titulo}</small><p>{contenido}</p></div>',
                unsafe_allow_html=True)


def etiqueta_cumple(o):
    if o["cumple"]:
        return '<span class="etiqueta ok">Cumple el estándar</span>'
    return '<span class="etiqueta no">Aún no llega al estándar</span>'


# ---------- Barra lateral: logo e índice ----------
st.sidebar.image("logo.png")
st.sidebar.title("Ferreindustrias S.A.C.")
seccion = st.sidebar.radio(
    "Índice",
    ["Carátula", "Planteamiento", "Dashboard general",
     "Objetivo 1", "Objetivo 2", "Objetivo 3", "Objetivo 4"],
)
transicion_suave(seccion)

# Filtro de meses (solo para los objetivos 2, 3 y 4)
meses_elegidos = ORDEN_MESES
if seccion in ("Objetivo 2", "Objetivo 3", "Objetivo 4"):
    with st.sidebar:
        st.divider()
        st.subheader("Filtros")
        desde, hasta = st.select_slider("Meses", options=ORDEN_MESES,
                                        value=(ORDEN_MESES[0], ORDEN_MESES[-1]))
        meses_elegidos = ORDEN_MESES[ORDEN_MESES.index(desde): ORDEN_MESES.index(hasta) + 1]


# ---------- Cabecera común de cada objetivo ----------
def cabecera_objetivo(o):
    st.title(f"Objetivo {o['n']}: {o['corto']}")
    st.markdown(etiqueta_cumple(o), unsafe_allow_html=True)
    st.caption(o["objetivo"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: ficha("Motivo", o["motivo"])
    with c2: ficha("Causa raíz", o["causa"])
    with c3: ficha("Herramienta", o["herramienta"])
    with c4: ficha("Indicador", o["indicador"])
    st.write("")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("As-Is (actual)", texto(o["as_is"], o["unidad"]))
    m2.metric("Estándar (meta)", texto(o["estandar"], o["unidad"]))
    dif = o["to_be"] - o["as_is"]
    dif_txt = f"{dif * 100:+.1f} pp" if o["unidad"] == "%" else f"{dif:+.1f} días"
    m3.metric("To-Be (con la mejora)", texto(o["to_be"], o["unidad"]), dif_txt,
              delta_color="normal" if o["mejor"] == "mayor" else "inverse")
    m4.metric("Brecha cerrada", f"{min(o['cierre'], 100):.0f}%")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("As-Is vs. Estándar vs. To-Be")
        st.plotly_chart(grafico_tres_barras(o), width="stretch", key=f"barras{o['n']}")
    with g2:
        st.subheader("Avance del indicador")
        st.plotly_chart(grafico_medidor(o), width="stretch", key=f"medidor{o['n']}")


def pie_objetivo(o):
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Conclusión")
        st.success(o["conclusion"] or "—")
    with c2:
        st.subheader("Recomendación" if o["n"] != 4 else "Propuesta")
        st.info(o["recomendacion"] or "—")


def ver_tabla(df, nombre):
    with st.expander("Ver los datos de esta tabla"):
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("Descargar (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"{nombre}.csv", mime="text/csv", key=f"dl_{nombre}")


# ---------- Contenido según la opción elegida ----------
if seccion == "Carátula":
    # ----- Edita estos datos con los de tu equipo -----
    INSTITUCION = "Universidad Privada del Norte"
    FACULTAD = "Facultad de Ingeniería Industrial"
    CURSO = "Gestión Estratégica de Operaciones"
    TITULO = "Dashboard: Baja rotación de inventarios"
    INTEGRANTES = [
        "DIANA MARIBEL GARCIA SALAZAR",
        "YASSER ARAFAT LUQUE GARCIA",
        "ERIG JOHAN DIAZ PERALTA",
        "JOSUE EDUARDO RAVELLO YASAKA",
    ]
    DOCENTE = "ALDO GUILLERMO RIVADENEYRA CUYA"
    FECHA = "16 Noviembre del 2026"
    # --------------------------------------------------

    izq, centro, der = st.columns([1, 3, 1])
    with centro:
        st.markdown(f"<h3 style='text-align:center'>{INSTITUCION}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='text-align:center'>{FACULTAD}</h5>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{CURSO}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h1 style='text-align:center'>{TITULO}</h1>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<h4 style='text-align:center'>Integrantes</h4>", unsafe_allow_html=True)
        for nombre in INTEGRANTES:
            st.markdown(f"<p style='text-align:center'>{nombre}</p>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center'>Docente</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{DOCENTE}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{FECHA}</p>", unsafe_allow_html=True)

elif seccion == "Planteamiento":
    st.title("Planteamiento del problema")
    st.markdown(f"### Problema general: {celda(P, 'F8', 'BAJA ROTACIÓN DE INVENTARIOS').title()}")
    st.caption(celda(P, "F3", ""))
    st.info(f"**Objetivo general:** {celda(P, 'R4', '')}")

    k1, k2, k3 = st.columns(3)
    rot_actual = numero(P, "H7")
    rot_ref = numero(P, "H13")
    k1.metric("Rotación actual", f"{rot_actual:.2f} veces/año" if rot_actual else "—")
    k2.metric("Rotación de referencia", f"{rot_ref:.0f} veces/año" if rot_ref else "—")
    k3.metric("Impacto económico", f"S/ {numero(P, 'H15'):,.0f}" if numero(P, "H15") else "—")

    st.subheader("Del problema a la solución")
    filas = []
    for o in OBJETIVOS:
        filas.append({"Problema": "Baja rotación de inventarios",
                      "Objetivo": f"Objetivo {o['n']}",
                      "Motivo": str(o["motivo"]).capitalize(),
                      "Herramienta": str(o["herramienta"])})
    arbol = pd.DataFrame(filas)
    fig = px.sunburst(arbol, path=["Problema", "Objetivo", "Motivo", "Herramienta"],
                      color="Objetivo", color_discrete_sequence=PALETA)
    fig.update_traces(insidetextorientation="radial")
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width="stretch")

    st.subheader("Detalle por objetivo")
    detalle = pd.DataFrame([{
        "Objetivo": f"Objetivo {o['n']}", "Motivo": o["motivo"], "Causa raíz": o["causa"],
        "Herramienta": o["herramienta"], "Indicador": o["indicador"],
    } for o in OBJETIVOS])
    st.dataframe(detalle, width="stretch", hide_index=True)

elif seccion == "Dashboard general":
    st.title("Dashboard")
    st.caption("Resumen de los 4 objetivos para incrementar la rotación de inventarios.")

    k1, k2, k3, k4 = st.columns(4)
    cumplen = sum(o["cumple"] for o in OBJETIVOS)
    k1.metric("Rotación actual", f"{numero(P, 'H7'):.2f}")
    k2.metric("Rotación de referencia", f"{numero(P, 'H13'):.0f}")
    k3.metric("Impacto económico", f"S/ {numero(P, 'H15'):,.0f}")
    k4.metric("Objetivos que cumplen el estándar", f"{cumplen} de {len(OBJETIVOS)}")

    st.subheader("As-Is, Estándar y To-Be de cada objetivo")
    for fila in (OBJETIVOS[:2], OBJETIVOS[2:]):
        cols = st.columns(2)
        for col, o in zip(cols, fila):
            with col:
                st.markdown(f"**Objetivo {o['n']} · {o['corto']}** &nbsp; {etiqueta_cumple(o)}",
                            unsafe_allow_html=True)
                st.caption(f"{o['herramienta']} — {o['indicador']}")
                st.plotly_chart(grafico_tres_barras(o, alto=260), width="stretch",
                                key=f"resumen{o['n']}")

    st.subheader("¿Cuánto de la brecha se cerró?")
    st.caption("100% = el To-Be llega al estándar. Más de 100% = lo supera.")
    cierre = pd.DataFrame([{"Objetivo": f"Obj. {o['n']} · {o['corto']}",
                            "Brecha cerrada (%)": round(o["cierre"], 1)} for o in OBJETIVOS])
    fig = px.bar(cierre, x="Brecha cerrada (%)", y="Objetivo", orientation="h",
                 text="Brecha cerrada (%)", color_discrete_sequence=[AMARILLO])
    fig.add_vline(x=100, line_dash="dash", line_color="#FFFFFF")
    fig.update_layout(height=300, yaxis={"categoryorder": "array",
                                          "categoryarray": list(cierre["Objetivo"])[::-1]})
    st.plotly_chart(fig, width="stretch")

    tabla_resumen = pd.DataFrame([{
        "Objetivo": f"Objetivo {o['n']}", "Indicador": o["indicador"],
        "As-Is": texto(o["as_is"], o["unidad"]), "Estándar": texto(o["estandar"], o["unidad"]),
        "To-Be": texto(o["to_be"], o["unidad"]), "¿Cumple?": "Sí" if o["cumple"] else "No",
    } for o in OBJETIVOS])
    st.dataframe(tabla_resumen, width="stretch", hide_index=True)

elif seccion == "Objetivo 1":
    o = OBJETIVOS[0]
    cabecera_objetivo(o)

    st.subheader("Exactitud por producto")
    fa = tabla("OBJ1", 64, 67, {"Producto": "B", "As-Is": "C", "Estándar": "D", "To-Be": "E"})
    fa_largo = fa.melt(id_vars="Producto", var_name="Escenario", value_name="FA")
    fa_largo["FA (%)"] = (fa_largo["FA"].astype(float) * 100).round(1)
    fig = px.bar(fa_largo, x="Producto", y="FA (%)", color="Escenario", barmode="group",
                 text="FA (%)", color_discrete_map=COLOR_ESC)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Error (MAPE) de cada modelo de pronóstico")
    mape = tabla("OBJ1", 38, 40, {"Producto": "B", "PMS (n=3)": "C", "PMP": "D", "SES": "E",
                                  "Regresión lineal": "F", "Estacional (m=2)": "G",
                                  "Modelo elegido": "H"})
    mape_largo = mape.drop(columns="Modelo elegido").melt(id_vars="Producto", var_name="Modelo",
                                                          value_name="MAPE")
    mape_largo["MAPE (%)"] = (mape_largo["MAPE"].astype(float) * 100).round(1)
    fig = px.bar(mape_largo, x="Producto", y="MAPE (%)", color="Modelo", barmode="group",
                 text="MAPE (%)")
    st.plotly_chart(fig, width="stretch")
    st.caption("Modelo elegido (menor MAPE): " +
               ", ".join(f"{r['Producto']} → {r['Modelo elegido']}" for _, r in mape.iterrows()))

    st.subheader("Demanda real vs. pronóstico")
    bloques = {"Pintura": 10, "Cintillo": 30, "Llave": 50}  # fila donde empieza cada producto
    producto = st.selectbox("Producto", list(bloques))
    ini = bloques[producto]
    pron = tabla("OBJ 1 PRONOSTCS", ini, ini + 11,
                 {"Mes": "A", "Demanda real": "C", "PMS (n=3)": "D", "PMP": "E", "SES": "F",
                  "Regresión lineal": "G", "Estacional (m=2)": "H"})
    elegido = mape.set_index("Producto").get("Modelo elegido", pd.Series()).get(producto)
    modelos = st.multiselect("Modelos a comparar",
                             ["PMS (n=3)", "PMP", "SES", "Regresión lineal", "Estacional (m=2)"],
                             default=[m for m in ["PMS (n=3)", elegido] if m] if elegido else ["PMS (n=3)"])
    fig = px.line(pron, x="Mes", y=["Demanda real"] + modelos, markers=True,
                  labels={"value": "Unidades", "variable": "Serie"})
    st.plotly_chart(fig, width="stretch")
    ver_tabla(pron, f"pronostico_{producto.lower()}")
    pie_objetivo(o)

elif seccion == "Objetivo 2":
    o = OBJETIVOS[1]
    cabecera_objetivo(o)

    st.subheader("Duración del inventario por mes")
    dur = tabla("OBJ2", 72, 83, {"Mes": "F", "Duración actual (días)": "L",
                                 "Duración con EOQ (días)": "P", "Mejora (días)": "R"})
    dur = filtrar_meses(dur, meses_elegidos)
    fig = px.line(dur, x="Mes", y=["Duración actual (días)", "Duración con EOQ (días)"],
                  markers=True, labels={"value": "Días", "variable": "Escenario"},
                  color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
    linea_estandar(fig, o["estandar"], f"Estándar {o['estandar']:.0f} días")
    st.plotly_chart(fig, width="stretch")
    ver_tabla(dur, "duracion_inventario")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Lote actual vs. lote óptimo (EOQ)")
        lotes = pd.DataFrame({
            "Producto": ["Pintura", "Cintillo", "Llave"],
            "Lote actual": [numero("OBJ2", "G64"), numero("OBJ2", "K64"), numero("OBJ2", "O64")],
            "EOQ óptimo": [numero("OBJ2", "G65"), numero("OBJ2", "K65"), numero("OBJ2", "O65")],
        })
        fig = px.bar(lotes, x="Producto", y=["Lote actual", "EOQ óptimo"], barmode="group",
                     text_auto=True, labels={"value": "Unidades", "variable": ""},
                     color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.subheader("Clasificación ABC")
        abc = tabla("OBJ2", 46, 48, {"Producto": "F", "Demanda": "I", "Costo (S/)": "L",
                                     "Valor anual (S/)": "O", "Clase": "R"})
        fig = px.pie(abc, names="Producto", values="Valor anual (S/)", hole=0.5)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Impacto económico mensual: antes vs. después del EOQ")
    imp = tabla("OBJ2", 113, 124, {"Mes": "F", "Antes (S/)": "H", "Después (S/)": "K"})
    imp = filtrar_meses(imp, meses_elegidos)
    fig = px.bar(imp, x="Mes", y=["Antes (S/)", "Después (S/)"], barmode="group",
                 labels={"value": "Soles", "variable": ""},
                 color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
    st.plotly_chart(fig, width="stretch")
    pie_objetivo(o)

elif seccion == "Objetivo 3":
    o = OBJETIVOS[2]
    cabecera_objetivo(o)

    asis = tabla("OBJ3", 40, 51, {"Mes": "G", "Diferencia (S/)": "L", "Error": "N", "Confiabilidad": "P"})
    tobe = tabla("OBJ3", 211, 222, {"Mes": "G", "Diferencia (S/)": "L", "Error": "N", "Confiabilidad": "P"})
    asis["Escenario"], tobe["Escenario"] = "As-Is", "To-Be"
    ambos = filtrar_meses(pd.concat([asis, tobe]), meses_elegidos)
    ambos["Confiabilidad (%)"] = (ambos["Confiabilidad"].astype(float) * 100).round(1)
    ambos["Error (%)"] = (ambos["Error"].astype(float) * 100).round(1)

    st.subheader("Confiabilidad del inventario por mes")
    fig = px.line(ambos, x="Mes", y="Confiabilidad (%)", color="Escenario", markers=True,
                  color_discrete_map=COLOR_ESC)
    linea_estandar(fig, o["estandar"] * 100, f"Estándar {o['estandar'] * 100:.0f}%")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Diferencia entre físico y sistema (S/)")
        fig = px.bar(ambos, x="Mes", y="Diferencia (S/)", color="Escenario", barmode="group",
                     color_discrete_map=COLOR_ESC)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.subheader("Costo de implementación RFID")
        costos = tabla("OBJ3", 109, 113, {"Componente": "F", "Cantidad": "N",
                                          "Costo unitario (S/)": "O", "Costo total (S/)": "P"})
        fig = px.pie(costos, names="Componente", values="Costo total (S/)", hole=0.5)
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Inversión total estimada: S/ {numero('OBJ3', 'P114'):,.0f}")
    ver_tabla(ambos.drop(columns=["Error", "Confiabilidad"]), "exactitud_inventarios")
    pie_objetivo(o)

elif seccion == "Objetivo 4":
    o = OBJETIVOS[3]
    cabecera_objetivo(o)

    cum = tabla("OBJ4", 70, 81, {"Mes": "B", "Programados": "C", "Retrasados As-Is": "D",
                                 "Cumplimiento As-Is": "E", "Retrasados To-Be": "F",
                                 "Cumplimiento To-Be": "H", "Impacto As-Is (S/)": "J",
                                 "Impacto To-Be (S/)": "K", "Ahorro (S/)": "L"})
    cum = filtrar_meses(cum, meses_elegidos)
    graf = cum.assign(**{"As-Is": cum["Cumplimiento As-Is"].astype(float) * 100,
                         "To-Be": cum["Cumplimiento To-Be"].astype(float) * 100})

    st.subheader("Cumplimiento de pedidos por mes")
    fig = px.line(graf, x="Mes", y=["As-Is", "To-Be"], markers=True,
                  labels={"value": "Cumplimiento (%)", "variable": "Escenario"},
                  color_discrete_map=COLOR_ESC)
    linea_estandar(fig, o["estandar"] * 100, f"Meta {o['estandar'] * 100:.0f}%")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Impacto económico por retrasos")
        fig = px.bar(cum, x="Mes", y=["Impacto As-Is (S/)", "Impacto To-Be (S/)"], barmode="group",
                     labels={"value": "Soles", "variable": ""},
                     color_discrete_sequence=[COLOR_ESC["As-Is"], COLOR_ESC["To-Be"]])
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Ahorro en los meses elegidos: S/ {cum['Ahorro (S/)'].astype(float).sum():,.0f}")
    with c2:
        st.subheader("Gráfico de control de retrasos (p)")
        ctrl = tabla("OBJ4", 30, 41, {"Mes": "B", "Proporción de retraso": "G",
                                      "LCS": "I", "LC": "K", "LCI": "M"})
        ctrl = filtrar_meses(ctrl, meses_elegidos)
        fig = px.line(ctrl, x="Mes", y=["Proporción de retraso", "LCS", "LC", "LCI"], markers=True,
                      labels={"value": "Proporción", "variable": ""},
                      color_discrete_sequence=[AMARILLO, "#E5484D", "#94A3B8", "#E5484D"])
        st.plotly_chart(fig, width="stretch")

    st.subheader("Plan de programación de despachos")
    plan = tabla("OBJ4", 60, 64, {"Actividad": "B", "Descripción": "E",
                                  "Responsable": "I", "Frecuencia": "K"})
    st.dataframe(plan, width="stretch", hide_index=True)
    ver_tabla(cum, "cumplimiento_pedidos")
    pie_objetivo(o)
