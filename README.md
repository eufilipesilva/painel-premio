# Painel de Resultados — Prêmio CNJ de Qualidade

Painel em Streamlit com a identidade visual do CNJ (Manual de Uso da Marca, 2024).

## Páginas

- **Ficha Avaliativa** — itens, pontuação e comentários de cada tribunal, com download em PDF e CSV.
- **Percentual de cumprimento** — percentual final por tribunal e premiação, por ramo e porte.
- **Histórico** — evolução de cada tribunal de 2014 em diante (selos, percentual e posição no ramo).
- **Evolução do Prêmio** — linha do tempo do Selo Justiça em Números e do Prêmio (texto em `historia.py`).

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `base_final.xlsx` | Itens avaliativos da edição atual (uma linha por tribunal e item) |
| `Serie_Completa.csv` | Série histórica (`;`, vírgula decimal, latin-1) |
| `historia.py` | Texto da página Evolução do Prêmio |
| `fichas_pdf/` | Fichas oficiais em PDF (opcional; a sigla do tribunal deve constar no nome do arquivo) |
| `app.py` | Painel |
| `ficha_pdf.py` | Geração do PDF da ficha |
| `historico.py` | Tratamento da série histórica |
| `identidade.py` | Cores, logotipos e textura do CNJ |
| `verificar_dados.py` | Conferência dos arquivos de dados |
| `assets/` | Logotipos e manual do CNJ; fonte Montserrat (licença OFL) |

## Atualizar para uma nova edição

1. Substitua `base_final.xlsx` (mesmas colunas).
2. Acrescente o novo ano em `Serie_Completa.csv`.
3. Ajuste `ANO_EDICAO` no início de `app.py`.
4. (Opcional) Coloque as fichas oficiais em `fichas_pdf/`.
5. Rode `python verificar_dados.py`.

Tribunais fora do painel: lista `EXCLUIDOS` em `app.py`.
