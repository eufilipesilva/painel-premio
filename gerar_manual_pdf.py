"""Gera o PDF do manual (docs/MANUAL.md) com a identidade visual do CNJ.

Uso (na pasta do painel):
    python gerar_manual_pdf.py

Cria docs/MANUAL.pdf (versão atual) e a cópia versionada
docs/versoes/MANUAL_v<versão>_<AAAA-MM-DD>.pdf, lendo a versão e a data da linha
"**Versão X.Y — DD/MM/AAAA**" do início do manual.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

import identidade as cnj
from ficha_pdf import _desenhar, _fontes, _svg, _textura

BASE = Path(__file__).parent
ORIGEM = BASE / "docs" / "MANUAL.md"
W, H = A4
MARGEM = 18 * mm
FAIXA = 17 * mm
C = colors.HexColor
F = _fontes()
TEXTO = C("#33363D")
SUBST = {"🏠": "Casa"}  # caracteres sem glifo na Montserrat

# --------------------------------------------------------------------------- estilos
E = {
    "corpo": ParagraphStyle("corpo", fontName=F["reg"], fontSize=9.6, leading=14.6, textColor=TEXTO,
                            spaceAfter=5, alignment=TA_LEFT),
    "h2": ParagraphStyle("h2", fontName=F["xbold"], fontSize=17, leading=21, textColor=C(cnj.MARINHO)),
    "h3": ParagraphStyle("h3", fontName=F["bold"], fontSize=11.5, leading=15, textColor=C(cnj.AZUL),
                         spaceBefore=9, spaceAfter=5),
    "item": ParagraphStyle("item", fontName=F["reg"], fontSize=9.6, leading=14.2, textColor=TEXTO, spaceAfter=2.5),
    "cel": ParagraphStyle("cel", fontName=F["reg"], fontSize=8.4, leading=11.4, textColor=TEXTO),
    "cab": ParagraphStyle("cab", fontName=F["bold"], fontSize=8.2, leading=10.5, textColor=colors.white),
    "codigo": ParagraphStyle("codigo", fontName="Courier", fontSize=8.3, leading=11.2, textColor=C(cnj.MARINHO)),
    "toc1": ParagraphStyle("toc1", fontName=F["semi"], fontSize=10.5, leading=13.5, textColor=C(cnj.PRETO),
                           leftIndent=0, spaceBefore=2.5),
    "toc2": ParagraphStyle("toc2", fontName=F["reg"], fontSize=9, leading=11, textColor=TEXTO,
                           leftIndent=14, spaceBefore=0),
}


def inline(texto: str) -> str:
    """Markdown em linha -> marcação do ReportLab (negrito, código, links)."""
    for a, b in SUBST.items():
        texto = texto.replace(a, b)
    partes = re.split(r"(`[^`]+`)", texto)
    saida = []
    for p in partes:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            saida.append(f'<font face="Courier" color="{cnj.AZUL_ESCURO}">{escape(p[1:-1])}</font>')
            continue
        p = escape(p)
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<font color="{cnj.AZUL}">{m.group(1)}</font>', p)
        p = re.sub(r"\*\*(.+?)\*\*", lambda m: f'<font name="{F["bold"]}" color="{cnj.PRETO}">{m.group(1)}</font>', p)
        p = re.sub(r"(https?://[^\s<]+)", lambda m: f'<font color="{cnj.AZUL}">{m.group(1)}</font>', p)
        saida.append(p)
    return "".join(saida)


class Titulo(Flowable):
    """Título de seção: número em círculo ciano + texto marinho + fio."""

    def __init__(self, texto, largura, no_sumario=True):
        super().__init__()
        self.no_sumario = no_sumario
        m = re.match(r"(\d+)\.\s*(.*)", texto)
        self.num, self.txt = (m.group(1), m.group(2)) if m else ("", texto)
        self.texto_toc = texto
        self.width, self.height = largura, 15 * mm

    def draw(self):
        c = self.canv
        x = 0
        if self.num:
            c.setFillColor(C(cnj.MARINHO))
            c.roundRect(0, 4 * mm, 10 * mm, 10 * mm, 2.4 * mm, stroke=0, fill=1)
            c.setFillColor(C(cnj.CIANO))
            c.rect(0, 4 * mm, 1.3 * mm, 10 * mm, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont(F["xbold"], 13)
            c.drawCentredString(5.6 * mm, 7.3 * mm, self.num)
            x = 14 * mm
        c.setFillColor(C(cnj.MARINHO))
        c.setFont(F["xbold"], 17)
        c.drawString(x, 6.6 * mm, self.txt)
        c.setStrokeColor(C("#E3E6EB"))
        c.setLineWidth(0.8)
        c.line(0, 1 * mm, self.width, 1 * mm)
        c.setStrokeColor(C(cnj.CIANO))
        c.setLineWidth(2)
        c.line(0, 1 * mm, 22 * mm, 1 * mm)


def tabela(linhas, largura):
    celulas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas]
    celulas = [r for r in celulas if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    n = max(len(r) for r in celulas)
    celulas = [r + [""] * (n - len(r)) for r in celulas]
    pesos = [max(8, min(55, max(len(re.sub(r"[`*]", "", r[i])) for r in celulas))) for i in range(n)]
    if n == 2 and pesos[0] < 30:
        pesos[0] = max(pesos[0], 22)
    larguras = [largura * p / sum(pesos) for p in pesos]
    dados = [[Paragraph(inline(c), E["cab"] if i == 0 else E["cel"]) for c in r] for i, r in enumerate(celulas)]
    t = Table(dados, colWidths=larguras, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), C(cnj.MARINHO)),
        ("LINEBELOW", (0, 0), (-1, 0), 1.6, C(cnj.CIANO)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, C("#E3E6EB")),
        ("BOX", (0, 0), (-1, -1), 0.6, C("#DADDE2")),
    ]
    for i in range(1, len(dados)):
        if i % 2 == 0:
            estilo.append(("BACKGROUND", (0, i), (-1, i), C("#F5F7FA")))
    t.setStyle(TableStyle(estilo))
    return t


def bloco_codigo(linhas, largura):
    pre = Preformatted("\n".join(linhas), E["codigo"])
    t = Table([[pre]], colWidths=[largura])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C("#F1F4F8")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, C(cnj.AZUL)),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def marcador(nivel, numero=None):
    """(texto, cor) do marcador da lista."""
    if numero is not None:
        return f"{numero}.", C(cnj.AZUL)
    return ("•", C(cnj.CIANO)) if nivel == 0 else ("–", C(cnj.CINZA))


def sem_markdown(texto: str) -> str:
    return re.sub(r"[`*]", "", texto)


# --------------------------------------------------------------------------- leitura do markdown
def converter(md: str, largura: float):
    linhas = md.splitlines()
    titulo, versao, data = "Manual", "1.0", datetime.now().strftime("%d/%m/%Y")
    story, i, par = [], 0, []
    intro = None

    def fecha_par():
        if par:
            story.append(Paragraph(inline(" ".join(par)), E["corpo"]))
            par.clear()

    while i < len(linhas):
        l = linhas[i]
        s = l.strip()
        if s.startswith("# "):
            titulo = s[2:].strip()
        elif m := re.fullmatch(r"\*\*Versão\s+([\d.]+)\s+—\s+([\d/]+)\*\*", s):
            versao, data = m.group(1), m.group(2)
        elif s == "---" or not s:
            fecha_par()
        elif s.startswith("## "):
            fecha_par()
            if intro is None:
                intro, story = story, []
            if story:
                story.append(PageBreak())
            story.append(Titulo(s[3:].strip(), largura))
            story.append(Spacer(1, 3 * mm))
        elif s.startswith("### "):
            fecha_par()
            story.append(CondPageBreak(30 * mm))
            p = Paragraph(inline(s[4:].strip()), E["h3"])
            p._toc = sem_markdown(s[4:].strip())
            story.append(p)
        elif s.startswith("```"):
            fecha_par()
            bloco, i = [], i + 1
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                bloco.append(linhas[i])
                i += 1
            story.append(Spacer(1, 1.5 * mm))
            story.append(bloco_codigo(bloco, largura))
            story.append(Spacer(1, 2.5 * mm))
        elif s.startswith("|"):
            fecha_par()
            recuo = len(l) - len(l.lstrip())
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                bloco.append(linhas[i])
                i += 1
            esq = 9 * mm if recuo else 0
            t = tabela(bloco, largura - esq)
            if esq:
                t.hAlign = "RIGHT"
            story.append(Spacer(1, 1.5 * mm))
            story.append(t)
            story.append(Spacer(1, 3 * mm))
            continue
        elif m := re.match(r"(\s*)(-|\d+\.)\s+(.*)", l):
            fecha_par()
            nivel = len(m.group(1)) // 2
            numero = m.group(2)[:-1] if m.group(2)[0].isdigit() else None
            texto = m.group(3)
            # linhas de continuação (recuadas, sem novo marcador)
            while (i + 1 < len(linhas) and linhas[i + 1].startswith(" " * (2 * nivel + 2))
                   and not re.match(r"\s*(-|\d+\.)\s+|\s*\|", linhas[i + 1])):
                i += 1
                texto += " " + linhas[i].strip()
            recuo = 5 * mm + nivel * 6 * mm
            simbolo, cor = marcador(nivel, numero)
            est = ParagraphStyle("li", parent=E["item"], leftIndent=recuo, bulletIndent=recuo - 4.2 * mm,
                                 bulletFontName=F["bold"], bulletColor=cor,
                                 bulletFontSize=11 if numero is None else 9.6)
            story.append(Paragraph(inline(texto), est, bulletText=simbolo))
        else:
            par.append(s)
        i += 1
    fecha_par()
    return titulo, versao, data, intro or [], story


# --------------------------------------------------------------------------- documento
class Documento(BaseDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, Titulo) and f.no_sumario:
            self.notify("TOCEntry", (0, sem_markdown(f.texto_toc), self.page))
        elif isinstance(f, Paragraph) and getattr(f, "_toc", None):
            self.notify("TOCEntry", (1, f._toc, self.page))


def gerar(destinos):
    md = ORIGEM.read_text(encoding="utf-8")
    largura = W - 2 * MARGEM
    titulo, versao, data, intro, corpo = converter(md, largura)
    logo_branca = _svg(str(cnj.PASTA / "logo-cnj-branca.svg"))
    logo_cor = _svg(str(cnj.PASTA / "logo-cnj-cor.svg"))
    textura = _textura()
    rotulo = f"Manual do Painel de Resultados · versão {versao}"

    def capa(c, doc):
        c.saveState()
        c.setFillColor(C(cnj.MARINHO))
        c.rect(0, 0, W, H, stroke=0, fill=1)
        # textura geométrica na metade inferior, esmaecendo para cima
        alt_tex = H * 0.42
        p = c.beginPath()
        p.rect(0, 0, W, alt_tex)
        c.saveState()
        c.clipPath(p, stroke=0, fill=0)
        esc_larg = W * 2.2
        _desenhar(c, textura, -W * 0.15, -8 * mm, esc_larg)
        c.restoreState()
        for k in range(60):
            c.setFillColor(C(cnj.MARINHO), alpha=1 - k / 60)
            c.rect(0, alt_tex - (k + 1) * alt_tex / 60 * 0.75, W, alt_tex / 60 * 0.75 + 0.6, stroke=0, fill=1)
        # logotipo branco com área de proteção
        _desenhar(c, logo_branca, MARGEM + 4 * mm, H - 44 * mm, 62 * mm)
        x = MARGEM + 4 * mm
        d = 22 * mm  # deslocamento do bloco de títulos
        c.setFillColor(C(cnj.CIANO))
        c.rect(x, H - 92 * mm - d, 2 * mm, 52 * mm, stroke=0, fill=1)
        c.setFont(F["bold"], 10)
        c.drawString(x + 8 * mm, H - 50 * mm - d, "PRÊMIO CNJ DE QUALIDADE")
        c.setFillColor(colors.white)
        c.setFont(F["xbold"], 30)
        c.drawString(x + 8 * mm, H - 64 * mm - d, "Manual do Painel")
        c.drawString(x + 8 * mm, H - 76 * mm - d, "de Resultados")
        c.setFont(F["reg"], 12)
        c.setFillColor(C("#C9D6E3"))
        c.drawString(x + 8 * mm, H - 87 * mm - d, "Funcionalidades, dados e manutenção")
        # selo de versão
        c.setFillColor(colors.white)
        c.roundRect(x + 8 * mm, H - 114 * mm - d, 58 * mm, 14 * mm, 7 * mm, stroke=0, fill=1)
        c.setFillColor(C(cnj.MARINHO))
        c.setFont(F["xbold"], 11)
        c.drawCentredString(x + 37 * mm, H - 108.5 * mm - d, f"Versão {versao} · {data}")
        c.setFillColor(C("#C9D6E3"))
        c.setFont(F["reg"], 8.5)
        c.drawString(MARGEM + 4 * mm, 14 * mm, "Conselho Nacional de Justiça · Documento de manutenção do painel")
        c.restoreState()

    def interna(c, doc):
        c.saveState()
        c.setFillColor(C(cnj.MARINHO))
        c.rect(0, H - FAIXA, W, FAIXA, stroke=0, fill=1)
        p = c.beginPath()
        p.rect(W * 0.6, H - FAIXA, W * 0.4, FAIXA)
        c.saveState()
        c.clipPath(p, stroke=0, fill=0)
        _desenhar(c, textura, W * 0.6, H - FAIXA - 4, W * 0.4 + 2)
        c.restoreState()
        for k in range(40):
            c.setFillColor(C(cnj.MARINHO), alpha=1 - k / 40)
            c.rect(W * 0.6 + k * W * 0.4 / 40, H - FAIXA, W * 0.4 / 40 + 0.5, FAIXA, stroke=0, fill=1)
        _desenhar(c, logo_branca, MARGEM, H - FAIXA + 4.2 * mm, 30 * mm)
        c.setStrokeColor(C(cnj.CIANO))
        c.setLineWidth(1)
        c.line(MARGEM + 34 * mm, H - FAIXA + 4 * mm, MARGEM + 34 * mm, H - 4 * mm)
        c.setFillColor(C(cnj.CIANO))
        c.setFont(F["bold"], 6.5)
        c.drawString(MARGEM + 38 * mm, H - 8.2 * mm, "PRÊMIO CNJ DE QUALIDADE")
        c.setFillColor(colors.white)
        c.setFont(F["semi"], 8.5)
        c.drawString(MARGEM + 38 * mm, H - 12.6 * mm, rotulo)
        # rodapé
        c.setStrokeColor(C("#DADDE2"))
        c.setLineWidth(0.6)
        c.line(MARGEM, 14 * mm, W - MARGEM, 14 * mm)
        _desenhar(c, logo_cor, MARGEM, 5 * mm, 22 * mm)
        c.setFont(F["reg"], 7)
        c.setFillColor(C(cnj.CINZA))
        c.drawCentredString(W / 2, 8 * mm, f"Versão {versao} · {data}")
        c.setFont(F["bold"], 8)
        c.setFillColor(C(cnj.MARINHO))
        c.drawRightString(W - MARGEM, 8 * mm, str(doc.page))
        c.restoreState()

    sumario = TableOfContents(levelStyles=[E["toc1"], E["toc2"]], dotsMinLevel=0)
    abertura = [
        NextPageTemplate("interna"), PageBreak(),
        Titulo("Sumário", largura, no_sumario=False), Spacer(1, 2 * mm), sumario,
        Spacer(1, 3 * mm),
        KeepTogether([Paragraph("Sobre este documento", E["h3"]), *intro]),
        PageBreak(),
    ]
    for destino in destinos[:1]:
        destino.parent.mkdir(parents=True, exist_ok=True)
        doc = Documento(str(destino), pagesize=A4, leftMargin=MARGEM, rightMargin=MARGEM,
                        topMargin=FAIXA + 10 * mm, bottomMargin=20 * mm,
                        title=titulo, author="Conselho Nacional de Justiça",
                        subject=f"Prêmio CNJ de Qualidade — versão {versao}")
        quadro = Frame(MARGEM, 20 * mm, largura, H - FAIXA - 30 * mm, id="q", leftPadding=0, rightPadding=0,
                       topPadding=0, bottomPadding=0)
        doc.addPageTemplates([PageTemplate("capa", [Frame(0, 0, W, H, id="c")], onPage=capa),
                              PageTemplate("interna", [quadro], onPage=interna)])
        doc.multiBuild(list(abertura) + list(corpo))
    for destino in destinos[1:]:  # cópias (ex.: versão arquivada)
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(destinos[0], destino)
    return versao, data


if __name__ == "__main__":
    md = ORIGEM.read_text(encoding="utf-8")
    _, v, d, _, _ = converter(md, 100)
    iso = datetime.strptime(d, "%d/%m/%Y").strftime("%Y-%m-%d")
    alvos = [BASE / "docs" / "MANUAL.pdf", BASE / "docs" / "versoes" / f"MANUAL_v{v}_{iso}.pdf"]
    gerar(alvos)
    for a in alvos:
        print("PDF gerado:", a.relative_to(BASE))
