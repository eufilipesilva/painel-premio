# Manual do Painel de Resultados — Prêmio CNJ de Qualidade

**Versão 1.10 — 18/11/2026**

Este documento é para quem for manter o painel: atualizar dados, ajustar textos, corrigir algo ou
acrescentar funcionalidades. Ele descreve o que o painel faz, de onde vem cada informação e onde cada coisa
está no código.

A versão atual fica sempre neste arquivo (`docs/MANUAL.md`) e no PDF `docs/MANUAL.pdf`. Cada versão
fica guardada em `docs/versoes/`, em Markdown e em PDF. O histórico de mudanças está no fim.

---

## 1. Visão geral

| Item | Valor |
|---|---|
| Tecnologia | Python + Streamlit 1.50 (gráficos em Plotly, PDF em ReportLab) |
| Código | `app.py` (painel) e módulos auxiliares na mesma pasta |
| Repositório | https://github.com/eufilipesilva/painel-premio (ramo `main`) |
| Publicação | Streamlit Community Cloud, que atualiza sozinho a cada envio ao GitHub |
| Identidade visual | Manual de Uso da Marca do CNJ (2024): cores oficiais, logotipos e fonte Montserrat |
| Edição atual | Maior ano encontrado em `dados/` (hoje, **2025**) |

### Rodar no computador

```powershell
pip install -r requirements.txt
streamlit run app.py              # abre em http://localhost:8501
```

### Navegação

- No topo há quatro botões de página, que ocupam a largura do banner. Não há barra lateral nem filtros globais.
- Logo abaixo fica o banner azul com o logotipo branco do CNJ e o título "Painel de Resultados {edição atual}".
- No rodapé ficam a textura geométrica, o logotipo colorido e a edição atual.
- Em todas as páginas há dois botões flutuantes no canto inferior direito: 🏠 (início) e ↑ (topo).

---

## 2. Páginas

### 2.1 Ficha Avaliativa

Mostra a avaliação completa de um tribunal na **última edição inserida**, que é o maior ano em `dados/`. A Ficha não tem seletor de edição: quando a pasta de um ano novo é publicada, ela passa a mostrar esse ano.

| Elemento | O que faz |
|---|---|
| Ramo de justiça | Escolhe o ramo. A lista de tribunais embaixo muda conforme o ramo. |
| Tribunal | Botões com as siglas do ramo, em ordem natural (TRT2 antes de TRT10). |
| Eixo | Todos, Governança, Produtividade, Transparência ou Dados e Tecnologia. Filtra o quadro. |
| Cabeçalho | Sigla, nome completo, selo da premiação, % de cumprimento, pontos/máximo, ramo e porte. |
| Barras por eixo | % de cada eixo, com os pontos obtidos sobre o máximo. |
| Quadro avaliativo | Uma linha por item: inciso, descrição, alínea, ordem, máximo, pontuação, % atingido e comentário. Há uma linha de subtotal por eixo. |
| Baixar ficha (PDF) | Se houver a ficha oficial em `dados/<ano>/fichas_pdf/`, baixa esse arquivo. Se não houver, gera o PDF no padrão do CNJ. |
| Baixar ficha (CSV) | Exporta os itens exibidos (`;`, vírgula decimal, UTF-8). |

Cores do "% atingido": verde = 100%; azul = 50% a 99%; vermelho = abaixo de 50%; cinza = não se aplica.

**PDF gerado** (`ficha_pdf.py`):

- A4 paisagem.
- Faixa azul com o logotipo branco e "PRÊMIO CNJ DE QUALIDADE {ano}".
- Indicadores, barras por eixo e a tabela de itens. Comentários longos continuam em linhas "(cont.)".
- Rodapé com o logotipo colorido e a numeração de páginas.

**Ficha oficial:** o nome do arquivo precisa conter a sigla do tribunal. Exemplos aceitos: `TJAC.pdf`,
`Ficha_TRE-AC.pdf`, `TRT_01.pdf`. Zeros à esquerda e separadores são ignorados.

### 2.2 Percentual de cumprimento

Gráfico de barras horizontais com o percentual final de cada tribunal na **última edição inserida**.
A cor da barra é a premiação.

