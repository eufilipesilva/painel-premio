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
| `dados/<ano>/base_final.xlsx` | Itens avaliativos da edição (uma linha por tribunal e item) |
| `dados/<ano>/fichas_pdf/` | Fichas oficiais em PDF da edição (opcional; a sigla do tribunal deve constar no nome do arquivo) |
| `Serie_Completa.csv` | Série histórica (`;`, vírgula decimal, latin-1) |
| `historia.py` | Texto da página Evolução do Prêmio |
| `app.py` | Painel |
| `edicoes.py` | Descoberta das edições em `dados/` (e em `simulacao/`, nos testes) |
| `ficha_pdf.py` | Geração do PDF da ficha |
| `historico.py` | Tratamento da série histórica |
| `identidade.py` | Cores, logotipos e textura do CNJ |
| `verificar_dados.py` | Conferência dos arquivos de dados |
| `simular_edicao.py` | Gera uma edição simulada para testes |
| `assets/` | Logotipos e manual do CNJ; fonte Montserrat (licença OFL) |

## Publicar uma nova edição (ex.: 2026)

1. Crie a pasta `dados/2026/` e coloque nela a planilha `base_final.xlsx` (mesmas colunas da de 2025).
2. (Opcional) Coloque as fichas oficiais em `dados/2026/fichas_pdf/`.
3. Rode `python verificar_dados.py` — deve terminar com "Tudo certo." ou só avisos.
4. Envie para o GitHub; o Streamlit Cloud atualiza sozinho.

Não é preciso mexer no código nem no `Serie_Completa.csv`: o painel passa a mostrar 2026 como edição
atual, a Ficha e o Percentual ganham o seletor de edição (2026/2025) e o Histórico recebe 2026 a partir
da própria planilha. Se um dia o ano entrar também no CSV, o CSV passa a valer para o histórico.

## Testar com dados simulados

```powershell
python simular_edicao.py                          # cria simulacao/2026/base_final.xlsx
$env:PAINEL_SIMULACAO = "1"; streamlit run app.py   # painel com a edição simulada
```

A edição simulada aparece com o selo amarelo "Dados simulados" no banner, "(simulação)" nos títulos,
"[SIMULAÇÃO]" nos comentários e no cabeçalho do PDF. A pasta `simulacao/` não vai para o GitHub, e sem a
variável `PAINEL_SIMULACAO` ela é ignorada — o painel publicado nunca a mostra. Para desligar no mesmo
terminal: `Remove-Item Env:PAINEL_SIMULACAO`.

Tribunais fora do painel: lista `EXCLUIDOS` em `app.py`.
