"""Geração da Ficha Avaliativa em PDF, com a identidade visual do CNJ."""

import base64
import io
import tempfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from svglib.svglib import svg2rlg

import identidade as cnj

BASE = Path(__file__).parent
PAGINA = landscape(A4)
MARGEM = 14 * mm
ALTURA_FAIXA = 26 * mm
C = colors.HexColor


# --------------------------------------------------------------------------- fontes
@lru_cache
def _fontes() -> dict:
    pasta = BASE / "assets" / "fontes"
    pesos = {"reg": "Regular", "med": "Medium", "semi": "SemiBold", "bold": "Bold", "xbold": "ExtraBold"}
    try:
        for chave, peso in pesos.items():
            pdfmetrics.registerFont(TTFont(f"Montserrat-{peso}", str(pasta / f"Montserrat-{peso}.ttf")))
        return {k: f"Montserrat-{v}" for k, v in pesos.items()}
    except Exception:  # sem os arquivos de fonte: usa Helvetica
        return {"reg": "Helvetica", "med": "Helvetica", "semi": "Helvetica-Bold",
                "bold": "Helvetica-Bold", "xbold": "Helvetica-Bold"}


@lru_cache
def _svg(caminho: str):
    return svg2rlg(caminho)


@lru_cache
def _textura():
    dados = base64.b64decode(cnj.textura_svg(8, 2, 60, 7).split(",", 1)[1])
    with tempfile.NamedTemporaryFile("wb", suffix=".svg", delete=False) as f:
        f.write(dados)
        nome = f.name
    try:
        return svg2rlg(nome)
    finally:
        Path(nome).unlink(missing_ok=True)


def _desenhar(canvas, desenho, x, y, largura):
    esc = largura / desenho.width
    canvas.saveState()
    canvas.translate(x, y)
    canvas.scale(esc, esc)
    renderPDF.draw(desenho, canvas, 0, 0)
    canvas.restoreState()
    return desenho.height * esc


def num_br(v, casas=2):
    if pd.isna(v):
        return "—"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _cor_perc(p):
    if pd.isna(p):
        return "#EEF0F3", "#707173"
    if p >= 0.999:
        return "#DFF3F1", "#00756E"
    if p >= 0.5:
        return "#E1EFF8", "#0F5F94"
    return "#F9E3E1", "#A33A2F"


def _partes_comentario(texto: str, largura: float, estilo, altura_max: float = 300) -> list:
    """Divide um comentário longo em blocos que cabem numa página (por linhas e, se preciso, palavras)."""
    def altura(linhas):
        return Paragraph("<br/>".join(linhas), estilo).wrap(largura, 10_000)[1]

    linhas = []
    for linha in escape(texto.replace("\r", "")).split("\n"):
        if altura([linha]) <= altura_max:
            linhas.append(linha)
            continue
        atual = []  # linha única gigante: quebra por palavras
        for palavra in linha.split(" "):
            if atual and altura([" ".join(atual + [palavra])]) > altura_max:
                linhas.append(" ".join(atual))
                atual = []
            atual.append(palavra)
        if atual:
            linhas.append(" ".join(atual))

    partes, atual = [], []
    for linha in linhas:
        if atual and altura(atual + [linha]) > altura_max:
            partes.append(atual)
            atual = []
        atual.append(linha)
    if atual:
        partes.append(atual)
    return ["<br/>".join(p) for p in partes] or [""]


class BarraProgresso(Flowable):
    def __init__(self, perc, cor, largura, altura=5):
        super().__init__()
        self.perc, self.cor, self.width, self.height = max(0, min(1, perc)), cor, largura, altura

    def draw(self):
        c = self.canv
        c.setFillColor(C("#E6EAF0"))
        c.roundRect(0, 0, self.width, self.height, self.height / 2, stroke=0, fill=1)
        if self.perc > 0:
            c.setFillColor(C(self.cor))
            c.roundRect(0, 0, max(self.height, self.width * self.perc), self.height, self.height / 2, stroke=0, fill=1)