- Filtros, lado a lado numa só linha: **Ramo de justiça** e **Porte** (Todos, Grande, Médio ou Pequeno,
  quando o ramo tem porte; começa em Grande). Não há seletor de edição.
- O valor aparece dentro de cada barra, em negrito. A legenda das premiações fica abaixo do gráfico.
- A legenda acima do gráfico informa o grupo, a quantidade de tribunais e a média do grupo.
- Ao passar o mouse aparecem o nome completo, o percentual, os pontos e a premiação.

### 2.3 Histórico

Análise da trajetória de um tribunal de 2014 até a edição atual.

| Elemento | O que faz |
|---|---|
| Ramo de justiça / Porte ({edição atual}) / Tribunal | Seleção do tribunal. O porte é o da edição atual e serve só para filtrar, porque muda ao longo dos anos. |
| Indicadores | Resultado da última edição (com selo e posição no ramo), variação em p.p. em relação ao ano anterior, melhor resultado, média histórica e total de premiações. |
| Linha do tempo | Um cartão por ano com selo, % e posição no ramo, em duas fases com cabeçalho: **Selo Justiça em Números 2014–2019** e **Prêmio CNJ de Qualidade 2020–…**. |
| Carrossel do Prêmio | A fase do Prêmio mostra as **5 edições mais recentes**. A seta ‹ à esquerda recua para as anteriores e a seta › volta. Feito só com HTML e CSS (veja a seção 4.6). |
| Evolução do percentual | Linha do tribunal comparada com a média e o melhor resultado do ramo, ano a ano. |
| Posição no ramo | Posição do tribunal no ramo em cada ano (1º = melhor). |
| Selos do ramo por ano | Colunas empilhadas com a quantidade de tribunais em cada selo. Os anos ficam em ordem crescente e o selo mais alto fica no topo da pilha. |
| Panorama histórico | Mapa de calor tribunais × anos do ramo (e do porte, se filtrado). A cor é o selo e o número é o %, com uma casa decimal. |
| Série histórica do tribunal | Tabela ano a ano com download em CSV. |

**Regras de comparação:**

- A comparação é sempre **dentro do ramo**, nunca por categoria ou porte. As categorias por porte só
  existem a partir de 2025, e o porte de um tribunal muda com o tempo.
- **2015:** a base não tem a pontuação máxima, então o percentual fica vazio e o cartão mostra os pontos.
  A posição no ramo de 2015 é calculada pela pontuação.
- **Sem resultado:** "Não participou", "Não inscrito" e "Desclassificado" contam como sem resultado. Não
  entram em médias nem em posições.

### 2.4 Evolução do Prêmio

Linha do tempo histórica do Selo e do Prêmio, com um menu lateral que acompanha a rolagem e leva a cada ano.

- **Ordem:** decrescente, com o mais recente primeiro. Primeiro vem a fase "Maturidade e Inteligência" (2026–2027 até 2019),
  depois a fase do Selo (2015 a 2018 e 2013). O menu de navegação rápida segue a mesma ordem.
- **Para incluir um ano novo:** em `historia.py`, copie um bloco `<div class="timeline-item" id="ano-…">` e coloque-o
  **no topo** da fase. Acrescente o link `#ano-…` correspondente no início do menu (`menu_html`). O id do bloco e o
  `href` do link precisam ser iguais.
