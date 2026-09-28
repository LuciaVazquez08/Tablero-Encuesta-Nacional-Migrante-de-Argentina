import pandas as pd
import plotly.express as px
import streamlit as st

from enma_palette import CHART_SEQUENCE, FONT_BODY, COLORS

DATA_PATH = "data/processed/ENMA.csv"
COLOR_DETALLE = COLORS["text_3"]

def aplicar_tipografia(fig):
    """DM Sans en negro puro para todos los textos del gráfico. El título va aparte, vía
    st.subheader (que ya hereda Syncopate del CSS global de la app), no como título nativo de Plotly."""
    fig.update_layout(
        font=dict(family=FONT_BODY, color="#000000"),
        legend=dict(font=dict(family=FONT_BODY, color="#000000")),
        hoverlabel=dict(font=dict(family=FONT_BODY, color="#000000")),
    )
    fig.update_xaxes(title_font=dict(family=FONT_BODY, color="#000000"), tickfont=dict(family=FONT_BODY, color="#000000"))
    fig.update_yaxes(title_font=dict(family=FONT_BODY, color="#000000"), tickfont=dict(family=FONT_BODY, color="#000000"))
    return fig


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def iniciar_filtros() -> "st.delta_generator.DeltaGenerator":
    """Encabezado del panel de filtros de la página + placeholder para el contador
    de encuestados"""
    st.session_state["_color_index"] = 0
    st.sidebar.header("Filtros")
    return st.sidebar.empty()

def _siguiente_color() -> str:
    """Devuelve el próximo color de CHART_SEQUENCE y avanza la rotación un lugar. Todas las
    barras de un mismo gráfico comparten ese único color"""
    indice = st.session_state.get("_color_index", 0)
    st.session_state["_color_index"] = indice + 1
    return CHART_SEQUENCE[indice % len(CHART_SEQUENCE)]


def filtro_edicion(df: pd.DataFrame, key: str, reset_keys: list[str] | None = None) -> pd.Series:
    """Selector de Año. Si se pasan `reset_keys`, al cambiar de año se incrementa
    la "versión" de esos otros widgets (p. ej. el filtro de nacionalidad). Un
    widget de Streamlit conserva su selección en el navegador mientras
    conserve su `key`, aunque el script borre esa entrada de session_state"""
    anios = sorted(df["Año"].dropna().unique())
    seleccion = st.sidebar.selectbox("Edición / Año", anios, key=key)
    anio_previo_key = f"_{key}_anio_previo"
    anio_previo = st.session_state.get(anio_previo_key)
    if reset_keys and anio_previo is not None and anio_previo != seleccion:
        for reset_key in reset_keys:
            version_key = f"_{reset_key}_version"
            st.session_state[version_key] = st.session_state.get(version_key, 0) + 1
    st.session_state[anio_previo_key] = seleccion
    return df["Año"] == seleccion

def version_key(key: str) -> str:
    """Key efectiva de un widget versionado por `filtro_edicion`"""
    return f"{key}_{st.session_state.get(f'_{key}_version', 0)}"

def filtro_nacionalidad(df: pd.DataFrame, key: str, df_opciones: pd.DataFrame | None = None) -> pd.Series:
    fuente = df_opciones if df_opciones is not None else df
    nacionalidades = sorted(fuente["pais_nacimiento_var"].dropna().unique())
    seleccion = st.sidebar.multiselect("Nacionalidad", nacionalidades, default=nacionalidades, key=version_key(key))
    return df["pais_nacimiento_var"].isin(seleccion)

def filtro_genero(df: pd.DataFrame, key: str) -> pd.Series:
    generos = sorted(df["genero_agrup"].dropna().unique())
    seleccion = st.sidebar.multiselect("Género", generos, default=generos, key=key)
    return df["genero_agrup"].isin(seleccion)


def filtro_edad(df: pd.DataFrame, key: str) -> pd.Series:
    edades = sorted(df["edad_agrupada"].dropna().unique())
    seleccion = st.sidebar.multiselect("Edades", edades, default=edades, key=key)
    return df["edad_agrupada"].isin(seleccion)


def filtro_region(df: pd.DataFrame, key: str) -> pd.Series:
    regiones = sorted(df["region"].dropna().unique())
    seleccion = st.sidebar.multiselect("Región", regiones, default=regiones, key=key)
    return df["region"].isin(seleccion)


