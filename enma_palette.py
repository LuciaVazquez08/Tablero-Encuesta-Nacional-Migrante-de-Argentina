"""
Paleta de marca extraída de encuestamigrante.ar (bloque :root del CSS del sitio).
"""

COLORS = {
    "yellow_1": "#FFC456",
    "yellow_2": "#FFA602",
    "orange_1": "#FF7900",
    "orange_2": "#FF4900",
    "blue": "#027BFF",
    "blue_dark": "#0055CC",
    "blue_pale": "#D6EAFF",
    "blue_accent": "#3DA0FF",
    "text": "#0F0F1A",
    "text_2": "#2E2E4A",
    "text_3": "#6B6B8A",
    "border": "#E6E9F2",
    "background": "#FFFFFF",
    "background_alt": "#F5F7FB",
}

CHART_SEQUENCE = [
    COLORS["orange_1"],
    COLORS["blue"],
    COLORS["yellow_2"],
    COLORS["blue_accent"],
    COLORS["orange_2"],
    COLORS["yellow_1"],
    COLORS["blue_dark"],
    COLORS["text_3"],
]

FONT_HEADINGS = '"Syncopate", sans-serif'
FONT_BODY = '"DM Sans", sans-serif'


def inject_fonts() -> None:
    import streamlit as st

    st.markdown(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syncopate:wght@400;700&display=swap" rel="stylesheet">
        <style>
        html, body, [class*="css"] {{
            font-family: {FONT_BODY};
            color: {COLORS['text']};
        }}
        h1 {{
            font-family: {FONT_HEADINGS} !important;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        [data-testid="stSidebarNavLink"] {{
            height: auto !important;
            min-height: 2rem;
        }}
        [data-testid="stSidebarNavLink"] span,
        [data-testid="stSidebarNavLink"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebarNavLink"] p {{
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
            height: auto !important;
        }}
        [class*="st-key-grafico_"], [class*="st-key-seccion_"] {{
            border: 2px solid #000000 !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
        }}
        [data-testid="stPlotlyChart"] {{
            height: 42vh;
            min-height: 260px;
            max-height: 520px;
        }}
        [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]),
        [data-testid="stFullScreenFrame"]:has(> [data-testid="stPlotlyChart"]) {{
            height: auto !important;
            flex: 0 0 auto !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
