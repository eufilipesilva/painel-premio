"""Série histórica do Prêmio CNJ de Qualidade (Serie_Completa.csv)."""

import re

import pandas as pd

import identidade as cnj

ORDEM_SELO = ["Excelência", "Diamante", "Ouro", "Prata", "Bronze", "Sem Prêmio",
              "Desclassificado", "Não inscrito", "Não participou"]
SELOS_PREMIO = ["Excelência", "Diamante", "Ouro", "Prata", "Bronze"]
SEM_RESULTADO = ["Desclassificado", "Não inscrito", "Não participou"]
CORES_SELO = {
    "Excelência": cnj.MARINHO,
    "Diamante": cnj.CIANO,
    "Ouro": "#C9A227",
    "Prata": "#A3A6AB",
    "Bronze": "#A8703F",
    "Sem Prêmio": "#DADDE2",
    "Desclassificado": "#EBCFCB",
    "Não inscrito": "#F1F2F5",
    "Não participou": "#F7F8FA",
}
TEXTO_SELO_CLARO = {"Excelência", "Diamante", "Bronze"}  # selos com texto branco
ANOS_SEM_PERCENTUAL = {2015: "pontuação máxima de 2015 não informada na base"}


def sigla_padrao(sigla: str) -> str:
    """TREAC -> TRE-AC (mesmo padrão da base de 2025)."""
    m = re.fullmatch(r"TRE([A-Z]{2})", str(sigla).strip())
    return f"TRE-{m.group(1)}" if m else str(sigla).strip()


def carregar(caminho, excluidos=()) -> pd.DataFrame:
    h = pd.read_csv(caminho, sep=";", decimal=",", encoding="latin-1", index_col=0)
    h["Tribunal"] = h["Sigla"].map(sigla_padrao)
    h = h[~h["Tribunal"].isin(excluidos)].copy()

    selo = h["Selo"].replace({"Sem prêmio": "Sem Prêmio"})
    nao_participou = (~h["Original"].astype(bool)) | selo.isna() | (selo == "Sem Selo")
    h["Selo"] = selo.where(~nao_participou, "Não participou")

    # ramo ausente em alguma linha: usa o do próprio tribunal nos demais anos
    h["Justiça"] = h.groupby("Tribunal")["Justiça"].transform(
        lambda s: s.fillna(s.dropna().mode().iloc[0]) if s.notna().any() else s)

    valido = ~h["Selo"].isin(SEM_RESULTADO)
    h["Resultado"] = h["Resultado"].where(valido)
    h["Percentual"] = h["Percentual"].where(valido)
    h.loc[h["Ano"].isin(ANOS_SEM_PERCENTUAL), "Percentual"] = float("nan")

    h["Porte"] = h["Categoria"].str.extract(r"(Grande|Médio|Pequeno) Porte")[0]
    # posição no ramo em cada ano (anos sem percentual: pela pontuação, que tem escala única no ano)
    chave = h["Percentual"].where(~h["Ano"].isin(ANOS_SEM_PERCENTUAL), h["Resultado"])
    h["_chave"] = chave
    # comparação dentro do ramo de justiça (as categorias por porte não são estáveis na série)
    h["Posição"] = h.groupby(["Ano", "Justiça"])["_chave"].rank(ascending=False, method="min")
    h["Concorrentes"] = h.groupby(["Ano", "Justiça"])["_chave"].transform("count")
    h = h.drop(columns="_chave")
    h["Selo"] = pd.Categorical(h["Selo"], ORDEM_SELO, ordered=True)
    return h.sort_values(["Tribunal", "Ano"]).reset_index(drop=True)
