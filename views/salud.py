import streamlit as st

from data_utils import aplicar_filtros, filtro_cruce, filtro_edicion, grafico_barras, grafico_multiseleccion, iniciar_filtros, load_data

FORMAS_ACCESO_SALUD = [
    ("salud_acceso_publica", "Salud pública"),
    ("salud_acceso_obrasocial", "Obra social, prepaga o privada"),
    ("salud_acceso_tradicional", "Medicina tradicional, familiar o comunitaria"),
    ("salud_acceso_nunca_necesito", "Nunca necesitó atenderse"),
    ("salud_acceso_no_pudo", "No pudo atenderse"),
    ("salud_acceso_otro", "Otro"),
]

ENFERMEDADES_2020 = [
    ("salud_enfermedad_ninguna", "No tiene ninguna enfermedad"),
    ("salud_enfermedad_cardiovascular", "Enfermedad cardiovascular"),
    ("salud_enfermedad_diabetes", "Diabetes"),
    ("salud_enfermedad_respiratoria", "Enfermedad respiratoria crónica"),
    ("salud_enfermedad_cancer", "Cáncer"),
    ("salud_enfermedad_renal", "Enfermedad renal"),
    ("salud_enfermedad_otra", "Otras"),
]

MOTIVOS_ACUDIO_2023 = [
    ("salud_motivo_fisica", "Salud física"),
    ("salud_motivo_mental", "Salud mental"),
    ("salud_motivo_sexual_reproductiva", "Salud sexual y/o reproductiva"),
    ("salud_motivo_no_acudio", "No acudió al sistema de salud"),
]

TIPOS_DIFICULTAD_SALUD = [
    ("salud_dificultad_maltrato", "Maltrato o discriminación"),
    ("salud_dificultad_economicas", "Barreras económicas"),
    ("salud_dificultad_administrativas", "Barreras administrativas"),
    ("salud_dificultad_comunicacion", "Barreras de comunicación"),
    ("salud_dificultad_acceso_servicio", "Barreras de acceso al servicio (turnos, distancia)"),
    ("salud_dificultad_otras", "Otras"),
]

def render():
    df = load_data()
    contador = iniciar_filtros()

    mask = filtro_edicion(df, "salud_edicion")

    df = aplicar_filtros(df, mask, contador)
    filtro_cruce(df, "salud_cruce")

    st.title("Derecho a la salud")
    st.caption("Cobertura, acceso y dificultades relacionadas con la atención de la salud.")

    col1, col2 = st.columns(2)
    with col1:
        grafico_barras(df, "salud_cobertura", "Distribución por cobertura de salud")
    with col2:
        grafico_barras(df, "salud_dificultad_acceso", "Distribución por frecuencia de dificultades para acceder a la salud")

    if (df["Año"] == 2020).all():
        grafico_multiseleccion(
            df, ENFERMEDADES_2020,
            "Distribución por enfermedades crónicas declaradas",
            "Qué % de quienes respondieron declaró tener cada enfermedad (pregunta solo de la edición "
            "2020; no es comparable con la de 2023, que pregunta por qué motivos acudió al sistema de salud).",
        )
    else:
        grafico_multiseleccion(
            df, MOTIVOS_ACUDIO_2023,
            "Distribución por motivos para acudir al sistema de salud",
            "Qué % de quienes respondieron acudió al sistema de salud en los últimos 2 años por cada "
            "motivo (pregunta solo de la edición 2023; no es comparable con la de 2020, que pregunta "
            "por enfermedades crónicas).",
        )
    
    grafico_multiseleccion(
        df, FORMAS_ACCESO_SALUD,
        "Distribución por formas de acceso a la atención de la salud",
        "Qué % de la población accedió (o intentó acceder) a la salud por cada vía en los últimos dos años (pregunta de selección múltiple).",
    )

    sin_dificultades = df["salud_dificultad_ninguna"] != True  # noqa: E712
    grafico_multiseleccion(
        df[sin_dificultades], TIPOS_DIFICULTAD_SALUD,
        "Tipos de dificultades de acceso a la salud",
        "Qué % de quienes tuvieron dificultades declaró cada tipo (pregunta de selección múltiple: una persona puede haber tenido más de una).",
    )