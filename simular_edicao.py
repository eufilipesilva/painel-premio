"""Gera uma edição SIMULADA a partir da edição real mais recente (só para testar o painel).

Uso (na pasta do painel):
    python simular_edicao.py            # cria simulacao/2026/base_final.xlsx a partir de dados/2025
    python simular_edicao.py 2027       # outro ano

Para ver a simulação no painel (PowerShell):
    $env:PAINEL_SIMULACAO = "1"; streamlit run app.py

A pasta simulacao/ não vai para o GitHub (.gitignore), então o painel publicado nunca a mostra.
A planilha gerada tem exatamente as mesmas colunas da original: os pontos de cada item mudam
aleatoriamente (semente fixa), o percentual final é recalculado e as premiações são redistribuídas
dentro de cada ramo, mantendo a quantidade de cada selo da edição de origem.
"""

import sys

import numpy as np
import pandas as pd

import edicoes

reais = edicoes.encontrar(simulacao=False)
origem = reais[max(reais)]
ano = int(sys.argv[1]) if len(sys.argv) > 1 else origem.ano + 1
rng = np.random.default_rng(ano)

base = pd.read_excel(origem.planilha)
colunas = list(base.columns)

# tendência própria de cada tribunal + ruído por item
tendencia = {t: rng.normal(0.02, 0.07) for t in base["Tribunal"].unique()}
maximo = base["Máximo"].astype(float)
atual = (base["Pontuação"] / maximo.where(maximo > 0)).fillna(0)
novo = (atual + base["Tribunal"].map(tendencia) + rng.normal(0, 0.12, len(base))).clip(0, 1)
# notas em degraus de 5% do máximo, como nas fichas reais
base["Pontuação"] = (np.round(novo * 20) / 20 * maximo).round(2).where(maximo > 0, base["Pontuação"])
if "PontCheck" in base:
    base["PontCheck"] = base["Pontuação"]
base["Comentário"] = "[SIMULAÇÃO] " + base["Comentário"].fillna("").astype(str)

# percentual final e premiação (somente tribunais classificados na origem)
pts = base.groupby("Tribunal").agg(P=("Pontuação", "sum"), M=("Máximo", "sum"),
                                   Ramo=("Ramo de Justiça", "first"), Premio=("Premiação", "first"),
                                   Perc=("Percentual Final", "first"))
classificados = pts["Premio"].notna() & pts["Perc"].notna()
pts.loc[classificados, "Perc"] = (pts["P"] / pts["M"]).round(3)
ordem = ["Excelência", "Diamante", "Ouro", "Prata", "Sem Prêmio"]
for ramo, grupo in pts[classificados].groupby("Ramo"):
    selos = sorted(grupo["Premio"], key=ordem.index)
    pts.loc[grupo.sort_values("Perc", ascending=False).index, "Premio"] = selos
base["Percentual Final"] = base["Tribunal"].map(pts["Perc"])
base["Premiação"] = base["Tribunal"].map(pts["Premio"])

destino = edicoes.PASTA_SIMULACAO / str(ano)
destino.mkdir(parents=True, exist_ok=True)
base[colunas].to_excel(destino / "base_final.xlsx", index=False)
print(f"Edição simulada {ano} gerada em {destino / 'base_final.xlsx'} (origem: {origem.planilha})")
print(pts[classificados].sort_values("Perc", ascending=False)[["Ramo", "Perc", "Premio"]].head(8).to_string())
