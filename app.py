"""Painel do Prêmio CNJ de Qualidade — Streamlit."""

from pathlib import Path

import html
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import identidade as cnj
from ficha_pdf import gerar_pdf
import historico as hist_mod

# ano da edição exibida (banner, rodapé, PDF da ficha e filtro de porte)
ANO_EDICAO = 2026
ARQUIVO = Path(__file__).parent / "base_final.xlsx"
# tribunais retirados do painel (a planilha original não é alterada)
EXCLUIDOS = ["TRT16", "CJF", "TSE"]
# fichas avaliativas oficiais em PDF (uma por tribunal; a sigla deve constar no nome do arquivo)
PASTA_FICHAS = Path(__file__).parent / "fichas_pdf"
ARQUIVO_HIST = Path(__file__).parent / "Serie_Completa.csv"
# texto da página "Evolução do Prêmio" (escrito manualmente; o painel só aplica o estilo)
ARQUIVO_HISTORIA = Path(__file__).parent / "historia.py"

ORDEM_PREMIO = ["Excelência", "Diamante", "Ouro", "Prata", "Sem Prêmio", "Não classificado"]
CORES_PREMIO = {
    "Excelência": cnj.MARINHO,
    "Diamante": cnj.CIANO,
    "Ouro": "#C9A227",
    "Prata": "#A3A6AB",
    "Sem Prêmio": "#DADDE2",
    "Não classificado": "#EEF0F3",
}
ORDEM_RAMO = ["Estadual", "Trabalho", "Eleitoral", "Federal", "Militar Estadual", "Superior", "Não classificado"]
ORDEM_EIXO = ["Governança", "Produtividade", "Transparência", "Dados e Tecnologia"]
CORES_EIXO = [cnj.MARINHO, cnj.AZUL, cnj.CIANO, cnj.VERDE_AGUA]
FICHA, CUMPRIMENTO, HISTORICO = "Ficha Avaliativa", "Percentual de cumprimento", "Histórico"
EVOLUCAO = "Evolução do Prêmio"
PAGINAS = [FICHA, CUMPRIMENTO, HISTORICO, EVOLUCAO]
ICONES = {
    FICHA: ":material/assignment:",
    CUMPRIMENTO: ":material/bar_chart:",
    HISTORICO: ":material/timeline:",
    EVOLUCAO: ":material/history_edu:",
}
TODOS = "Todos"

st.set_page_config(page_title="Painel Prêmio CNJ de Qualidade", page_icon="🏆", layout="wide")

# --------------------------------------------------------------------------- estilo
NAVY, DESTAQUE, CINZA = cnj.MARINHO, cnj.CIANO, cnj.CINZA

