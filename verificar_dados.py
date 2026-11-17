"""Confere se os arquivos de dados estão no formato esperado pelo painel.

Uso (na pasta do painel):  python verificar_dados.py
"""

import ast
import re
import sys
from pathlib import Path

import pandas as pd

import historico

PASTA = Path(__file__).parent
codigo_app = (PASTA / "app.py").read_text(encoding="utf-8")


def constante(nome):
    m = re.search(rf"^{nome} = (.+)$", codigo_app, re.M)
    return ast.literal_eval(m.group(1)) if m else None


ANO = constante("ANO_EDICAO")
EXCLUIDOS = constante("EXCLUIDOS") or []
EIXOS = constante("ORDEM_EIXO") or []
PREMIOS = constante("ORDEM_PREMIO") or []
RAMOS = constante("ORDEM_RAMO") or []

problemas, avisos = [], []

# ---------------------------------------------------------------- base_final.xlsx
print(f"Ano da edição no painel (ANO_EDICAO): {ANO}")
print("\n[1] base_final.xlsx")
base = pd.read_excel(PASTA / "base_final.xlsx")
colunas = ["Tribunal", "Inciso", "Ordem", "Descrição", "Alínea", "Máximo", "Pontuação", "Nome_Completo",
           "Comentário", "Eixo", "Romano_num", "Ramo de Justiça", "Percentual Final", "Porte", "Premiação"]
faltando = [c for c in colunas if c not in base.columns]
if faltando:
    problemas.append(f"base_final.xlsx: colunas ausentes {faltando}")
else:
    base = base[~base["Tribunal"].isin(EXCLUIDOS)]
    print(f"  {base['Tribunal'].nunique()} tribunais, {len(base)} linhas de itens")
    for col, validos, nome in [("Eixo", EIXOS, "ORDEM_EIXO"), ("Premiação", PREMIOS, "ORDEM_PREMIO"),
                               ("Ramo de Justiça", RAMOS, "ORDEM_RAMO")]:
        novos = sorted(set(base[col].dropna().astype(str)) - set(validos))
        if novos:
            problemas.append(f"base_final.xlsx: valores de '{col}' não previstos em {nome} no app.py: {novos}")
    porte_ok = base["Porte"].dropna().astype(str).str.contains("Grande|Médio|Pequeno|Federal|Militar|Superior")
    if not porte_ok.all():
        avisos.append(f"Porte com valores inesperados: {sorted(set(base.loc[~porte_ok.reindex(base.index, fill_value=True), 'Porte']))}")
    sem_perc = base.groupby("Tribunal")["Percentual Final"].first().isna()
    if sem_perc.any():
        avisos.append(f"Tribunais sem 'Percentual Final' (será calculado pelos pontos): {sorted(sem_perc[sem_perc].index)}")

# ---------------------------------------------------------------- Serie_Completa.csv
print("\n[2] Serie_Completa.csv")
try:
    h = historico.carregar(PASTA / "Serie_Completa.csv", EXCLUIDOS)
    anos = sorted(h["Ano"].unique())
    print(f"  anos {anos[0]}–{anos[-1]}, {h['Tribunal'].nunique()} tribunais")
    if ANO not in anos:
        avisos.append(f"Serie_Completa.csv ainda não tem o ano {ANO}")
    ult = h[h["Ano"] == anos[-1]]
    sem_base = sorted(set(ult["Tribunal"]) - set(base["Tribunal"])) if "Tribunal" in base else []
    sem_hist = sorted(set(base["Tribunal"]) - set(ult["Tribunal"])) if "Tribunal" in base else []
    if sem_base:
        avisos.append(f"Tribunais no histórico de {anos[-1]} que não estão na base_final: {sem_base}")
    if sem_hist:
        avisos.append(f"Tribunais da base_final sem linha em {anos[-1]} no histórico: {sem_hist}")
    selos = sorted(set(h["Selo"].astype(str)) - set(historico.ORDEM_SELO))
    if selos:
        problemas.append(f"Serie_Completa.csv: selos não previstos em historico.ORDEM_SELO: {selos}")
    dup = h.duplicated(["Ano", "Tribunal"])
    if dup.any():
        problemas.append(f"Serie_Completa.csv: linhas duplicadas (Ano, Tribunal): {h.loc[dup, ['Ano', 'Tribunal']].values.tolist()[:10]}")
    if anos[-1] == ANO and "Tribunal" in base:
        comp = (ult.set_index("Tribunal")["Percentual"]
                .sub(base.groupby("Tribunal")["Percentual Final"].first()).abs().dropna())
        divergentes = comp[comp > 0.0015]
        if len(divergentes):
            avisos.append(f"Percentual de {ANO} diferente entre histórico e base_final: {sorted(divergentes.index)}")
except Exception as e:  # formato inválido
    problemas.append(f"Serie_Completa.csv não pôde ser lido: {e}")

# ---------------------------------------------------------------- fichas_pdf
pasta_fichas = PASTA / "fichas_pdf"
pdfs = list(pasta_fichas.glob("*.pdf")) if pasta_fichas.is_dir() else []
print(f"\n[3] fichas_pdf: {len(pdfs)} arquivos PDF")

print()
for a in avisos:
    print("  AVISO   ", a)
for p in problemas:
    print("  PROBLEMA", p)
if not avisos and not problemas:
    print("  Tudo certo.")
sys.exit(1 if problemas else 0)