def aplicar_filtros(df: pd.DataFrame, mask: pd.Series, contador) -> pd.DataFrame:
    df_filtrado = df[mask]
    contador.caption(f"{len(df_filtrado):,}".replace(",", ".") + " personas encuestadas")
    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        st.stop()
    return df_filtrado


def distribucion(
    df: pd.DataFrame,
    columna: str,
    orden: list | None = None,
    columna_peso: str = "peso_muestral_total",
) -> pd.DataFrame:
    datos = df.dropna(subset=[columna])
    cantidad = datos.groupby(columna)[columna_peso].sum()
    porcentaje = cantidad.div(cantidad.sum()).mul(100).round(1)
    if orden:
        indice = [c for c in orden if c in cantidad.index]
    else:
        indice = porcentaje.sort_values(ascending=False).index
    data = pd.DataFrame({
        columna: indice,
        "Porcentaje": porcentaje.reindex(indice).values,
        "Cantidad": cantidad.reindex(indice).values,
    })
    return data


def grafico_barras(
    df: pd.DataFrame,
    columna: str,
    titulo: str,
    orden: list | None = None,
    horizontal: bool = False,
    columna_peso: str = "peso_muestral_total",
):
    with st.container(border=True, key=f"grafico_{columna}"):
        st.subheader(titulo)
        data = distribucion(df, columna, orden, columna_peso=columna_peso)
        if data.empty:
            st.info("Sin datos para este filtro.")
            return
        color = _siguiente_color()
        if horizontal:
            data = data.iloc[::-1]
            fig = px.bar(
                data, x="Porcentaje", y=columna, orientation="h",
                color_discrete_sequence=[color], text="Porcentaje",
                custom_data=["Cantidad"],
            )
            fig.update_layout(yaxis_title=None, xaxis_title="Porcentaje (%)")
            fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.18])
            hovertemplate = (
                "%{y}<br>Porcentaje: %{x:.1f}%"
                "<extra></extra>"
            )
        else:
            fig = px.bar(
                data, x=columna, y="Porcentaje",
                color_discrete_sequence=[color], text="Porcentaje",
                custom_data=["Cantidad"],
            )
            fig.update_layout(xaxis_title=None, yaxis_title="Porcentaje (%)")
            fig.update_yaxes(range=[0, data["Porcentaje"].max() * 1.3])
            hovertemplate = (
                "%{x}<br>Porcentaje: %{y:.1f}%"
                "<extra></extra>"
            )
        fig.update_traces(texttemplate="%{text}%", textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")

def _a_binario(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie.replace({True: 1, False: 0, "True": 1, "False": 0}),errors="coerce",)

def grafico_multiseleccion(
    df: pd.DataFrame,
    opciones: list[tuple[str, str]],
    titulo: str,
    subtitulo: str,
    columna_peso: str = "peso_muestral_total",
):
    columna_base = opciones[0][0]
    with st.container(border=True, key=f"grafico_{columna_base}"):
        st.subheader(titulo)
        st.caption(subtitulo)
        filas = []
        for columna, etiqueta in opciones:
            datos = df.dropna(subset=[columna])
            if datos.empty:
                continue
            seleccionado = _a_binario(datos[columna])
            peso = datos[columna_peso]
            total_peso = peso.sum()
            if not total_peso:
                continue
            cantidad = (seleccionado * peso).sum()
            filas.append({
                "Opción": etiqueta,
                "Porcentaje": round(cantidad / total_peso * 100, 1),
                "Cantidad": round(cantidad),
            })
        if not filas:
            st.info("Sin datos para este filtro.")
            return
        data = pd.DataFrame(filas).sort_values("Porcentaje", ascending=True)
        fig = px.bar(
            data, x="Porcentaje", y="Opción", orientation="h",
            color_discrete_sequence=[_siguiente_color()], text="Porcentaje",
            custom_data=["Cantidad"],
        )
        fig.update_layout(yaxis_title=None, xaxis_title="Porcentaje (%)")
        fig.update_xaxes(range=[0, data["Porcentaje"].max() * 1.18])
        hovertemplate = ("%{y}<br>Porcentaje: %{x:.1f}%""<extra></extra>")
        fig.update_traces(texttemplate="%{text}%", textposition="outside", hovertemplate=hovertemplate)
        fig.update_layout(margin=dict(t=25, b=25, l=15, r=15))
        aplicar_tipografia(fig)
        st.plotly_chart(fig, width="stretch")