- **Imagens dos cartões:** ficam em `static/historia/`. O painel serve essa pasta (`enableStaticServing` em
  `.streamlit/config.toml`). Arquivos de cada cartão (todos já estão na pasta):

  | Cartão | Arquivo |
  |---|---|
  | 2026 – 2027 | `2026-2027.png` (arte no padrão do banner do painel) |
  | 2024 a 2025 | `2024-2025.jpg` |
  | 2021 a 2022 | `2021-2022.jpg` |
  | 2020 | `2020.jpg` |
  | 2019 | `2019.jpg` |
  | 2015 a 2018 | `2015-2018.jpg` |
  | 2013 | `2013.png` (selo inteiro centralizado sobre fundo marinho, em 4:3) |

  - **Trocar ou incluir uma imagem:** basta salvar o arquivo na pasta com o nome da tabela e enviar para o
    GitHub. O formato pode ser JPG, JPEG, PNG ou WEBP: o painel aceita qualquer um com o mesmo nome (ex.:
    `2019.png`). Prefira a proporção 4:3 (ex.: 800 × 600) e menos de 500 KB.
  - **Enquanto o arquivo não existir:** o cartão aparece só com texto, sem ícone de imagem quebrada. Quem faz
    isso é a função `_imagens_historia` em `app.py`.
  - **Cartão novo:** em `historia.py`, coloque como primeira linha dentro de `<div class="timeline-card">`:
    `<img src="app/static/historia/NOME.jpg" class="timeline-img" alt="descrição">`. Use nomes sem espaços nem acentos.
  - **Enquadramento:** toda imagem preenche um quadro 4:3 com cantos arredondados (`object-fit: cover`). Imagens
    em outra proporção são cortadas pelo centro. Para mostrar uma imagem vertical inteira, componha-a antes num
    quadro 4:3, como foi feito com o selo de 2013.
    A regra usa `!important` porque o Streamlit aplica `scale-down` às imagens do markdown.

- **O texto foi escrito manualmente e não deve ser alterado pelo painel.**
- O conteúdo fica em `historia.py`. O painel lê os textos desse arquivo sem executá-lo e aplica apenas o
  estilo visual (`CSS_EVOLUCAO` em `app.py`).
- Para mudar um texto ou uma imagem, edite `historia.py`. Para mudar a aparência, edite `CSS_EVOLUCAO`.

---

## 3. Dados

### 3.1 Estrutura de pastas

```
dados/
  2025/
    base_final.xlsx      planilha da edição (obrigatória)
    fichas_pdf/          fichas oficiais em PDF (opcional)
  2026/ ...              próxima edição: mesma estrutura
Serie_Completa.csv       série histórica 2014–2025
historia.py              texto da página Evolução do Prêmio
static/historia/         imagens dos cartões da Evolução do Prêmio
simulacao/               edições simuladas (só local; não vai para o GitHub)
```

### 3.2 Planilha da edição (`dados/<ano>/base_final.xlsx`)

A planilha tem uma linha por tribunal × item avaliativo. Estas colunas são obrigatórias (e conferidas pelo
`verificar_dados.py`):

| Coluna | Uso |
|---|---|
| Tribunal | Sigla (ex.: TJAC, TRE-AC, TRT8) |
| Nome_Completo | Nome exibido abaixo da sigla |
| Ramo de Justiça | Estadual, Trabalho, Eleitoral, Federal, Militar Estadual ou Superior |
| Porte | Ex.: "Estadual Pequeno", "Trabalho Grande", "Federal" |
| Premiação | Excelência, Diamante, Ouro, Prata ou Sem Prêmio |
| Percentual Final | % oficial (0 a 1). Se estiver vazio, o painel calcula pontos ÷ máximo. |
| Eixo | Governança, Produtividade, Transparência ou Dados e Tecnologia |
| Inciso, Romano_num, Ordem, Alínea, Descrição | Identificação e ordenação dos itens |
| Máximo, Pontuação | Pontos possíveis e obtidos no item |
| Comentário | Justificativa da pontuação (`_x000D_` é removido) |

Outras colunas da planilha são ignoradas.

### 3.3 Série histórica (`Serie_Completa.csv`)

O arquivo usa `;` como separador, vírgula decimal e codificação latin-1. As colunas são `Ano`, `Sigla`,
`Justiça`, `Resultado` (pontos), `Percentual` (0 a 1), `Selo`, `Original` (TRUE/FALSE) e `Categoria`.

Tratamentos feitos em `historico.py`:

- Siglas `TREAC` viram `TRE-AC`, para casar com a planilha.
- "Sem prêmio" vira "Sem Prêmio".
- `Original` = FALSE, selo vazio ou "Sem Selo" viram **Não participou**.
- Se um ano faltar o ramo, usa-se o ramo do próprio tribunal nos outros anos.
- Posição e número de concorrentes são calculados por ano e ramo.

**Anos que não estão no CSV:**