# --------------------------------------------------------------------------- PDF
def gerar_pdf(trib: str, info: dict, itens: pd.DataFrame, por_eixo: pd.DataFrame,
              ordem_eixos: list, cores_eixos: list, eixo_filtro: str = "Todos", ano: int = 2025) -> bytes:
    """
    info: Nome, Ramo, Porte, Premiação, Pontos, Máximo, Percentual
    itens: Eixo, Inciso, Descrição, Alínea, Máximo, Pontuação, Perc, Comentário (já ordenados)
    por_eixo: índice = eixo, colunas Pontuação e Máximo (tribunal inteiro)
    """
    F = _fontes()
    buf = io.BytesIO()
    largura_util = PAGINA[0] - 2 * MARGEM
    gerado = datetime.now().strftime("%d/%m/%Y %H:%M")
    logo_branca = _svg(str(cnj.PASTA / "logo-cnj-branca.svg"))
    logo_cor = _svg(str(cnj.PASTA / "logo-cnj-cor.svg"))
    textura = _textura()

    def moldura(canvas, doc):
        w, h = PAGINA
        canvas.saveState()
        # faixa superior institucional
        canvas.setFillColor(C(cnj.MARINHO))
        canvas.rect(0, h - ALTURA_FAIXA, w, ALTURA_FAIXA, stroke=0, fill=1)
        # textura à direita (recortada na faixa)
        p = canvas.beginPath()
        p.rect(w * 0.62, h - ALTURA_FAIXA, w * 0.38, ALTURA_FAIXA)
        canvas.saveState()
        canvas.clipPath(p, stroke=0, fill=0)
        _desenhar(canvas, textura, w * 0.62, h - ALTURA_FAIXA - 2, w * 0.38 + 2)
        canvas.restoreState()
        # degradê sobre a textura
        for i in range(40):
            canvas.setFillColor(C(cnj.MARINHO), alpha=1 - i / 40)
            canvas.rect(w * 0.62 + i * 3, h - ALTURA_FAIXA, 3.2, ALTURA_FAIXA, stroke=0, fill=1)
        # logotipo (versão branca sobre fundo escuro), com área de proteção
        _desenhar(canvas, logo_branca, MARGEM, h - ALTURA_FAIXA + 6.5 * mm, 46 * mm)
        canvas.setStrokeColor(C(cnj.CIANO))
        canvas.setLineWidth(1.2)
        x_sep = MARGEM + 52 * mm
        canvas.line(x_sep, h - ALTURA_FAIXA + 5 * mm, x_sep, h - 5 * mm)
        canvas.setFillColor(C(cnj.CIANO))
        canvas.setFont(F["bold"], 7.5)
        canvas.drawString(x_sep + 6 * mm, h - 10.5 * mm, f"PRÊMIO CNJ DE QUALIDADE {ano}")
        canvas.setFillColor(colors.white)
        canvas.setFont(F["xbold"], 17)
        canvas.drawString(x_sep + 6 * mm, h - 17.5 * mm, "Ficha Avaliativa")
        canvas.setFont(F["reg"], 8.5)
        canvas.setFillColor(C("#C9D6E3"))
        sub = f"{trib} · {info.get('Nome') or ''}"
        canvas.drawString(x_sep + 6 * mm, h - 22 * mm, sub[:110])
        # rodapé
        canvas.setStrokeColor(C("#DADDE2"))
        canvas.setLineWidth(0.6)
        canvas.line(MARGEM, 13 * mm, w - MARGEM, 13 * mm)
        _desenhar(canvas, logo_cor, MARGEM, 4.5 * mm, 26 * mm)
        canvas.setFont(F["reg"], 7)
        canvas.setFillColor(C(cnj.CINZA))
        canvas.drawCentredString(w / 2, 7.5 * mm, f"Gerado em {gerado} · Painel de Resultados — Prêmio CNJ de Qualidade")
        canvas.drawRightString(w - MARGEM, 7.5 * mm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buf, pagesize=PAGINA, leftMargin=MARGEM, rightMargin=MARGEM,
        topMargin=ALTURA_FAIXA + 7 * mm, bottomMargin=17 * mm,
        title=f"Ficha Avaliativa — {trib}", author="Conselho Nacional de Justiça",
        subject=f"Prêmio CNJ de Qualidade {ano}",
    )

    est = {
        "rot": ParagraphStyle("rot", fontName=F["bold"], fontSize=6.5, textColor=C(cnj.CINZA), leading=8),
        "val": ParagraphStyle("val", fontName=F["xbold"], fontSize=14, textColor=C(cnj.PRETO), leading=17),
        "val_p": ParagraphStyle("valp", fontName=F["bold"], fontSize=10, textColor=C(cnj.PRETO), leading=13),
        "sigla": ParagraphStyle("sigla", fontName=F["xbold"], fontSize=26, textColor=C(cnj.PRETO), leading=29),
        "nome": ParagraphStyle("nome", fontName=F["reg"], fontSize=9, textColor=C(cnj.CINZA), leading=12),
        "sec": ParagraphStyle("sec", fontName=F["bold"], fontSize=10, textColor=C(cnj.AZUL), leading=13,
                              spaceBefore=4, spaceAfter=5),
        "cab": ParagraphStyle("cab", fontName=F["semi"], fontSize=7.5, textColor=colors.white, leading=9),
        "cab_d": ParagraphStyle("cabd", fontName=F["semi"], fontSize=7.5, textColor=colors.white, leading=9,
                                alignment=TA_RIGHT),
        "cel": ParagraphStyle("cel", fontName=F["reg"], fontSize=7.4, textColor=C("#2A2E37"), leading=9.6),
        "cel_b": ParagraphStyle("celb", fontName=F["semi"], fontSize=7.4, textColor=C(cnj.MARINHO), leading=9.6),
        "num": ParagraphStyle("num", fontName=F["reg"], fontSize=7.4, leading=9.6, alignment=TA_RIGHT),
        "num_b": ParagraphStyle("numb", fontName=F["bold"], fontSize=7.4, leading=9.6, alignment=TA_RIGHT),
        "chip": ParagraphStyle("chip", fontName=F["bold"], fontSize=7, leading=9, alignment=TA_CENTER),
        "eixo_t": ParagraphStyle("eixot", fontName=F["semi"], fontSize=8, leading=10, textColor=C(cnj.PRETO)),
        "eixo_p": ParagraphStyle("eixop", fontName=F["reg"], fontSize=6.8, leading=9, textColor=C(cnj.CINZA)),
        "sec_tab": ParagraphStyle("sect", fontName=F["xbold"], fontSize=8.5, leading=11, textColor=C(cnj.MARINHO)),
        "sec_tab_d": ParagraphStyle("sectd", fontName=F["semi"], fontSize=7.5, leading=11,
                                    textColor=C("#3A3F4B"), alignment=TA_RIGHT),
    }
    P = Paragraph
    story = []

    # ---- identificação e indicadores
    premio = str(info.get("Premiação", ""))
    cor_premio = {"Excelência": cnj.MARINHO, "Diamante": cnj.CIANO, "Ouro": "#C9A227",
                  "Prata": "#A3A6AB"}.get(premio, "#DADDE2")
    txt_premio = "#FFFFFF" if premio in ("Excelência", "Diamante", "Ouro") else cnj.PRETO
    porte = str(info.get("Porte", "")).replace(str(info.get("Ramo", "")), "").strip() or info.get("Porte", "")

    def kpi(rotulo, valor, estilo="val"):
        return [P(rotulo.upper(), est["rot"]), P(valor, est[estilo])]

    selo = Table([[P(escape(premio), ParagraphStyle("s", parent=est["val_p"], textColor=C(txt_premio),
                                                     alignment=TA_CENTER))]],
                 style=[("BACKGROUND", (0, 0), (-1, -1), C(cor_premio)),
                        ("ROUNDEDCORNERS", [8, 8, 8, 8]), ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)])
    ident = [P(escape(trib), est["sigla"]), P(escape(str(info.get("Nome") or "")), est["nome"])]
    kpis = [
        [P("PREMIAÇÃO", est["rot"]), selo],
        kpi("Cumprimento", f"{num_br(info['Percentual'] * 100, 1)}%"),
        kpi("Pontuação", f"{num_br(info['Pontos'])} <font size=8 color='{cnj.CINZA}'>/ {num_br(info['Máximo'], 0)}</font>"),
        kpi("Ramo · Porte", f"{escape(str(info.get('Ramo', '')))} · {escape(str(porte))}", "val_p"),
    ]
    larg_kpi = [32 * mm, 32 * mm, 46 * mm, 52 * mm]
    t_kpi = Table([kpis], colWidths=larg_kpi)
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C("#F5F7FA")),
        ("BOX", (0, 0), (-1, -1), 0, colors.white),
        ("LINEAFTER", (0, 0), (-2, -1), 3, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    topo = Table([[ident, t_kpi]], colWidths=[largura_util - sum(larg_kpi), sum(larg_kpi)])
    topo.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [topo, Spacer(1, 5 * mm)]

    # ---- desempenho por eixo
    celulas, n = [], 0
    larg_eixo = (largura_util - 3 * 4 * mm) / 4
    for e, cor in zip(ordem_eixos, cores_eixos):
        if e not in por_eixo.index:
            continue
        p, m = por_eixo.loc[e, "Pontuação"], por_eixo.loc[e, "Máximo"]
        perc = p / m if m else 0
        bloco = Table(
            [[P(escape(e), est["eixo_t"]), P(f"<b>{num_br(perc * 100, 1)}%</b>", est["num_b"])],
             [BarraProgresso(perc, cor, larg_eixo - 32), ""],
             [P(f"{num_br(p)} de {num_br(m, 0)} pontos", est["eixo_p"]), ""]],
            colWidths=[larg_eixo * 0.68 - 8, larg_eixo * 0.32 - 8],
        )
        bloco.setStyle(TableStyle([
            ("SPAN", (0, 1), (1, 1)), ("SPAN", (0, 2), (1, 2)),
            ("BOX", (0, 0), (-1, -1), 0.6, C("#E3E6EB")), ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ]))
        celulas.append(bloco)
        n += 1
    if celulas:
        t_eixos = Table([celulas], colWidths=[larg_eixo + (4 * mm if i < n - 1 else 0) for i in range(n)])
        t_eixos.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                                     ("RIGHTPADDING", (-1, 0), (-1, 0), 0)]))
        story += [t_eixos, Spacer(1, 6 * mm)]

    # ---- quadro avaliativo
    titulo = "FICHA AVALIATIVA" + ("" if eixo_filtro == "Todos" else f" — {eixo_filtro.upper()}")
    story.append(P(titulo, est["sec"]))

    larg = [20 * mm, 52 * mm, 13 * mm, 17 * mm, 18 * mm, 16 * mm]
    larg.append(largura_util - sum(larg))
    cab = ["Inciso", "Descrição", "Alínea", "Máximo", "Pontuação", "Atingido", "Comentário"]
    dados = [[P(c, est["cab_d"] if c in ("Máximo", "Pontuação") else est["cab"]) for c in cab]]
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), C(cnj.MARINHO)),
        ("LINEBELOW", (0, 0), (-1, 0), 2, C(cnj.CIANO)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for e in [x for x in ordem_eixos if x in itens["Eixo"].unique()]:
        bloco = itens[itens["Eixo"] == e]
        p, m = bloco["Pontuação"].sum(), bloco["Máximo"].sum()
        r = len(dados)
        dados.append([P(escape(e), est["sec_tab"]), "", "", "", "", "",
                      P(f"{num_br(p)} de {num_br(m, 0)} pontos · {num_br(p / m * 100 if m else 0, 1)}%",
                        est["sec_tab_d"])])
        estilos += [("SPAN", (0, r), (5, r)), ("BACKGROUND", (0, r), (-1, r), C("#EEF1F5")),
                    ("LINEBELOW", (0, r), (-1, r), 0.6, C("#DADDE2"))]
        for _, it in bloco.iterrows():
            r = len(dados)
            fundo, texto = _cor_perc(it["Perc"])
            chip = "N/A" if pd.isna(it["Perc"]) else f"{num_br(it['Perc'] * 100, 0)}%"
            partes = _partes_comentario(str(it["Comentário"]).strip(), larg[-1] - 8, est["cel"])
            comentario = partes[0]
            dados.append([
                P(escape(str(it["Inciso"])), est["cel_b"]),
                P(escape(str(it["Descrição"])), est["cel"]),
                P(escape(str(it["Alínea"])), ParagraphStyle("a", parent=est["cel"], alignment=TA_CENTER)),
                P(num_br(it["Máximo"]), est["num"]),
                P(num_br(it["Pontuação"]), est["num_b"]),
                P(chip, ParagraphStyle("c", parent=est["chip"], textColor=C(texto))),
                P(comentario, est["cel"]),
            ])
            estilos.append(("BACKGROUND", (5, r), (5, r), C(fundo)))
            for parte in partes[1:]:  # continuação de comentários longos
                dados.append([P(f"{escape(str(it['Inciso']))}<br/><font color='{cnj.CINZA}' size=6.5>(cont.)</font>",
                                est["cel_b"]), "", "", "", "", "", P(parte, est["cel"])])
            estilos.append(("LINEBELOW", (0, len(dados) - 1), (-1, len(dados) - 1), 0.4, C("#E6E9EE")))

    quadro = Table(dados, colWidths=larg, repeatRows=1, splitByRow=1)
    quadro.setStyle(TableStyle(estilos))
    story.append(quadro)

    doc.build(story, onFirstPage=moldura, onLaterPages=moldura)
    return buf.getvalue()
