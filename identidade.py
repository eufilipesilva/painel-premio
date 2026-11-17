"""Identidade visual do CNJ (Manual de Uso da Marca, 2024).

Fonte: https://www.cnj.jus.br/sobre-o-cnj/logotipos-e-marcas/
Os arquivos originais (logotipos e manual em PDF) estão em assets/cnj/.
"""

import base64
import random
from functools import lru_cache
from pathlib import Path

PASTA = Path(__file__).parent / "assets" / "cnj"

# ---- cores principais da marca
PRETO = "#1a171b"
CINZA = "#707173"

# ---- cores de apoio
CIANO = "#00a4d6"
AZUL_MEDIO = "#348bc3"
AZUL = "#0f76b5"
AZUL_ESCURO = "#044e93"
MARINHO = "#0a243b"
VERDE_AGUA = "#009d94"

# ---- tons usados na textura padrão (amostrados do manual)
TEXTURA = ["#233160", "#2b3a63", "#165a9b", "#3a72ab", "#5a97d3", "#18628f"]

FONTE = "Montserrat"


@lru_cache
def logo_data_uri(versao: str = "cor") -> str:
    """Logotipo oficial em SVG. versao='cor' (fundos claros) ou 'branca' (fundos escuros)."""
    arquivo = PASTA / ("logo-cnj-cor.svg" if versao == "cor" else "logo-cnj-branca.svg")
    return "data:image/svg+xml;base64," + base64.b64encode(arquivo.read_bytes()).decode()


def _forma(x: int, y: int, s: int, tipo: int, rot: int) -> str:
    """Uma peça geométrica do padrão de texturas, dentro do quadrado (x, y, s)."""
    cantos = [(x, y), (x + s, y), (x + s, y + s), (x, y + s)]
    c0, c1, c2, c3 = (cantos[(i + rot) % 4] for i in range(4))
    if tipo == 0:  # quarto de círculo
        return f"M{c0[0]} {c0[1]} L{c1[0]} {c1[1]} A{s} {s} 0 0 1 {c3[0]} {c3[1]} Z"
    if tipo == 1:  # folha (dois arcos)
        return f"M{c1[0]} {c1[1]} A{s} {s} 0 0 1 {c3[0]} {c3[1]} A{s} {s} 0 0 1 {c1[0]} {c1[1]} Z"
    if tipo == 2:  # triângulo
        return f"M{c0[0]} {c0[1]} L{c1[0]} {c1[1]} L{c3[0]} {c3[1]} Z"
    if tipo == 3:  # semicírculo
        r = s / 2
        mx, my = (c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2
        return f"M{c0[0]} {c0[1]} A{r} {r} 0 0 0 {c1[0]} {c1[1]} L{mx} {my} Z"
    return ""


@lru_cache
def textura_svg(colunas: int = 12, linhas: int = 3, lado: int = 60, semente: int = 7) -> str:
    """Gera o padrão geométrico da identidade visual como SVG (data URI)."""
    rnd = random.Random(semente)
    w, h = colunas * lado, linhas * lado
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
              f'preserveAspectRatio="xMidYMid slice">']
    for i in range(colunas):
        for j in range(linhas):
            x, y = i * lado, j * lado
            fundo, cor = rnd.sample(TEXTURA, 2)
            partes.append(f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" fill="{fundo}"/>')
            tipo = rnd.choices([0, 1, 2, 3, 4, 5], weights=[4, 2, 2, 2, 1, 1])[0]
            if tipo <= 3:
                partes.append(f'<path d="{_forma(x, y, lado, tipo, rnd.randrange(4))}" fill="{cor}"/>')
            elif tipo == 4:  # círculo inteiro
                partes.append(f'<circle cx="{x + lado / 2}" cy="{y + lado / 2}" r="{lado / 2}" fill="{cor}"/>')
            if rnd.random() < 0.12:  # pequeno ponto
                ponto = rnd.choice(TEXTURA)
                partes.append(f'<circle cx="{x + lado / 2}" cy="{y + lado / 2}" r="{lado / 6}" fill="{ponto}"/>')
    partes.append("</svg>")
    svg = "".join(partes)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