- Se uma edição em `dados/` tiver um ano que o CSV não tem, as linhas desse ano são calculadas a partir da
  planilha (`historico.linhas_da_edicao`).
- Por isso **não é preciso editar o CSV** a cada nova edição.
- Se um dia o ano for incluído no CSV, o CSV passa a valer para o histórico desse ano.
- A conversão foi conferida com 2025: ramo, selo, categoria e percentual coincidem com o CSV nos 90 tribunais.

### 3.4 Tribunais excluídos

`EXCLUIDOS = ["TRT16", "CJF", "TSE"]` no início de `app.py`. Esses tribunais saem de todas as páginas, mas os
arquivos originais não são alterados.

### 3.5 Pontos de atenção conhecidos nos dados

- **Pontuação total de 2025:** difere entre o CSV e a planilha em três tribunais. Os percentuais são iguais.
  | Tribunal | CSV | Planilha |
  |---|---|---|
  | STJ | 979,65 | 989,65 |
  | TRE-DF | 1.011,57 | 991,57 |
  | TST | 882,30 | 887,30 |
- **2014:** alguns tribunais têm 0% com "Sem Prêmio". Talvez sejam casos de não participação; ainda não
  foi confirmado.

---

## 4. Como o código funciona

### 4.1 Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Painel: estilo (CSS), carga de dados, navegação, as quatro páginas, botões flutuantes e rodapé |
| `edicoes.py` | Descobre as edições em `dados/<ano>/` (e em `simulacao/<ano>/` quando a simulação está ligada) |
| `historico.py` | Lê e trata a série histórica; converte uma planilha de edição em linhas da série |
| `ficha_pdf.py` | Gera o PDF da ficha avaliativa |
| `identidade.py` | Cores oficiais do CNJ, logotipos (`logo_data_uri`) e a textura geométrica (`textura_svg`) |
| `historia.py` | Conteúdo da página Evolução do Prêmio (somente leitura para o painel) |
| `verificar_dados.py` | Confere os dados antes de publicar |
| `simular_edicao.py` | Gera uma edição simulada para testes. **Só local:** está no `.gitignore` e não vai para o GitHub |
| `gerar_manual_pdf.py` | Gera o PDF deste manual com a identidade visual do CNJ |
| `docs/` | Este manual (`MANUAL.md` e `MANUAL.pdf`) e as versões anteriores em `docs/versoes/` |
| `.streamlit/config.toml` | Tema: Montserrat, cor primária `#0f76b5`, fundo `#F1F3F6` |
| `requirements.txt` | Versões fixas das bibliotecas |
| `assets/cnj/` | Logotipos oficiais e o manual da marca |
| `assets/fontes/` | Montserrat (licença OFL) usada no PDF |

### 4.2 Edições (`edicoes.py`)

- `encontrar()` devolve `{ano: Edicao}`. Cada `Edicao` tem a planilha, a pasta de fichas e a marcação de simulada.
- A planilha da pasta é `base_final.xlsx`. Se esse nome não existir, vale a única `.xlsx` da pasta.
- Em `app.py`:
  - `EDICOES = ed.encontrar()`.
  - `ANO_EDICAO = max(EDICOES)` é a edição atual. É ela que aparece no banner, no rodapé, na Ficha, no
    Percentual e no filtro de porte do histórico. Não há seletor de edição no painel.
  - As edições anteriores continuam sendo lidas para compor o Histórico.

### 4.3 Cache

- Os dados ficam em cache (`st.cache_data`).
- A data de modificação de cada arquivo entra na chave do cache. Assim, ao substituir uma planilha ou o
  CSV, o painel recarrega sozinho, sem precisar reiniciar.

### 4.4 Estilo

- Todo o CSS fica no bloco `st.markdown("<style>…")`, no início de `app.py`.
- Os cartões brancos são `st.container(key="card_…")` (função `cartao`), estilizados pela classe
  `.st-key-card_…`.
- Os gráficos usam o template Plotly "painel": separador decimal vírgula, fundo transparente e dica (tooltip)
  escura.
- Cores das premiações: `CORES_PREMIO` em `app.py`. Cores dos selos do histórico: `CORES_SELO` em `historico.py`.

### 4.5 Simulação

