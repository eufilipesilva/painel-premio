"""Confere se os arquivos de dados estão no formato esperado pelo painel.

Uso (na pasta do painel):
    python verificar_dados.py               # edições reais (dados/<ano>/)
    python verificar_dados.py --simulacao   # inclui as edições simuladas (simulacao/<ano>/)
"""

import ast
import re
import sys
from pathlib import Path

import pandas as pd

import edicoes
import historico

PASTA = Path(__file__).parent
codigo_app = (PASTA / "app.py").read_text(encoding="utf-8")


def constante(nome):
    m = re.search(rf"^{nome} = (.+)$", codigo_app, re.M)
    return ast.literal_eval(m.group(1)) if m else None


EXCLUIDOS = constante("EXCLUIDOS") or []
EIXOS = constante("ORDEM_EIXO") or []
PREMIOS = constante("ORDEM_PREMIO") or []
RAMOS = constante("ORDEM_RAMO") or []
COLUNAS = ["Tribunal", "Inciso", "Ordem", "Descrição", "Alínea", "Máximo", "Pontuação", "Nome_Completo",
           "Comentário", "Eixo", "Romano_num", "Ramo de Justiça", "Percentual Final", "Porte", "Premiação"]

problemas, avisos = [], []
EDICOES = edicoes.encontrar(simulacao=edicoes.SIMULACAO or "--simulacao" in sys.argv)
if not EDICOES:
    print("Nenhuma edição encontrada: crie dados/<ano>/base_final.xlsx")
    sys.exit(1)
ANO = max(EDICOES)
print("Edições encontradas: " + ", ".join(
    f"{a}{' (simulada)' if e.simulada else ''}" for a, e in EDICOES.items()))
print(f"Edição atual do painel: {ANO}")

# ---------------------------------------------------------------- planilhas das edições
bases, linhas_hist = {}, []
for i, (ano, ed) in enumerate(EDICOES.items(), 1):
    print(f"\n[{i}] {ed.planilha.relative_to(PASTA)}")
    base = pd.read_excel(ed.planilha)
    faltando = [c for c in COLUNAS if c not in base.columns]
    if faltando:
        problemas.append(f"{ano}: colunas ausentes {faltando}")
        continue
    linhas_hist.append(historico.linhas_da_edicao(base, ano))
    base = base[~base["Tribunal"].isin(EXCLUIDOS)]
    bases[ano] = base
    print(f"  {base['Tribunal'].nunique()} tribunais, {len(base)} linhas de itens")
    for col, validos, nome in [("Eixo", EIXOS, "ORDEM_EIXO"), ("Premiação", PREMIOS, "ORDEM_PREMIO"),
                               ("Ramo de Justiça", RAMOS, "ORDEM_RAMO")]:
        novos = sorted(set(base[col].dropna().astype(str)) - set(validos))
        if novos:
            problemas.append(f"{ano}: valores de '{col}' não previstos em {nome} no app.py: {novos}")
    porte = base["Porte"].dropna().astype(str)
    porte_ruim = sorted(set(porte[~porte.str.contains("Grande|Médio|Pequeno|Federal|Militar|Superior")]))
    if porte_ruim:
        avisos.append(f"{ano}: Porte com valores inesperados: {porte_ruim}")
    sem_perc = base.groupby("Tribunal")["Percentual Final"].first().isna()
    if sem_perc.any():
        avisos.append(f"{ano}: tribunais sem 'Percentual Final' (será calculado pelos pontos): "
                      f"{sorted(sem_perc[sem_perc].index)}")
    acima = base[base["Pontuação"] > base["Máximo"] + 1e-9]
    if len(acima):
        problemas.append(f"{ano}: itens com pontuação acima do máximo: "
                         f"{acima[['Tribunal', 'Inciso', 'Alínea']].values.tolist()[:10]}")
    pdfs = list(ed.fichas.glob("*.pdf")) if ed.fichas.is_dir() else []
    print(f"  fichas oficiais em PDF: {len(pdfs)}")

# ---------------------------------------------------------------- Serie_Completa.csv
print("\n[série] Serie_Completa.csv + edições")
try:
    csv = pd.read_csv(PASTA / "Serie_Completa.csv", sep=";", decimal=",", encoding="latin-1", index_col=0)
    anos_csv = set(csv["Ano"].unique())
    for ano in EDICOES:
        if ano not in anos_csv:
            print(f"  {ano}: não está no CSV — entra pela planilha da edição")
    h = historico.carregar(PASTA / "Serie_Completa.csv", EXCLUIDOS, linhas_hist)
    anos = sorted(h["Ano"].unique())
    print(f"  anos {anos[0]}–{anos[-1]}, {h['Tribunal'].nunique()} tribunais")
    selos = sorted(set(h["Selo"].astype(str)) - set(historico.ORDEM_SELO))
    if selos:
        problemas.append(f"Série: selos não previstos em historico.ORDEM_SELO: {selos}")
    dup = h.duplicated(["Ano", "Tribunal"])
    if dup.any():
        problemas.append(f"Série: linhas duplicadas (Ano, Tribunal): {h.loc[dup, ['Ano', 'Tribunal']].values.tolist()[:10]}")
    for ano, base in bases.items():
        if ano not in anos_csv:
            continue
        # ano presente nos dois lugares: o CSV vale para o histórico; confere se bate com a planilha
        ult = h[h["Ano"] == ano].set_index("Tribunal")
        sem_base = sorted(set(ult.index) - set(base["Tribunal"]))
        sem_hist = sorted(set(base["Tribunal"]) - set(ult.index))
        if sem_base:
            avisos.append(f"{ano}: tribunais no CSV que não estão na planilha: {sem_base}")
        if sem_hist:
            avisos.append(f"{ano}: tribunais da planilha sem linha no CSV: {sem_hist}")
        comp = ult["Percentual"].sub(base.groupby("Tribunal")["Percentual Final"].first()).abs().dropna()
        divergentes = comp[comp > 0.0015]
        if len(divergentes):
            avisos.append(f"{ano}: percentual diferente entre CSV e planilha: {sorted(divergentes.index)}")
except Exception as e:  # formato inválido
    problemas.append(f"Serie_Completa.csv não pôde ser lido: {e}")

print()
for a in avisos:
    print("  AVISO   ", a)
for p in problemas:
    print("  PROBLEMA", p)
if not avisos and not problemas:
    print("  Tudo certo.")
sys.exit(1 if problemas else 0)