st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stHeader"] {{display: none;}}
    .block-container {{padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px;}}

    /* título */
    .titulo {{display: flex; align-items: center; gap: 1.1rem; margin: 2.2rem 0 0.2rem 0;}}
    .titulo .icone {{font-size: 3.6rem; line-height: 1;}}
    .titulo h1 {{font-family: 'Montserrat', sans-serif; font-weight: 900;
                 font-size: 4rem; letter-spacing: -0.045em; line-height: 1; margin: 0; padding: 0;
                 color: #1a171b;}}
    .subtitulo {{color: {CINZA}; font-size: 1rem; margin: 0.4rem 0 1.6rem 0.2rem;}}

    /* rótulos dos widgets em caixa alta */
    [data-testid="stWidgetLabel"] p {{text-transform: uppercase; font-size: 0.72rem !important;
                 font-weight: 700; letter-spacing: 0.06em; color: {CINZA};}}

    /* campos de seleção brancos */
    [data-baseweb="select"] > div {{background: #FFFFFF; border-color: #DADDE5;}}
    [data-baseweb="tag"] {{background: {NAVY} !important;}}

    /* navegação (botões no topo) */
    .st-key-nav [data-baseweb="button-group"] {{display: flex; flex-wrap: nowrap; width: 100%; gap: 0.5rem;}}
    .st-key-nav [data-baseweb="button-group"] button {{flex: 1 1 auto; width: auto !important;
                 justify-content: center;}}
    @media (max-width: 900px) {{ .st-key-nav [data-baseweb="button-group"] {{flex-wrap: wrap;}}
                                 .st-key-nav [data-baseweb="button-group"] button {{flex: 1 1 40%;}} }}
    .st-key-nav button {{background: #FFFFFF; border: 1px solid #E3E5EC !important;
                 border-radius: 12px !important; padding: 0.55rem 1.1rem !important;
                 box-shadow: 0 2px 6px rgba(22,24,29,0.06); color: #3A3F4B; font-weight: 600;}}
    .st-key-nav button p {{font-weight: 600;}}
    .st-key-nav button[data-testid="stBaseButton-segmented_controlActive"] {{
                 background: {NAVY}; color: #FFFFFF; border-color: {NAVY} !important;
                 box-shadow: inset 5px 0 0 {DESTAQUE}, 0 4px 12px rgba(10,36,59,0.25);}}
    .st-key-nav button[data-testid="stBaseButton-segmented_controlActive"] * {{color: #FFFFFF;}}

    /* botão Limpar */
    .st-key-limpar button {{background: {NAVY}; color: #FFFFFF; border: none; height: 3rem;
                 border-radius: 12px; box-shadow: inset 7px 0 0 {DESTAQUE}, 0 6px 14px rgba(10,36,59,0.25);
                 font-weight: 600;}}
    .st-key-limpar button:hover {{background: #044e93; color: #FFFFFF;}}
    .st-key-limpar button:active, .st-key-limpar button:focus {{color: #FFFFFF; background: {NAVY};}}

    /* cartões brancos */
    [class*="st-key-card"] {{background: rgba(255,255,255,0.92); border-radius: 22px;
                 padding: 1.6rem 1.8rem; box-shadow: 0 6px 24px rgba(22,24,29,0.06);
                 border: 1px solid #ECEEF3;}}
    [class*="st-key-card"] h3 {{font-family: 'Montserrat', sans-serif; font-weight: 800;
                 letter-spacing: -0.02em;}}

    /* indicadores */
    [data-testid="stMetric"] {{background: #F7F8FB; border-radius: 14px; padding: 0.9rem 1.1rem;
                 border: 1px solid #ECEEF3;}}
    [data-testid="stMetricValue"] {{font-family: 'Montserrat', sans-serif; font-weight: 800;}}

    /* estado vazio */
    .vazio {{text-align: center; padding: 4rem 1rem;}}
    .vazio .icone {{font-size: 4rem;}}
    .vazio h3 {{font-family: 'Montserrat', sans-serif; font-weight: 800; margin: 1rem 0 0.4rem;}}
    .vazio p {{color: {CINZA};}}

    /* botões de seleção (segmented / pills) em geral */
    button[data-testid="stBaseButton-segmented_controlActive"],
    button[data-testid="stBaseButton-pillsActive"] {{
                 background: {NAVY} !important; border-color: {NAVY} !important;
                 box-shadow: inset 4px 0 0 {DESTAQUE};}}
    button[data-testid="stBaseButton-segmented_controlActive"] *,
    button[data-testid="stBaseButton-pillsActive"] * {{color: #FFFFFF !important;}}

    /* ficha: grade de tribunais */
    [class*="st-key-ficha_trib"] [data-testid="stButtonGroup"] , [class*="st-key-hist_trib"] [data-testid="stButtonGroup"] {{gap: 0.45rem;}}
    [class*="st-key-ficha_trib"] button , [class*="st-key-hist_trib"] button {{min-width: 92px; justify-content: center;
                 background: #FFFFFF; border: 1px solid #E3E5EC; border-radius: 10px;
                 padding: 0.5rem 0.8rem; box-shadow: 0 2px 5px rgba(22,24,29,0.05);}}
    [class*="st-key-ficha_trib"] button p , [class*="st-key-hist_trib"] button p {{font-weight: 700; color: {NAVY}; letter-spacing: 0.02em;}}
    .st-key-ficha_eixo button, .st-key-ficha_ramo button {{padding: 0.45rem 1.2rem;}}
    .st-key-ficha_eixo button p, .st-key-ficha_ramo button p {{font-weight: 600;}}

    /* ficha: cabeçalho do tribunal */
    .ficha-topo {{display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: stretch;}}
    .ficha-id {{flex: 1 1 280px;}}
    .ficha-id .sigla {{font-family: 'Montserrat', sans-serif; font-weight: 900; font-size: 2.6rem;
                 letter-spacing: -0.04em; line-height: 1; color: #1a171b;}}
    .ficha-id .nome {{color: {CINZA}; margin-top: 0.35rem;}}
    .ficha-kpis {{display: flex; flex-wrap: wrap; gap: 0.8rem;}}
    .ficha-kpi {{background: #F7F8FB; border: 1px solid #ECEEF3; border-radius: 14px;
                 padding: 0.7rem 1.1rem; min-width: 140px;}}
    .ficha-kpi .rot {{display: block; text-transform: uppercase; font-size: 0.68rem; font-weight: 700;
                 letter-spacing: 0.06em; color: {CINZA}; margin-bottom: 0.25rem;}}
    .ficha-kpi .val {{font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 1.45rem;
                 color: #1a171b;}}
    .ficha-kpi .val small {{font-size: 0.85rem; color: {CINZA}; font-weight: 600;}}
    .selo {{display: inline-block; padding: 0.25rem 0.8rem; border-radius: 999px; font-weight: 700;
                 font-size: 1rem;}}
    .ficha-eixos {{display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
                 gap: 0.8rem; margin-top: 1.3rem;}}
    .ficha-eixo {{border: 1px solid #ECEEF3; border-radius: 14px; padding: 0.7rem 1rem; background: #FFFFFF;}}
    .ficha-eixo .topo {{display: flex; justify-content: space-between; font-weight: 600; font-size: 0.9rem;}}
    .ficha-eixo .barra {{height: 8px; background: #EEF0F5; border-radius: 99px; margin: 0.45rem 0 0.3rem;
                 overflow: hidden;}}
    .ficha-eixo .barra span {{display: block; height: 100%; border-radius: 99px;}}
    .ficha-eixo .pts {{font-size: 0.78rem; color: {CINZA};}}

    /* ficha: quadro avaliativo */
    .ficha-quadro {{max-height: 680px; overflow: auto; border: 1px solid #E3E5EC; border-radius: 14px;}}
    .ficha-quadro table {{width: 100%; min-width: 1100px; table-layout: fixed; border-collapse: separate;
                 border-spacing: 0; font-size: 0.84rem;}}
    .ficha-quadro td {{overflow-wrap: anywhere;}}
    .ficha-quadro thead th {{position: sticky; top: 0; z-index: 2; background: {NAVY}; color: #FFFFFF;
                 text-align: left; font-weight: 600; padding: 0.65rem 0.7rem; white-space: nowrap;
                 border-bottom: 3px solid {DESTAQUE};}}
    .ficha-quadro td {{padding: 0.6rem 0.7rem; border-bottom: 1px solid #EEF0F5; vertical-align: top;
                 color: #2A2E37;}}
    .ficha-quadro tbody tr:hover td {{background: #F7F8FB;}}
    .ficha-quadro td.num {{text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums;}}
    .ficha-quadro td.cen {{text-align: center; white-space: nowrap;}}
    .ficha-quadro td.inc {{white-space: nowrap; font-weight: 600; color: {NAVY};}}
    .ficha-quadro td.com {{white-space: pre-line; line-height: 1.45;}}
    .ficha-quadro tr.secao td {{background: #EEF0F5; font-family: 'Montserrat', sans-serif;
                 font-weight: 800; color: {NAVY}; font-size: 0.95rem; border-bottom: 1px solid #DADDE5;}}
    .ficha-quadro tr.secao td span {{float: right; font-family: 'Montserrat', sans-serif; font-weight: 600;
                 font-size: 0.82rem; color: #3A3F4B;}}
    .chip {{display: inline-block; min-width: 3.4rem; text-align: center; padding: 0.15rem 0.5rem;
                 border-radius: 999px; font-weight: 700; font-size: 0.78rem;}}

    /* ===== identidade visual CNJ ===== */
    /* textos explicativos com mais contraste */
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
                 color: #33363D !important; opacity: 1 !important; font-size: 0.92rem !important;
                 line-height: 1.5;}}
    .ficha-kpi div, .ficha-eixo .pts, .linha-tempo .pos, .ficha-id .nome {{color: #4A4D55 !important;}}
    .ficha-kpi .rot, [data-testid="stWidgetLabel"] p {{color: #55585F !important;}}
    .hist-kpis {{display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.5rem; margin-top: 1.2rem;}}
    .hist-kpis .ficha-kpi {{min-width: 0;}}
    @media (max-width: 900px) {{ .hist-kpis {{grid-template-columns: repeat(2, minmax(0, 1fr));}} }}
    .fases-rot {{margin-top: 1.4rem; text-transform: uppercase; font-size: 0.7rem; font-weight: 700;
                 letter-spacing: 0.06em; color: {CINZA};}}
    .fases {{display: flex; gap: 0.9rem; align-items: stretch; margin-top: 0.6rem;}}
    .fase {{min-width: 0; display: flex; flex-direction: column;}}
    .fase-cab {{background: #EEF1F5; border-radius: 10px; box-shadow: inset 4px 0 0 {cnj.AZUL};
                 text-align: center; text-transform: uppercase; font-size: 0.72rem; font-weight: 700;
                 letter-spacing: 0.05em; color: {NAVY}; padding: 0.45rem 0.8rem; margin-bottom: 0.55rem;}}
    .fase:last-child .fase-cab {{background: #E3F1FA; color: {cnj.AZUL_ESCURO}; box-shadow: inset 4px 0 0 {DESTAQUE};}}
    .fase-sep {{width: 3px; flex: none; border-radius: 3px; margin: 2.6rem 0 0.4rem 0;
                 background: linear-gradient(180deg, {DESTAQUE}, {cnj.AZUL_ESCURO});}}
    @media (max-width: 900px) {{ .fases {{flex-direction: column;}} .fase-sep {{display: none;}} }}
    .linha-tempo {{display: grid; grid-template-columns: repeat(auto-fit, minmax(74px, 1fr)); gap: 0.5rem;}}
    .linha-tempo .ano {{text-align: center; border: 1px solid #E3E6EB; border-radius: 12px; padding: 0.55rem 0.3rem;
                 background: #FFFFFF;}}
    .linha-tempo .ano b {{display: block; font-size: 0.8rem; color: {CINZA}; margin-bottom: 0.35rem;}}
    .linha-tempo .selo-h {{display: block; border-radius: 999px; font-size: 0.72rem; font-weight: 700;
                 padding: 0.22rem 0.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
    .linha-tempo .pct {{display: block; font-size: 0.78rem; font-weight: 600; margin-top: 0.35rem; color: #2A2E37;}}
    .linha-tempo .pos {{display: block; font-size: 0.68rem; color: {CINZA};}}
    .st-key-baixar_pdf button {{background: {NAVY}; border: none; box-shadow: inset 5px 0 0 {DESTAQUE};}}
    .st-key-baixar_pdf button:hover {{background: {cnj.AZUL_ESCURO};}}
    [data-testid="stPlotlyChart"] .main-svg {{background: transparent !important;}}
    [data-testid="stPlotlyChart"] .bglayer rect {{fill: transparent !important;}}
    html, body, .stApp {{font-family: 'Montserrat', sans-serif;}}
    .cnj-banner {{position: relative; overflow: hidden; background: {NAVY}; border-radius: 20px;
                 margin: 1rem 0 1.6rem 0; min-height: 168px; display: flex; align-items: center;}}
    .cnj-banner-conteudo {{position: relative; z-index: 2; display: flex; align-items: center; gap: 2rem;
                 padding: 2rem 2.4rem;}}
    .cnj-logo {{width: 210px; height: auto; flex: none; margin: 4px;}}
    .cnj-sep {{width: 2px; align-self: stretch; background: {DESTAQUE}; border-radius: 2px;}}
    .cnj-kicker {{color: {DESTAQUE}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em;
                 font-size: 0.8rem;}}
    .cnj-banner h1 {{font-family: 'Montserrat', sans-serif; color: #FFFFFF; font-weight: 800;
                 font-size: 2.5rem; letter-spacing: -0.02em; line-height: 1.1; margin: 0.25rem 0 0.35rem 0; padding: 0;}}
    .cnj-banner p {{color: #C9D6E3; margin: 0; font-size: 0.95rem;}}
    .cnj-banner-textura {{position: absolute; top: 0; right: 0; bottom: 0; width: 46%;
                 background-size: cover; background-position: right center;
                 -webkit-mask-image: linear-gradient(to right, transparent 0%, #000 45%);
                 mask-image: linear-gradient(to right, transparent 0%, #000 45%);}}
    .cnj-rodape {{margin-top: 2.5rem; border-radius: 16px; overflow: hidden; background: #FFFFFF;
                 border: 1px solid #E3E6EB;}}
    .cnj-rodape .faixa {{height: 54px; background-size: cover; background-position: center;}}
    .cnj-rodape .linha {{display: flex; justify-content: space-between; align-items: center;
                 padding: 1rem 1.6rem; color: {CINZA}; font-size: 0.8rem;}}
    .cnj-rodape img {{width: 150px; height: auto; margin: 4px;}}
    [class*="st-key-card"] h3 {{color: {cnj.AZUL} !important; text-transform: uppercase; font-weight: 700 !important;
                 font-size: 1.05rem !important; letter-spacing: 0.03em !important;}}
    @media (max-width: 800px) {{
        .cnj-banner-conteudo {{flex-direction: column; align-items: flex-start; gap: 1rem; padding: 1.5rem;}}
        .cnj-sep {{display: none;}}
        .cnj-banner h1 {{font-size: 1.8rem;}}
        .cnj-banner-textura {{width: 100%; opacity: 0.25;}}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

pio.templates["painel"] = go.layout.Template(
    layout=dict(
        font=dict(family="Montserrat, sans-serif", color="#3A3F4B", size=13),
        separators=",.",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        title=dict(font=dict(family="Montserrat, sans-serif", size=17, color="#1a171b")),
        xaxis=dict(gridcolor="#E9EBF0", zerolinecolor="#E9EBF0", linecolor="#E9EBF0"),
        yaxis=dict(gridcolor="#E9EBF0", zerolinecolor="#E9EBF0", linecolor="#E9EBF0"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=cnj.AZUL, align="left",
                        font=dict(family="Montserrat, sans-serif", size=13, color=cnj.PRETO)),
    )
)
pio.templates.default = "plotly_white+painel"


CSS_EVOLUCAO = """
<style>
html, [data-testid="stMain"], [data-testid="stAppViewContainer"] { scroll-behavior: smooth; }

/* cabeçalho da página */
.page-title { font-family: 'Montserrat', sans-serif !important; font-size: 2.6rem !important;
    font-weight: 800 !important; color: @PRETO@; letter-spacing: -0.02em; margin: 0.2rem 0 0.3rem 0; line-height: 1.15; }
.page-subtitle { font-size: 1.1rem !important; color: #33363D; font-weight: 400; margin-bottom: 0.4rem; }

/* linha do tempo */
.timeline-wrapper { border-left: 3px solid @AZUL@; margin-left: 18px; padding-left: 40px; padding-bottom: 30px; }
.timeline-item { position: relative; margin-bottom: 44px; scroll-margin-top: 24px; }
.timeline-item::before { content: ''; position: absolute; left: -53px; top: 30px; width: 20px; height: 20px;
    background-color: @CIANO@; border: 4px solid @MARINHO@; border-radius: 50%; z-index: 2;
    box-shadow: 0 0 0 5px #F1F3F6; }
.timeline-phase { background-color: @MARINHO@; color: #FFFFFF; font-size: 1.05rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.05em; padding: 12px 26px; border-radius: 12px;
    display: inline-block; margin-bottom: 34px; margin-top: 6px; position: relative; left: -58px;
    box-shadow: inset 6px 0 0 @CIANO@, 0 6px 16px rgba(10,36,59,0.22); z-index: 3; }
.timeline-card { background: #FFFFFF; padding: 32px; border-radius: 22px; border: 1px solid #ECEEF3;
    box-shadow: 0 6px 24px rgba(22,24,29,0.06); border-left: 6px solid @CIANO@; transition: transform 0.2s, box-shadow 0.2s;
    display: flex; flex-direction: row; gap: 32px; align-items: flex-start; }
.timeline-card:hover { transform: translateX(6px); box-shadow: 0 10px 28px rgba(10,36,59,0.12); }
.timeline-img { width: 250px; aspect-ratio: 4/3; border-radius: 14px; object-fit: cover;
    box-shadow: 0 4px 12px rgba(22,24,29,0.10); flex-shrink: 0; }
.timeline-content { flex: 1; min-width: 0; }
.timeline-year { font-family: 'Montserrat', sans-serif !important; font-size: 1.55rem; font-weight: 800;
    color: @AZUL@; margin: 0 0 16px 0; line-height: 1.25; }
.timeline-text { font-size: 1rem; color: #33363D; line-height: 1.75; margin: 0 0 14px 0; text-align: justify; }
.timeline-list { margin: 8px 0 18px 0; padding-left: 22px; font-size: 1rem; color: #33363D; line-height: 1.75; }
.timeline-list li { margin-bottom: 8px; }
.timeline-list li::marker { color: @CIANO@; }
.timeline-card a { color: @AZUL@ !important; text-decoration: none; border-bottom: 1px solid rgba(15,118,181,0.35); }
.timeline-card a:hover { color: @MARINHO@ !important; border-bottom-color: @MARINHO@; }
.timeline-card b { color: @PRETO@; }
.timeline-card a b { color: inherit; }
@media (max-width: 900px) {
    .timeline-card { flex-direction: column; gap: 18px; padding: 22px; }
    .timeline-img { width: 100%; height: auto; aspect-ratio: 16/9; }
}

/* menu de navegação fixo ao rolar */
[data-testid="stLayoutWrapper"]:has(> .st-key-menu_nav) { position: sticky; top: 24px; z-index: 50; }
.sticky-menu-container { background: #FFFFFF; padding: 22px; border-radius: 18px; border: 1px solid #ECEEF3;
    box-shadow: 0 6px 24px rgba(22,24,29,0.06); border-top: 5px solid @AZUL@; width: 100%; }
.sticky-title { font-family: 'Montserrat', sans-serif !important; font-weight: 800; font-size: 1.05rem; color: @PRETO@;
    margin-bottom: 12px; border-bottom: 2px solid #EEF1F5; padding-bottom: 10px; }
.sticky-menu-container > div[style] { color: @AZUL@ !important; font-weight: 700 !important;
    letter-spacing: 0.05em; font-size: 0.75rem !important; }
.sticky-link { display: block; text-decoration: none !important; color: #33363D !important; font-weight: 600;
    font-size: 0.9rem; padding: 9px 0 9px 10px; border-bottom: 1px solid #F1F3F6; border-left: 3px solid transparent;
    transition: all 0.2s; }
.sticky-link:hover { color: @MARINHO@ !important; padding-left: 14px !important; border-left: 3px solid @CIANO@;
    background: #F5F8FB; }
</style>
"""

# botões flutuantes (início e voltar ao topo), presentes em todas as páginas
CSS_BOTOES = """
<style>
html, [data-testid="stMain"], [data-testid="stAppViewContainer"] { scroll-behavior: smooth; }
.floating-btn, .floating-btn1 { position: fixed; bottom: 36px; width: 54px; height: 54px; background-color: @MARINHO@;
    color: #FFFFFF !important; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 24px; text-decoration: none !important; box-shadow: inset 0 0 0 2px @CIANO@, 0 6px 18px rgba(10,36,59,0.35);
    z-index: 9999; transition: all 0.25s ease; }
.floating-btn:hover, .floating-btn1:hover { transform: translateY(-6px); background-color: @AZUL_ESCURO@; }
.floating-btn { right: 36px; }
.floating-btn1 { right: 100px; }
@media (max-width: 700px) { .floating-btn, .floating-btn1 { bottom: 20px; width: 46px; height: 46px; font-size: 20px; }
    .floating-btn { right: 16px; } .floating-btn1 { right: 72px; } }
</style>
"""
BOTOES_HTML = """<a href="/" target="_self" class="floating-btn1">🏠</a>
<a href="#topo" class="floating-btn">↑</a>"""
for _k, _v in {"@PRETO@": cnj.PRETO, "@AZUL@": cnj.AZUL, "@CIANO@": cnj.CIANO, "@MARINHO@": cnj.MARINHO,
               "@AZUL_ESCURO@": cnj.AZUL_ESCURO}.items():
    CSS_EVOLUCAO = CSS_EVOLUCAO.replace(_k, _v)
    CSS_BOTOES = CSS_BOTOES.replace(_k, _v)


def grafico(fig, alvo=st):
    fig.update_layout(hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=cnj.AZUL, align="left",
                                      font=dict(family="Montserrat, sans-serif", size=13, color=cnj.PRETO)))
    fig.update_traces(hoverlabel=dict(font_color=cnj.PRETO, bgcolor="#FFFFFF"))
    alvo.plotly_chart(fig, theme=None, config={"displaylogo": False})


def cartao(nome):
    return st.container(key=f"card_{nome}")


# --------------------------------------------------------------------------- dados
def carregar() -> pd.DataFrame:
    # a data de modificação renova o cache quando o base_final.xlsx é substituído
    return _carregar(ARQUIVO.stat().st_mtime, tuple(EXCLUIDOS))


@st.cache_data
def _carregar(versao: float, excluidos: tuple) -> pd.DataFrame:
    df = pd.read_excel(ARQUIVO)
    df = df[~df["Tribunal"].isin(EXCLUIDOS)].copy()
    df["Comentário"] = (
        df["Comentário"].astype(str).str.replace("_x000D_", "", regex=False).replace("nan", "")
    )
    for col in ["Ramo de Justiça", "Porte", "Premiação"]:
        df[col] = df[col].fillna("Não classificado")
    df["Alínea"] = df["Alínea"].fillna("-")
    df["Item"] = df.apply(
        lambda r: r["Inciso"] if r["Alínea"] == "-" else f"{r['Inciso']} {r['Alínea']}", axis=1
    )
    df["ordem_item"] = (
        df["Eixo"].map({e: i for i, e in enumerate(ORDEM_EIXO)}) * 10_000 + df["Romano_num"] * 100
    )
    return df


@st.cache_data
def resumo_tribunais(df: pd.DataFrame) -> pd.DataFrame:
    r = (
        df.groupby("Tribunal")
        .agg(
            Nome=("Nome_Completo", "first"),
            Ramo=("Ramo de Justiça", "first"),
            Porte=("Porte", "first"),
            Premiação=("Premiação", "first"),
            Pontos=("Pontuação", "sum"),
            Máximo=("Máximo", "sum"),
            Oficial=("Percentual Final", "first"),
        )
        .reset_index()
    )
    r["Percentual"] = r["Oficial"].fillna(r["Pontos"] / r["Máximo"])
    r["Nome"] = r["Nome"].fillna("")
    r = r.drop(columns="Oficial")
    r["Premiação"] = pd.Categorical(r["Premiação"], ORDEM_PREMIO, ordered=True)
    return r.sort_values("Percentual", ascending=False)


df = carregar()
tribunais = resumo_tribunais(df)

# --------------------------------------------------------------------------- topo
st.markdown('<div id="topo"></div>' + CSS_BOTOES, unsafe_allow_html=True)
pagina = st.segmented_control(
    "Página", PAGINAS, default=PAGINAS[0], key="nav", label_visibility="collapsed", width="stretch",
    format_func=lambda p: f"{ICONES[p]} {p}",
) or PAGINAS[0]

st.html(
    f"""
    <div class="cnj-banner">
      <div class="cnj-banner-conteudo">
        <img class="cnj-logo" src="{cnj.logo_data_uri('branca')}" alt="Conselho Nacional de Justiça">
        <div class="cnj-sep"></div>
        <div>
          <div class="cnj-kicker">Prêmio CNJ de Qualidade</div>
          <h1>Painel de Resultados {ANO_EDICAO}</h1>
          <p>Ficha avaliativa, percentual de cumprimento e histórico por tribunal</p>
        </div>
      </div>
      <div class="cnj-banner-textura" style="background-image:url('{cnj.textura_svg(10, 3, 60, 7)}')"></div>
    </div>
    """
)


# sem filtros globais: cada página tem sua própria seleção
sel = tribunais
df_sel = df


def ficha_oficial(trib: str):
    """Procura em PASTA_FICHAS o PDF do tribunal (ex.: TJAC.pdf, Ficha_TRE-AC.pdf, TRT_01.pdf)."""
    if not PASTA_FICHAS.is_dir():
        return None
    partes = re.findall(r"[A-Z]+|\d+", trib.upper())
    padrao = r"(?<![A-Z0-9])" + r"[\W_]*".join(
        ("0*" + p) if p.isdigit() else p for p in partes) + r"(?![A-Z0-9])"
    achados = [f for f in sorted(PASTA_FICHAS.glob("*.pdf")) if re.search(padrao, f.stem.upper())]
    if not achados:
        return None
    exatos = [f for f in achados if re.sub(r"[\W_]", "", f.stem.upper()) == re.sub(r"\W", "", trib.upper())]
    return (exatos or achados)[0]


@st.cache_data
def ler_arquivo(caminho: str, modificado: float) -> bytes:
    return Path(caminho).read_bytes()


@st.cache_data(show_spinner="Gerando PDF...")
def pdf_ficha(trib: str, eixo: str, versao: float = 0.0) -> bytes:
    info = tribunais.set_index("Tribunal").loc[trib].to_dict()
    info["Premiação"] = str(info["Premiação"])
    dt = df[df["Tribunal"] == trib].copy()
    dt["Perc"] = dt["Pontuação"] / dt["Máximo"].where(dt["Máximo"] > 0)
    por_eixo = dt.groupby("Eixo")[["Pontuação", "Máximo"]].sum()
    if eixo != "Todos":
        dt = dt[dt["Eixo"] == eixo]
    dt = dt.sort_values(["ordem_item", "Ordem", "Alínea"])
    return gerar_pdf(trib, info, dt, por_eixo, ORDEM_EIXO, CORES_EIXO, eixo, ano=ANO_EDICAO)



def chave_natural(t):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", t)]


@st.cache_data
def _historico(versao: tuple) -> pd.DataFrame:
    return hist_mod.carregar(ARQUIVO_HIST, EXCLUIDOS)


def carregar_historico() -> pd.DataFrame:
    # a versão (datas de modificação) renova o cache quando o CSV ou o historico.py mudam
    versao = (ARQUIVO_HIST.stat().st_mtime, Path(hist_mod.__file__).stat().st_mtime, tuple(EXCLUIDOS))
    return _historico(versao)


@st.cache_data
def _historia(versao: float) -> dict:
    """Lê os textos do historia.py sem executá-lo; o conteúdo é usado exatamente como está no arquivo."""
    import ast
    arvore = ast.parse(ARQUIVO_HISTORIA.read_text(encoding="utf-8"))
    variaveis = {}
    for no in ast.walk(arvore):
        if isinstance(no, ast.Assign) and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str):
            for alvo in no.targets:
                if isinstance(alvo, ast.Name):
                    variaveis[alvo.id] = no.value.value
    textos = [no.value for no in ast.walk(arvore) if isinstance(no, ast.Constant) and isinstance(no.value, str)]
    return {
        "titulo": next((x for x in textos if 'class="page-title"' in x), ""),
        "subtitulo": next((x for x in textos if 'class="page-subtitle"' in x), ""),
        "linha": variaveis.get("timeline_html", ""),
        "menu": variaveis.get("menu_html", ""),
        "botoes": next((x for x in textos if "floating-btn" in x and "<a" in x), ""),
    }


def carregar_historia() -> dict:
    return _historia(ARQUIVO_HISTORIA.stat().st_mtime)


def num_fmt(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(s):
    return s.map(lambda v: f"{v:.1%}".replace(".", ","))


# --------------------------------------------------------------------------- Ficha Avaliativa
if pagina == FICHA:

    def num_br(v, casas=2):
        if pd.isna(v):
            return "—"
        return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def chave_natural(t):
        return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", t)]

    def cor_perc(p):
        if pd.isna(p):
            return "#EEF0F5", "#8A8F9C"
        if p >= 0.999:
            return "#DFF3F1", "#00756E"
        if p >= 0.5:
            return "#E1EFF8", "#0F5F94"
        return "#F9E3E1", "#A33A2F"

    ramos_ficha = [r for r in ORDEM_RAMO if r in sel["Ramo"].unique()]
    with cartao("ficha_sel"):
        ramo_padrao = ramos_ficha[0]
        ramo_f = st.segmented_control(
            "Ramo de justiça", ramos_ficha, default=ramo_padrao, key="ficha_ramo"
        ) or ramo_padrao
        tribs = sorted(sel.loc[sel["Ramo"] == ramo_f, "Tribunal"], key=chave_natural)
        trib = st.pills(
            "Tribunal", tribs, default=tribs[0], key=f"ficha_trib_{re.sub(r'\W', '_', ramo_f)}"
        ) or tribs[0]
        eixo_f = st.segmented_control(
            "Eixo", ["Todos"] + ORDEM_EIXO, default="Todos", key="ficha_eixo"
        ) or "Todos"

    info = tribunais.set_index("Tribunal").loc[trib]
    dt = df[df["Tribunal"] == trib].copy()
    dt["Perc"] = dt["Pontuação"] / dt["Máximo"].where(dt["Máximo"] > 0)

    # ---- cabeçalho do tribunal
    premio_txt = str(info["Premiação"])
    fundo = CORES_PREMIO.get(premio_txt, "#E1E4EA")
    texto_selo = "#FFFFFF" if premio_txt in ("Excelência", "Diamante") else "#1a171b"
    porte_txt = info["Porte"].replace(info["Ramo"], "").strip() or info["Porte"]
    eixos_html = ""
    por_eixo = dt.groupby("Eixo")[["Pontuação", "Máximo"]].sum()
    for e in ORDEM_EIXO:
        if e not in por_eixo.index:
            continue
        p, m = por_eixo.loc[e, "Pontuação"], por_eixo.loc[e, "Máximo"]
        perc = p / m if m else 0
        cor = CORES_EIXO[ORDEM_EIXO.index(e)]
        eixos_html += (
            f'<div class="ficha-eixo"><div class="topo"><span>{e}</span><span>{num_br(perc * 100, 1)}%</span></div>'
            f'<div class="barra"><span style="width:{perc * 100:.1f}%;background:{cor}"></span></div>'
            f'<div class="pts">{num_br(p)} de {num_br(m, 0)} pontos</div></div>'
        )
    with cartao("ficha_topo"):
        st.html(
            f"""
            <div class="ficha-topo">
              <div class="ficha-id"><div class="sigla">{html.escape(trib)}</div>
                <div class="nome">{html.escape(str(info["Nome"] or ""))}</div></div>
              <div class="ficha-kpis">
                <div class="ficha-kpi"><span class="rot">Premiação</span>
                  <span class="selo" style="background:{fundo};color:{texto_selo}">{premio_txt}</span></div>
                <div class="ficha-kpi"><span class="rot">Cumprimento</span>
                  <span class="val">{num_br(info["Percentual"] * 100, 1)}%</span></div>
                <div class="ficha-kpi"><span class="rot">Pontuação</span>
                  <span class="val">{num_br(info["Pontos"])} <small>/ {num_br(info["Máximo"], 0)}</small></span></div>
                <div class="ficha-kpi"><span class="rot">Ramo · Porte</span>
                  <span class="val" style="font-size:1.05rem">{info["Ramo"]} · {porte_txt}</span></div>
              </div>
            </div>
            <div class="ficha-eixos">{eixos_html}</div>
            """
        )

    # ---- quadro avaliativo
    if eixo_f != "Todos":
        dt = dt[dt["Eixo"] == eixo_f]
    dt = dt.sort_values(["ordem_item", "Ordem", "Alínea"])

    linhas = []
    for e in [x for x in ORDEM_EIXO if x in dt["Eixo"].unique()]:
        bloco = dt[dt["Eixo"] == e]
        p, m = bloco["Pontuação"].sum(), bloco["Máximo"].sum()
        linhas.append(
            f'<tr class="secao"><td colspan="8">{e}'
            f'<span>{num_br(p)} de {num_br(m, 0)} pontos · {num_br(p / m * 100 if m else 0, 1)}%</span></td></tr>'
        )
        for _, r in bloco.iterrows():
            bg, fg = cor_perc(r["Perc"])
            chip = "N/A" if pd.isna(r["Perc"]) else f"{num_br(r['Perc'] * 100, 0)}%"
            linhas.append(
                "<tr>"
                f'<td class="inc" style="white-space:normal">{html.escape(str(r["Inciso"]))}</td>'
                f'<td class="desc">{html.escape(str(r["Descrição"]))}</td>'
                f'<td class="cen">{html.escape(str(r["Alínea"]))}</td>'
                f'<td class="num">{r["Ordem"]}</td>'
                f'<td class="num">{num_br(r["Máximo"])}</td>'
                f'<td class="num"><b>{num_br(r["Pontuação"])}</b></td>'
                f'<td class="cen"><span class="chip" style="background:{bg};color:{fg}">{chip}</span></td>'
                f'<td class="com">{html.escape(str(r["Comentário"]).strip())}</td>'
                "</tr>"
            )

    with cartao("ficha_quadro"):
        titulo = "Ficha avaliativa" + ("" if eixo_f == "Todos" else f" — {eixo_f}")
        st.subheader(titulo)
        st.html(
            '<div class="ficha-quadro"><table>'
            '<colgroup><col style="width:105px"><col style="width:24%"><col style="width:62px">'
            '<col style="width:66px"><col style="width:82px"><col style="width:96px">'
            '<col style="width:92px"><col></colgroup><thead><tr>'
            "<th>Inciso</th><th>Descrição</th><th>Alínea</th><th>Ordem</th>"
            "<th>Máximo</th><th>Pontuação</th><th>Atingido</th><th>Comentário</th>"
            "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table></div>"
        )
        exportar = dt[["Tribunal", "Eixo", "Inciso", "Descrição", "Alínea", "Ordem", "Máximo",
                       "Pontuação", "Comentário"]]
        sufixo = "" if eixo_f == "Todos" else "_" + re.sub(r"\W+", "_", eixo_f.lower())
        oficial = ficha_oficial(trib)
        b1, b2, _ = st.columns([1.3, 1.3, 4], vertical_alignment="center")
        with b1:
            if oficial:
                st.download_button(
                    "Baixar ficha (PDF)",
                    data=ler_arquivo(str(oficial), oficial.stat().st_mtime),
                    file_name=oficial.name, mime="application/pdf",
                    icon=":material/picture_as_pdf:", key="baixar_pdf", type="primary", width="stretch",
                )
            else:
                st.download_button(
                    "Baixar ficha (PDF)",
                    data=pdf_ficha(trib, eixo_f, ARQUIVO.stat().st_mtime),
                    file_name=f"ficha_avaliativa_{trib}{sufixo}.pdf", mime="application/pdf",
                    icon=":material/picture_as_pdf:", key="baixar_pdf", type="primary", width="stretch",
                )
        with b2:
            st.download_button(
                "Baixar ficha (CSV)", exportar.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                file_name=f"ficha_avaliativa_{trib}{sufixo}.csv", mime="text/csv",
                icon=":material/download:", width="stretch",
            )

# --------------------------------------------------------------------------- Percentual de cumprimento
elif pagina == CUMPRIMENTO:
    ORDEM_PORTE = ["Grande", "Médio", "Pequeno"]
    base_g = tribunais.copy()
    base_g["Porte_simples"] = [p.replace(r, "").strip() for p, r in zip(base_g["Porte"], base_g["Ramo"])]
    ramos_g = [r for r in ORDEM_RAMO if r in base_g["Ramo"].unique()]

    with cartao("cumprimento_sel"):
        c1, c2 = st.columns([3, 1.6])
        with c1:
            ramo_g = st.segmented_control(
                "Ramo de justiça", ramos_g, default="Estadual" if "Estadual" in ramos_g else ramos_g[0],
                key="cump_ramo",
            ) or ramos_g[0]
        base_g = base_g[base_g["Ramo"] == ramo_g]
        portes_g = [p for p in ORDEM_PORTE if p in base_g["Porte_simples"].unique()]
        porte_g = None
        with c2:
            if portes_g:
                porte_g = st.segmented_control(
                    "Porte", portes_g + ["Todos"], default=portes_g[0],
                    key="cump_porte_" + re.sub(r"\W", "_", ramo_g),
                ) or portes_g[0]
                if porte_g != "Todos":
                    base_g = base_g[base_g["Porte_simples"] == porte_g]

    with cartao("cumprimento"):
        st.subheader("Percentual final por tribunal e premiação")
        rotulo = ramo_g if not porte_g or porte_g == "Todos" else f"{ramo_g} · {porte_g}"
        media_g = base_g["Percentual"].mean()
        st.caption(f"{rotulo} — {len(base_g)} tribunais · média do grupo {num_fmt(media_g * 100, 1)}%")

        graf = base_g.sort_values("Percentual", ascending=True)
        graf["Premiação"] = graf["Premiação"].astype(str)
        fig = go.Figure()
        for p in ORDEM_PREMIO:
            d = graf[graf["Premiação"] == p]
            if d.empty:
                continue
            texto_claro = p in ("Excelência", "Diamante")
            fig.add_bar(
                x=d["Percentual"], y=d["Tribunal"], orientation="h", name=p,
                marker=dict(color=CORES_PREMIO[p], line=dict(color="#C9CDD6", width=0.6), cornerradius=6),
                text=[f"{num_fmt(v * 100, 2)}%" for v in d["Percentual"]],
                textposition="inside", insidetextanchor="end", textangle=0,
                textfont=dict(family="Montserrat", size=13, weight=700,
                              color="#FFFFFF" if texto_claro else cnj.PRETO),
                customdata=d[["Nome", "Pontos", "Máximo"]].values,
                hovertemplate=("<b>%{y}</b> — %{customdata[0]}<br>Percentual final: %{x:.1%}"
                               "<br>Pontos: %{customdata[1]:,.2f} de %{customdata[2]:,}<br>Premiação: <b>" + p + "</b><extra></extra>"),
            )
        x_max = min(1.0, (int(graf["Percentual"].max() * 10) + 1) / 10)
        fig.update_layout(
            barmode="stack", bargap=0.28,
            height=max(320, 58 * len(graf) + 130),
            yaxis=dict(categoryorder="array", categoryarray=graf["Tribunal"].tolist(), title=None,
                       tickfont=dict(size=12, color="#3A3F4B"), showgrid=False),
            xaxis=dict(tickformat=".0%", range=[0, x_max], title=None, dtick=0.2 if x_max > 0.5 else 0.1),
            legend=dict(orientation="h", x=1, xanchor="right", y=-0.1, yanchor="top",
                        title_text="Premiação  ", traceorder="normal"),
            margin=dict(l=10, r=20, t=10, b=80),
            uniformtext=dict(minsize=10, mode="show"),
        )
        grafico(fig)

# --------------------------------------------------------------------------- Histórico
elif pagina == HISTORICO:
    H = carregar_historico()
    CS = hist_mod.CORES_SELO
    nomes_h = dict(zip(tribunais["Tribunal"], tribunais["Nome"]))
    anos = sorted(H["Ano"].unique())
    ramos_h = [r for r in ORDEM_RAMO if r in H["Justiça"].unique()]

    porte_atual = {t: p.replace(r, "").strip() for t, p, r in
                   zip(tribunais["Tribunal"], tribunais["Porte"], tribunais["Ramo"])}
    with cartao("hist_sel"):
        c1, c2 = st.columns([3, 1.6])
        with c1:
            ramo_h = st.segmented_control("Ramo de justiça", ramos_h, default=ramos_h[0],
                                          key="hist_ramo") or ramos_h[0]
        tribs_ramo = sorted(H.loc[H["Justiça"] == ramo_h, "Tribunal"].unique(), key=chave_natural)
        portes_h = [p for p in ["Grande", "Médio", "Pequeno"] if p in {porte_atual.get(t) for t in tribs_ramo}]
        porte_h = "Todos"
        with c2:
            if portes_h:
                porte_h = st.segmented_control(
                    f"Porte ({ANO_EDICAO})", ["Todos"] + portes_h, default="Todos",
                    key="hist_porte_" + re.sub(r"\W", "_", ramo_h),
                ) or "Todos"
        tribs_h = [t for t in tribs_ramo if porte_h == "Todos" or porte_atual.get(t) == porte_h]
        trib_h = st.pills("Tribunal", tribs_h, default=tribs_h[0],
                          key="hist_trib_" + re.sub(r"\W", "_", f"{ramo_h}_{porte_h}")) or tribs_h[0]

    ht = H[H["Tribunal"] == trib_h].sort_values("Ano").copy()
    ramo_ano = H.groupby(["Ano", "Justiça"])["Percentual"].agg(Media_ramo="mean", Melhor_ramo="max").reset_index()
    ht = ht.merge(ramo_ano, on=["Ano", "Justiça"], how="left")
    ht["Selo"] = ht["Selo"].astype(str)
    validos = ht.dropna(subset=["Percentual"])

    # ---- indicadores
    participou = ht[~ht["Selo"].isin(["Não inscrito", "Não participou"])]
    premiados = ht[ht["Selo"].isin(hist_mod.SELOS_PREMIO)]
    contagem = premiados["Selo"].value_counts()
    resumo_premios = " · ".join(f"{contagem[p]} {p}" for p in hist_mod.SELOS_PREMIO if p in contagem)
    melhor = validos.loc[validos["Percentual"].idxmax()] if not validos.empty else None
    ult = ht.iloc[-1]
    ant = ht[ht["Ano"] == ult["Ano"] - 1]
    delta = None
    if not ant.empty and pd.notna(ult["Percentual"]) and pd.notna(ant.iloc[0]["Percentual"]):
        delta = (ult["Percentual"] - ant.iloc[0]["Percentual"]) * 100

    def kpi_html(rot, val, extra=""):
        return (f'<div class="ficha-kpi"><span class="rot">{rot}</span><span class="val">{val}</span>'
                f'<div style="font-size:0.75rem;color:{cnj.CINZA};margin-top:0.15rem">{extra}</div></div>')

    if delta is None:
        txt_delta = "—"
    else:
        cor_d = "#00756E" if delta >= 0 else "#A33A2F"
        txt_delta = f'<span style="color:{cor_d}">{"▲" if delta >= 0 else "▼"} {num_fmt(abs(delta), 1)} p.p.</span>'
    pos_txt = (f"{int(ult['Posição'])}º de {int(ult['Concorrentes'])}" if pd.notna(ult["Posição"]) else "—")
    kpis = "".join([
        kpi_html(f"Resultado {int(ult['Ano'])}",
                 f"{num_fmt(ult['Percentual'] * 100, 1)}%" if pd.notna(ult["Percentual"]) else "—",
                 f"{ult['Selo']} · {pos_txt} no ramo"),
        kpi_html(f"Variação vs {int(ult['Ano']) - 1}", txt_delta, "em pontos percentuais"),
        kpi_html("Melhor resultado",
                 f"{num_fmt(melhor['Percentual'] * 100, 1)}%" if melhor is not None else "—",
                 f"em {int(melhor['Ano'])} ({melhor['Selo']})" if melhor is not None else ""),
        kpi_html("Média histórica",
                 f"{num_fmt(validos['Percentual'].mean() * 100, 1)}%" if not validos.empty else "—",
                 f"{len(validos)} edições com percentual"),
        kpi_html("Premiações", f"{len(premiados)} <small>/ {len(participou)}</small>",
                 resumo_premios or "nenhuma premiação"),
    ])

    # linha do tempo dos selos
    blocos = []
    for _, r in ht.iterrows():
        cor = CS.get(r["Selo"], "#F7F8FA")
        txt = "#FFFFFF" if r["Selo"] in hist_mod.TEXTO_SELO_CLARO else cnj.PRETO
        borda = "border:1px dashed #C9CDD6;" if r["Selo"] in ("Não inscrito", "Não participou") else ""
        pct = f"{num_fmt(r['Percentual'] * 100, 1)}%" if pd.notna(r["Percentual"]) else (
            f"{num_fmt(r['Resultado'], 0)} pts" if pd.notna(r["Resultado"]) else "—")
        pos = f"{int(r['Posição'])}º/{int(r['Concorrentes'])}" if pd.notna(r["Posição"]) else "&nbsp;"
        blocos.append((int(r["Ano"]),
            f'<div class="ano"><b>{int(r["Ano"])}</b>'
            f'<span class="selo-h" style="background:{cor};color:{txt};{borda}" title="{r["Selo"]}">{r["Selo"]}</span>'
            f'<span class="pct">{pct}</span><span class="pos">{pos}</span></div>'
        ))

    FASES = [("Selo Justiça em Números", 2014, 2019), ("Prêmio CNJ de Qualidade", 2020, 2100)]
    grupos_html = []
    for i, (nome_fase, ini, fim) in enumerate(FASES):
        cards = [b for a, b in blocos if ini <= a <= fim]
        if not cards:
            continue
        anos_fase = [a for a, _ in blocos if ini <= a <= fim]
        if grupos_html:
            grupos_html.append('<div class="fase-sep"></div>')
        grupos_html.append(
            f'<div class="fase" style="flex:{len(cards)}">'
            f'<div class="fase-cab">{nome_fase} &nbsp;·&nbsp; {min(anos_fase)}–{max(anos_fase)}</div>'
            f'<div class="linha-tempo" style="grid-template-columns:repeat({len(cards)}, minmax(0, 1fr))">'
            f'{"".join(cards)}</div></div>'
        )

    with cartao("hist_topo"):
        st.html(
            f"""
            <div class="ficha-topo">
              <div class="ficha-id"><div class="sigla">{html.escape(trib_h)}</div>
                <div class="nome">{html.escape(str(nomes_h.get(trib_h, "")))}</div></div>
            </div>
            <div class="hist-kpis">{kpis}</div>
            <div class="fases-rot">Linha do tempo · edição a edição</div>
            <div class="fases">{''.join(grupos_html)}</div>
            """
        )

    # ---- evolução do percentual
    with cartao("hist_evolucao"):
        st.subheader("Evolução do percentual de cumprimento")
        st.caption(f"Comparação com a média e o melhor resultado da Justiça {ramo_h} em cada ano. "
                   "Os critérios e a pontuação máxima mudam a cada edição; compare percentuais com cautela.")
        fig = go.Figure()
        fig.add_scatter(x=ht["Ano"], y=ht["Melhor_ramo"], name="Melhor do ramo", mode="lines+markers",
                        line=dict(color=cnj.CIANO, width=1.5, dash="dot"), marker=dict(size=5, color=cnj.CIANO),
                        hovertemplate="%{x}: %{y:.1%}<br><b>Melhor do ramo</b><extra></extra>")
        fig.add_scatter(x=ht["Ano"], y=ht["Media_ramo"], name="Média do ramo", mode="lines+markers",
                        line=dict(color=cnj.CINZA, width=2, dash="dash"), marker=dict(size=5, color=cnj.CINZA),
                        hovertemplate="%{x}: %{y:.1%}<br><b>Média do ramo</b><extra></extra>")
        fig.add_scatter(
            x=ht["Ano"], y=ht["Percentual"], name=trib_h, mode="lines+markers+text",
            line=dict(color=cnj.AZUL_ESCURO, width=3.5),
            marker=dict(size=15, color=[CS.get(x, "#FFF") for x in ht["Selo"]],
                        line=dict(color=cnj.AZUL_ESCURO, width=2)),
            text=[f"{num_fmt(v * 100, 1)}%" if pd.notna(v) else "" for v in ht["Percentual"]],
            textposition="top center", textfont=dict(family="Montserrat", size=12, weight=700, color=cnj.PRETO),
            customdata=list(zip(ht["Selo"], [f"{int(p)}º de {int(c)} na Justiça {ramo_h}" if pd.notna(p) else ""
                                             for p, c in zip(ht["Posição"], ht["Concorrentes"])])),
            hovertemplate="<b>%{x}</b> — %{y:.1%}<br>%{customdata[0]}<br>%{customdata[1]}<br><b>" + trib_h + "</b><extra></extra>",
        )
        for ano_sp, motivo in hist_mod.ANOS_SEM_PERCENTUAL.items():
            if ano_sp in anos:
                fig.add_vrect(x0=ano_sp - 0.4, x1=ano_sp + 0.4, fillcolor="#EEF1F5", line_width=0, layer="below",
                              annotation_text="sem %", annotation_position="bottom",
                              annotation_font=dict(size=10, color=cnj.CINZA))
        fig.update_layout(
            height=430, hovermode="closest",
            yaxis=dict(tickformat=".0%", range=[0, 1.12], title=None),
            xaxis=dict(dtick=1, title=None, range=[anos[0] - 0.5, anos[-1] + 0.5]),
            legend=dict(orientation="h", y=1.08, x=0, yanchor="bottom"),
            margin=dict(t=30, b=20),
        )
        grafico(fig)

    # ---- posição no ramo + selos
    c1, c2 = st.columns([1.15, 1])
    with c1, cartao("hist_posicao"):
        st.subheader("Posição no ramo")
        st.caption(f"1º = melhor resultado da Justiça {ramo_h} naquele ano. Em 2015, posição pela pontuação.")
        pos = ht.dropna(subset=["Posição"])
        fig = go.Figure()
        fig.add_scatter(
            x=pos["Ano"], y=pos["Posição"], name="Posição", mode="lines+markers+text",
            line=dict(color=cnj.AZUL, width=3), marker=dict(size=11, color=cnj.AZUL),
            text=[f"{int(p)}º/{int(c)}" for p, c in zip(pos["Posição"], pos["Concorrentes"])],
            textposition="top center",
            textfont=dict(family="Montserrat", size=11, weight=700, color=cnj.MARINHO),
            customdata=pos[["Concorrentes"]].values,
            hovertemplate="%{x}: %{y}º de %{customdata[0]}<extra></extra>",
        )
        y_top = int(pos["Concorrentes"].max()) if not pos.empty else 10
        fig.update_layout(
            height=360, showlegend=False,
            yaxis=dict(autorange=False, range=[y_top + 0.8, 0.2], tick0=1, dtick=2 if y_top > 12 else 1, title="posição"),
            xaxis=dict(dtick=1, title=None),
            margin=dict(t=20, b=20),
        )
        grafico(fig)
    with c2, cartao("hist_selos_ramo"):
        st.subheader(f"Selos da Justiça {ramo_h} por ano" if ramo_h not in ("Superior",) else "Selos dos tribunais superiores por ano")
        st.caption("Quantidade de tribunais do ramo em cada selo.")
        dist = (H[H["Justiça"] == ramo_h].assign(Selo=lambda d: d["Selo"].astype(str))
                .groupby(["Ano", "Selo"]).size().reset_index(name="Tribunais"))
        fig = px.bar(dist, x="Ano", y="Tribunais", color="Selo", color_discrete_map=CS,
                     category_orders={"Selo": hist_mod.ORDEM_SELO[::-1]})
        fig.update_traces(marker_line_color="#C9CDD6", marker_line_width=0.5)
        fig.update_layout(height=360, xaxis=dict(dtick=1, title=None), yaxis_title=None,
                          legend_title_text="", legend_traceorder="reversed",
                          bargap=0.25, margin=dict(t=20, b=20))
        grafico(fig)

    # ---- panorama do ramo
    with cartao("hist_panorama"):
        st.subheader(f"Panorama histórico — {ramo_h}" + ("" if porte_h == "Todos" else f" · {porte_h} porte"))
        st.caption("Cor = selo obtido; número = percentual de cumprimento. O tribunal selecionado aparece em destaque.")
        hr = H[(H["Justiça"] == ramo_h) & H["Tribunal"].isin(tribs_h)].copy()
        hr["Selo"] = hr["Selo"].astype(str)
        ordem_t = (hr[hr["Ano"] == anos[-1]].sort_values("Percentual", ascending=False)["Tribunal"].tolist())
        ordem_t += [t for t in sorted(hr["Tribunal"].unique(), key=chave_natural) if t not in ordem_t]
        codigos = {s_: i for i, s_ in enumerate(hist_mod.ORDEM_SELO)}
        z = hr.pivot_table(index="Tribunal", columns="Ano", values="Selo",
                           aggfunc="first").reindex(index=ordem_t, columns=anos)
        pct = hr.pivot_table(index="Tribunal", columns="Ano", values="Percentual").reindex(index=ordem_t, columns=anos)
        zc = z.apply(lambda col: col.map(codigos))
        n = len(hist_mod.ORDEM_SELO)
        escala = []
        for i, s_ in enumerate(hist_mod.ORDEM_SELO):
            escala += [[i / n, CS[s_]], [(i + 1) / n, CS[s_]]]
        texto = pct.apply(lambda col: col.map(lambda v: f"{num_fmt(v * 100, 1)}%" if pd.notna(v) else ""))
        fig = go.Figure(go.Heatmap(
            z=zc.values, x=[str(a) for a in anos], y=ordem_t, zmin=-0.5, zmax=n - 0.5,
            colorscale=escala,
            showscale=False, xgap=3, ygap=3, text=texto.values, texttemplate="%{text}",
            textfont=dict(family="Montserrat", size=12.5, weight=700),
            customdata=z.values,
            hovertemplate="<b>%{y}</b> — %{x}<br>%{customdata}<br>%{text}<extra></extra>",
        ))
        fig.update_layout(
            height=max(260, 34 * len(ordem_t) + 80),
            xaxis=dict(side="top", title=None, showgrid=False),
            yaxis=dict(autorange="reversed", title=None, showgrid=False,
                       tickmode="array", tickvals=ordem_t,
                       ticktext=[f"<b style='color:{cnj.AZUL}'>▶ {t}</b>" if t == trib_h else t for t in ordem_t]),
            margin=dict(t=40, b=10),
        )
        grafico(fig)
        legenda = " ".join(
            f'<span style="display:inline-flex;align-items:center;gap:0.35rem;margin-right:0.9rem;font-size:0.8rem">'
            f'<span style="width:14px;height:14px;border-radius:4px;background:{CS[s_]};border:1px solid #DADDE2"></span>{s_}</span>'
            for s_ in hist_mod.ORDEM_SELO if s_ in set(hr["Selo"]))
        st.html(f"<div>{legenda}</div>")

    # ---- tabela
    with cartao("hist_tabela"):
        st.subheader("Série histórica do tribunal")
        tab = ht[["Ano", "Resultado", "Percentual", "Selo", "Posição", "Concorrentes", "Media_ramo"]].copy()
        tab["Variação (p.p.)"] = tab["Percentual"].diff() * 100
        tab["Posição"] = [f"{int(p)}º de {int(c)}" if pd.notna(p) else "—" for p, c in zip(tab["Posição"], tab["Concorrentes"])]
        tab = tab.drop(columns="Concorrentes").sort_values("Ano", ascending=False)
        st.dataframe(
            tab, hide_index=True, width="stretch",
            column_config={
                "Ano": st.column_config.NumberColumn(format="%d"),
                "Resultado": st.column_config.NumberColumn("Pontos", format="%.2f"),
                "Percentual": st.column_config.ProgressColumn("Percentual", format="percent", min_value=0, max_value=1),
                "Media_ramo": st.column_config.NumberColumn("Média do ramo", format="percent"),
                "Posição": st.column_config.TextColumn("Posição no ramo"),
                "Variação (p.p.)": st.column_config.NumberColumn(format="%+.1f"),
            },
        )
        st.download_button(
            "Baixar série (CSV)",
            ht[["Ano", "Tribunal", "Justiça", "Resultado", "Percentual", "Selo", "Posição", "Concorrentes"]]
            .to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
            file_name=f"serie_historica_{trib_h}.csv", mime="text/csv", icon=":material/download:",
        )


# --------------------------------------------------------------------------- Evolução do Prêmio
elif pagina == EVOLUCAO:
    conteudo = carregar_historia()
    st.markdown(CSS_EVOLUCAO, unsafe_allow_html=True)
    col_main, _, col_menu = st.columns([7.5, 0.3, 2.2])
    with col_main:
        with cartao("evolucao_titulo"):
            st.markdown(conteudo["titulo"], unsafe_allow_html=True)
            st.markdown(conteudo["subtitulo"], unsafe_allow_html=True)
        st.write("")
        st.markdown(conteudo["linha"], unsafe_allow_html=True)
    with col_menu:
        with st.container(key="menu_nav"):
            st.markdown(conteudo["menu"], unsafe_allow_html=True)


# --------------------------------------------------------------------------- botões flutuantes
st.markdown(BOTOES_HTML, unsafe_allow_html=True)

# --------------------------------------------------------------------------- rodapé
st.html(
    f"""
    <div class="cnj-rodape">
      <div class="faixa" style="background-image:url('{cnj.textura_svg(24, 1, 54, 3)}')"></div>
      <div class="linha">
        <img src="{cnj.logo_data_uri('cor')}" alt="Conselho Nacional de Justiça">
        <span>Prêmio CNJ de Qualidade · Painel de Resultados {ANO_EDICAO}</span>
      </div>
    </div>
    """
)