- `python simular_edicao.py` cria `simulacao/2026/base_final.xlsx` a partir da última edição real:
  - os pontos variam aleatoriamente, com semente fixa;
  - o percentual é recalculado;
  - os selos são redistribuídos dentro de cada ramo, mantendo a quantidade de cada um.
- Para ver: `$env:PAINEL_SIMULACAO = "1"; streamlit run app.py`.
- Para desligar: `Remove-Item Env:PAINEL_SIMULACAO`.
- O painel **não exibe nenhum aviso de simulação**: a edição simulada aparece igual a uma edição real.
  Por isso, use a simulação só no seu computador e nunca envie a pasta `simulacao/` para o GitHub.
- `simular_edicao.py` e `simulacao/` estão no `.gitignore`: o script e as planilhas simuladas existem só no
  computador de quem mantém o painel.
- Sem a variável `PAINEL_SIMULACAO`, a pasta `simulacao/` é ignorada, então o painel publicado nunca a mostra.
  Uma edição real do mesmo ano tem prioridade sobre a simulada.

### 4.6 Carrossel da linha do tempo

- O `st.html` não executa JavaScript, por isso o carrossel usa botões de rádio invisíveis com rótulos
  (as setas).
- O CSS gerado para cada posição desloca a trilha de cartões (`translateX`) e mostra as setas daquela posição.
- O número de cartões visíveis é `VISIVEIS = 5` (página Histórico, em `app.py`).
- A fase Selo (2014–2019) não usa carrossel.

---

## 5. Tarefas de manutenção

### 5.1 Publicar uma nova edição (ex.: 2026)

1. Crie `dados/2026/` e coloque nela `base_final.xlsx`, com as mesmas colunas de 2025.
2. Se quiser, coloque as fichas oficiais em `dados/2026/fichas_pdf/`.
3. Rode `python verificar_dados.py`. Ele deve terminar com "Tudo certo." ou apenas com avisos.
4. Envie para o GitHub:
   `git add -A; git commit -m "Edição 2026"; git push`.
5. O Streamlit Cloud atualiza em instantes. Se não atualizar, use Manage app → Reboot app.

O código não muda. O painel passa a mostrar 2026 como edição atual: a Ficha e o Percentual passam a
mostrar 2026 e o Histórico ganha o ano 2026.

### 5.2 Outras alterações comuns

| Quero… | Onde mexer |
|---|---|
| Excluir ou incluir um tribunal | `EXCLUIDOS` em `app.py` |
| Nova premiação, ramo ou eixo | `ORDEM_PREMIO`/`CORES_PREMIO`, `ORDEM_RAMO`, `ORDEM_EIXO`/`CORES_EIXO` em `app.py`. Para o histórico, também `ORDEM_SELO`/`CORES_SELO` em `historico.py`. O `verificar_dados.py` avisa quando a planilha traz um valor não previsto. |
| Mudar a divisão das fases da linha do tempo | `FASES` na página Histórico, em `app.py` |
| Mostrar mais ou menos edições no carrossel | `VISIVEIS` em `app.py` |
| Corrigir o texto da Evolução do Prêmio | `historia.py` |
| Trocar cores ou logotipos | `identidade.py` e `assets/cnj/` |
| Atualizar uma biblioteca | `requirements.txt` (mantenha `svglib==1.5.1`: a 1.6+ exige pycairo, que não instala no Streamlit Cloud) |

### 5.3 Atualizar este manual

1. Edite `docs/MANUAL.md`. Suba a versão na linha "**Versão X.Y — data**" e acrescente uma linha na
   tabela da seção 6.
2. Copie o arquivo para `docs/versoes/MANUAL_vX.Y_AAAA-MM-DD.md`.
3. Rode `python gerar_manual_pdf.py`. Ele gera `docs/MANUAL.pdf` e a cópia versionada
   `docs/versoes/MANUAL_vX.Y_AAAA-MM-DD.pdf`, com capa, sumário com páginas, faixa institucional e
   rodapé no padrão do CNJ.

O gerador entende o Markdown usado aqui: títulos `##`/`###`, parágrafos, listas (com subníveis e
numeradas), tabelas, blocos de código, **negrito**, `código` e links.

