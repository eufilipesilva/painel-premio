"""Edições do Prêmio disponíveis no painel.

Cada edição fica numa pasta com o ano:

    dados/<ano>/base_final.xlsx   planilha da avaliação (mesmo formato de 2025)
    dados/<ano>/fichas_pdf/       fichas oficiais em PDF (opcional)

O painel mostra como edição atual o maior ano encontrado. Para publicar uma
nova edição basta criar a pasta do ano com a planilha — nada no código muda.

Simulação (só para testes locais): com a variável de ambiente
PAINEL_SIMULACAO=1, as pastas de simulacao/<ano>/ também entram e são
marcadas como "dados simulados" no painel.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).parent
PASTA_DADOS = RAIZ / "dados"
PASTA_SIMULACAO = RAIZ / "simulacao"
SIMULACAO = os.environ.get("PAINEL_SIMULACAO", "").strip().lower() in {"1", "true", "sim"}


@dataclass(frozen=True)
class Edicao:
    ano: int
    planilha: Path
    fichas: Path
    simulada: bool = False


def _planilha(pasta: Path):
    """base_final.xlsx, ou a única planilha .xlsx da pasta."""
    preferida = pasta / "base_final.xlsx"
    if preferida.is_file():
        return preferida
    xlsx = [f for f in sorted(pasta.glob("*.xlsx")) if not f.name.startswith("~$")]
    return xlsx[0] if len(xlsx) == 1 else None


def encontrar(simulacao: bool = SIMULACAO) -> dict:
    """{ano: Edicao}, em ordem crescente de ano."""
    raizes = [(PASTA_DADOS, False)] + ([(PASTA_SIMULACAO, True)] if simulacao else [])
    achadas = {}
    for raiz, simulada in raizes:
        if not raiz.is_dir():
            continue
        for pasta in raiz.iterdir():
            if not (pasta.is_dir() and re.fullmatch(r"20\d\d", pasta.name)):
                continue
            planilha = _planilha(pasta)
            if planilha is None:
                continue
            ano = int(pasta.name)
            # uma edição real tem prioridade sobre a simulada do mesmo ano
            if ano in achadas and not achadas[ano].simulada:
                continue
            achadas[ano] = Edicao(ano, planilha, pasta / "fichas_pdf", simulada)
    return dict(sorted(achadas.items()))