### 5.4 Conferências antes de publicar

- `python verificar_dados.py` confere as colunas, os valores previstos, as duplicidades e a coerência
  entre o CSV e a planilha. Use `--simulacao` para incluir as edições simuladas.
- Abra o painel localmente e passe pelas quatro páginas.

---

## 6. Histórico de versões do painel

| Versão | Data | Mudanças |
|---|---|---|
| 1.10 | 18/11/2026 | Evolução do Prêmio: imagem de 2013 refeita em 4:3, com o selo inteiro centralizado sobre fundo marinho (a versão vertical era cortada no cartão). |
| 1.9 | 18/11/2026 | Evolução do Prêmio: imagens passam a preencher o quadro 4:3 com cantos arredondados (o Streamlit forçava `scale-down`, deixando a foto com canto reto dentro de uma moldura). Cartões 2021 a 2022 e 2013 passam a usar imagens locais; nenhum cartão usa mais imagem da internet. |
| 1.8 | 18/11/2026 | Evolução do Prêmio: incluídas as imagens dos cartões 2024 a 2025, 2020, 2019 e 2015 a 2018 (fornecidas pelo usuário) e a arte do cartão 2026–2027, criada no padrão do banner do painel (fundo marinho, textura geométrica do CNJ, Montserrat). |
| 1.7 | 18/11/2026 | Evolução do Prêmio: os cartões 2026–2027, 2024 a 2025, 2020, 2019 e 2015 a 2018 passam a usar imagens locais em `static/historia/` (nomes fixos). O painel aceita JPG/JPEG/PNG/WEBP e esconde a imagem enquanto o arquivo não existir; as imagens quebradas da internet foram retiradas desses cartões. |
| 1.6 | 18/11/2026 | Evolução do Prêmio: retirado o bloco "2024 - Foco no Cidadão e IA" (e seu link no menu). Criada a pasta `static/historia/` para as imagens dos cartões, servida pelo Streamlit (`enableStaticServing`). |
| 1.5 | 18/11/2026 | Evolução do Prêmio: incluídos os blocos "2024 a 2025 – Evolução do Critério de Pontuação" e "2026 – 2027: Instituição do regulamento bienal" (texto fornecido pelo usuário, com links para a Portaria CNJ n. 471/2025 e o Plano Pena Justa); linha do tempo e menu reordenados em ordem decrescente de ano. |
| 1.4 | 18/11/2026 | `simular_edicao.py` retirado do repositório e incluído no `.gitignore` (fica só no computador local). A pasta `simulacao/` local foi apagada; o painel mostra apenas os dados reais de 2025. |
| 1.3 | 17/11/2026 | Percentual de cumprimento mostra sempre a última edição inserida: seletor de edição retirado; filtros de ramo e porte reorganizados lado a lado numa só linha, com "Todos" como primeira opção do porte. |
| 1.2 | 17/11/2026 | Retirados os avisos de dados simulados do painel (selo no banner, "(simulação)" nos títulos e no seletor, marca no PDF e nos comentários). O mecanismo de simulação continua disponível para testes locais. |
| 1.1 | 17/11/2026 | A Ficha Avaliativa mostra sempre a última edição inserida: o seletor de edição foi retirado dela e continua só no Percentual de cumprimento. |
| 1.0 | 17/11/2026 | **Primeira versão deste manual.** Descreve o painel com as quatro páginas (Ficha Avaliativa, Percentual de cumprimento, Histórico, Evolução do Prêmio). Novidades da sessão: (a) edições organizadas por pasta `dados/<ano>/`, com detecção automática da edição atual e seletor de edição na Ficha e no Percentual; (b) histórico completado a partir da planilha quando o ano não está no CSV; (c) simulação de 2026 (`simular_edicao.py` + `PAINEL_SIMULACAO`); (d) `verificar_dados.py` conferindo todas as edições; (e) carrossel com as 5 edições mais recentes na fase do Prêmio da linha do tempo; (f) manual em PDF no padrão visual do CNJ (`gerar_manual_pdf.py`). Antes disso: publicação no GitHub e no Streamlit Cloud (com a correção do `svglib`) e a edição exibida ajustada para 2025. |
