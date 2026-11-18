import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="História - Prêmio CNJ", initial_sidebar_state="collapsed")

# --- CSS BASE E COMPONENTES ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,100..900;1,100..900&display=swap');
    
    /* --- EXTIRPAR O MENU LATERAL --- */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    
    /* Configuração de Rolagem Suave */
    html { scroll-behavior: smooth !important; }
    
    html, body, [class*="css"], p, h1, h2, h3, div, li {
        font-family: 'Inter Tight', sans-serif !important;
    }
    
    header { visibility: hidden; }

    /* --- CABEÇALHO DA PÁGINA --- */
    .page-title {
        font-size: 65px !important; font-weight: 900 !important;
        color: #1a1a1a; margin-bottom: 0px; letter-spacing: -2px;
        margin-top: 1rem;
    }
    .page-subtitle {
        font-size: 24px !important; color: #555;
        font-weight: 400; margin-bottom: 50px;
    }

    /* --- TIMELINE VERTICAL --- */
    .timeline-wrapper {
        border-left: 4px solid #1815dd; 
        margin-left: 20px;
        padding-left: 40px;
        padding-bottom: 50px;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 70px;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -54px; 
        top: 0px;
        width: 24px;
        height: 24px;
        background-color: #ffca28;
        border: 4px solid #1815dd;
        border-radius: 50%;
        z-index: 2;
        box-shadow: 0 0 0 4px white; 
    }
    
    /* Fase Marker */
    .timeline-phase {
        background-color: #1815dd;
        color: white;
        font-size: 24px;
        font-weight: 900;
        padding: 12px 30px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 50px;
        margin-top: 10px;
        position: relative;
        left: -54px; 
        border-left: 8px solid #ffca28;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        z-index: 3;
    }

    .timeline-card {
        background: white;
        padding: 40px; 
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-left: 8px solid #ffca28;
        transition: transform 0.2s;
        display: flex;
        flex-direction: row;
        gap: 40px; 
        align-items: flex-start;
    }
    .timeline-card:hover {
        transform: translateX(10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .timeline-img {
        width: 260px; 
        aspect-ratio: 4/3; 
        border-radius: 12px;
        object-fit: cover; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        flex-shrink: 0; 
    }
    
    .timeline-content { flex: 1; }
    
    .timeline-year {
        font-size: 34px; font-weight: 900; color: #1815dd; 
        margin-top: 0; margin-bottom: 20px; line-height: 1.2;
    }
    
    .timeline-text {
        font-size: 18px; color: #444; line-height: 1.7; 
        margin-top: 0; margin-bottom: 15px; text-align: justify; 
    }
    
    .timeline-list {
        margin-top: 10px; margin-bottom: 20px; padding-left: 25px;
        font-size: 18px; color: #444; line-height: 1.7;
    }
    .timeline-list li { margin-bottom: 8px; }

    @media (max-width: 900px) {
        .timeline-card { flex-direction: column; gap: 20px; padding: 25px; }
        .timeline-img { width: 100%; height: auto; aspect-ratio: 16/9; }
    }

    /* ========================================================= */
    /* --- O SEGREDO DO MENU FLUTUANTE (AGORA VAI!) --- */
    /* ========================================================= */
    
    /* 1. Impede TODAS as colunas de esticarem verticalmente */
    div[data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 2. Aplica o Sticky no container do menu de navegação */
    .st-key-menu_nav {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 80px !important;
        align-self: flex-start !important;
        z-index: 999;
    }

    /* Estética da caixa do menu */
    .sticky-menu-container {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-top: 5px solid #1815dd;
        width: 100%;
    }
    .sticky-title {
        font-weight: 900; font-size: 20px; color: #1a1a1a;
        margin-bottom: 15px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;
    }
    .sticky-link {
        display: block; text-decoration: none !important;
        color: #555 !important; font-weight: 600; font-size: 16px;
        padding: 10px 0; border-bottom: 1px solid #f5f5f5; transition: all 0.2s;
    }
    .sticky-link:hover {
        color: #1815dd !important; padding-left: 10px;
        border-left: 4px solid #ffca28; background: #fafafa;
    }

    /* --- BOTÕES FLUTUANTES --- */
    .floating-btn, .floating-btn1 {
        position: fixed; bottom: 40px;
        width: 60px; height: 60px;
        background-color: #1815dd; color: white !important;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 28px; text-decoration: none !important;
        box-shadow: 0 6px 20px rgba(24, 21, 221, 0.4);
        z-index: 9999; transition: all 0.3s ease; border: 2px solid #ffca28;
    }
    .floating-btn:hover, .floating-btn1:hover {
        transform: translateY(-8px) scale(1.05); background-color: #100dbd;
        box-shadow: 0 10px 25px rgba(24, 21, 221, 0.6);
    }
    .floating-btn  { right: 40px; }
    .floating-btn1 { right: 110px; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- ESTRUTURA DA PÁGINA ---
col_main, espaco, col_menu = st.columns([7.5, 0.5, 2.0])

with col_main:
    st.markdown('<div id="topo"></div>', unsafe_allow_html=True)
    st.markdown('<p class="page-title">A História do Prêmio</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Acompanhe a evolução do Prêmio CNJ de Qualidade e seus critérios ao longo dos anos.</p>', unsafe_allow_html=True)
    
    timeline_html = """
<div class="timeline-wrapper">
    <div class="timeline-phase">Fase 2: Maturidade e Inteligência</div>    
        <div class="timeline-item" id="ano-2026">
            <div class="timeline-card">
                <img src="app/static/historia/2026-2027.jpg" class="timeline-img" alt="Biênio 2026-2027">
                <div class="timeline-content">
                    <p class="timeline-year">2026 a 2027: Instituição do regulamento bienal</p>
                    <p class="timeline-text">A fim de atender a necessidade dos tribunais de possuir critérios mais previsíveis para melhorar o trabalho nas políticas tocadas pelo prêmio, foi publicada a da <a href="https://atos.cnj.jus.br/atos/detalhar/6575" target="_blank"><b>Portaria CNJ n. 471/2025</b></a> que apresentou o edital do Biênio 2026-2027 do Prêmio CNJ de Qualidade.</p>
                    <p class="timeline-text">As categorias de premiação também foram reorganizadas neste edital. A categoria Excelência deixou de existir, e permanecem as premiações Diamante, Ouro e Prata, conferidas segundo o ramo de justiça e o porte do tribunal (grande, médio e pequeno), este definido pelo Relatório Justiça em Números do mesmo ano.</p>
                    <p class="timeline-text">Quanto aos critérios, a nova portaria criou critérios específicos relacionados ao <a href="https://www.cnj.jus.br/sistema-carcerario/plano-pena-justa/" target="_blank"><b>Plano Pena Justa</b></a>, voltado a enfrentar a situação de calamidade nas prisões brasileiras, além de novos parâmetros para o atendimento de pessoas idosas e para a capacitação de equipes multiprofissionais.</p>
                </div>
            </div>
        </div>
        <div class="timeline-item" id="ano-20242025">
            <div class="timeline-card">
                <img src="app/static/historia/2024-2025.jpg" class="timeline-img" alt="Premio20242025">
                <div class="timeline-content">
                    <p class="timeline-year">2024 a 2025 – Evolução do Critério de Pontuação</p>
                    <p class="timeline-text">A partir de 2024, o prêmio instituiu o critério de premiação dos tribunais por portes, conforme classificação dos tribunais estaduais, eleitorais e do trabalho no relatório Justiça em Números publicado no ano da premiação (<a href="https://atos.cnj.jus.br/atos/detalhar/5366" target="_blank"><b>Portaria CNJ N. 353/2023</b></a>).</p>
                    <p class="timeline-text">Além disso, os tribunais tiveram acesso a portaria em dezembro do ano anterior ao prêmio, antecipando também o prazo de impugnação ao edital, que passou a ser final de janeiro, atendendo uma antiga necessidade dos gestores dos tribunais a fim de realizar o planejamento das atividades relacionadas ao certame.</p>
                    <ul class="timeline-list">
                        <li>Ações voltadas à aposentadoria de magistrados;</li>
                        <li>Número de eleitores com indicação de deficiência no cadastro eleitoral;</li>
                        <li>Alimentação adequada do Banco Nacional de Medidas Penais e Prisões;</li>
                        <li>Redução das desigualdades e inclusão social de mulheres de grupos vulneráveis no mercado de trabalho;</li>
                        <li>Implantação do Domicílio Judicial Eletrônico;</li>
                        <li>Implantar o Diário de Justiça Eletrônico Nacional;</li>
                        <li>Adesão a Plataforma Codex.</li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="timeline-item" id="ano-2021">
            <div class="timeline-card">
                <img src="app/static/historia/2021-2022.jpg" class="timeline-img" alt="Premio2021">
                <div class="timeline-content">
                    <p class="timeline-year">2021 a 2022 - Criação de ferramentas de apoio aos tribunais</p>
                    <p class="timeline-text">A <a href="https://atos.cnj.jus.br/atos/detalhar/3916" target="_blank"><b>Portaria CNJ n. 135/2021</b></a> instituiu o regulamento do Prêmio CNJ de Qualidade 2021 e nesta edição foi criado o painel de Saneamento do DATAJUD, que apresentava resultados dos itens relacionados ao DATAJUD e informações para subsidiar os tribunais na correção de seus dados.</p>
                    <p class="timeline-text">Além disso, foi apresentado o Painel de Resultados do Prêmio, com os resultados de todos os tribunais, as fichas e o desempenho dos tribunais por ramo em cada item.</p>
                    <p class="timeline-text">Em 2022, o regulamento do Prêmio CNJ de Qualidade 2022 foi instituído pela <a href="https://atos.cnj.jus.br/atos/detalhar/4549" target="_blank"><b>Portaria CNJ n. 170/2022</b></a> e era composto por 52 itens avaliativos, 10 a mais que o prêmio de 2021. Dentre as novidades apresentadas entre 2021 e 2022, temos seguintes temas abrangidos: </p>
                    <ul class="timeline-list">
                        <li>Plano Nacional de Atenção e Apoio às Vítimas de Crimes e Atos Infracionais.</li>
                        <li>Política de Gestão da Inovação.</li>
                        <li>Gestão de Memória e Gestão Documental;.</li>
                        <li>Realização de inspeção nos estabelecimentos prisionais e unidades de cumprimento de medidas socioeducativas.</li>
                        <li>Instalação dos Grupos de Monitoramento de Fiscalização dos Sistemas Carcerário e Socioeducativo.</li>
                        <li>Adesão a Plataforma Digital do Poder Judiciário.</li>
                        <li>Adesão a Plataforma Codex.</li>
                    </ul> 
                </div>
            </div>
        </div>
        <div class="timeline-item" id="ano-2020">
            <div class="timeline-card">
                <img src="app/static/historia/2020.jpg" class="timeline-img" alt="Premio2020">
                <div class="timeline-content">
                    <p class="timeline-year">2020 - Criação do DATAJUD</p>
                    <p class="timeline-text">Em 2020, o <a href="https://www.cnj.jus.br/sistemas/datajud/" target="_blank"><b>DATAJUD</b></a> foi instituído pela <a href="https://atos.cnj.jus.br/atos/detalhar/3428" target="_blank"><b>Resolução CNJ n. 331/2020</b></a> como fonte primária de dados do Sistema de Estatística do Poder Judiciário (SIESPJ) e passou ser a repositório de dados de referência para diversos itens do prêmio. </p>
                    <p class="timeline-text">Com 40 itens, a <a href="https://atos.cnj.jus.br/atos/detalhar/3341" target="_blank"><b>Portaria CNJ n. 88/2020</b></a> apresentou as seguintes inovações: </p>
                    <ul class="timeline-list">
                        <li><b>Avaliação de Recurso antecipada:</b> Instituição de fase prévia de avaliação e recursos para os itens documentais.</li>
                        <li><b>Fim do Melhor do Ano:</b> Fim da premiação para o melhor tribunal ramo de justiça.</li>
                        <li><b>Mudança no ranking:</b> Instituição da premiação relacionada ao ranking dos tribunais por ramo de justiça.</li>
                        <li><b>Novas categorias de itens:</b> Os itens avaliativos foram reagrupados em quatro eixos: Governança (12 itens), Produtividade (12 itens), Transparência (3 itens) e Dados e Tecnologia (14 itens).</li>
                        <li><b>Novos critérios:</b> Inserção de critérios sobre os seguintes temas: Metas Nacionais, Implantação do PJe, Infância e Juventude e Adoção.</li>
                    </ul>                
                </div>
            </div>
        </div>
        <div class="timeline-item" id="ano-2019">
            <div class="timeline-card">
                <img src="app/static/historia/2019.jpg" class="timeline-img" alt="Premio2019">
                <div class="timeline-content">
                    <p class="timeline-year">2019 - Prêmio CNJ de Qualidade</p>
                    <p class="timeline-text">Por meio da <a href="https://atos.cnj.jus.br/atos/detalhar/2920" target="_blank"><b>Portaria CNJ n. 88/2019</b></a>, o CNJ instituiu no ano de 2019 o Prêmio CNJ de Qualidade, uma evolução do Selo Justiça em Números, com o objetivo de promover desenvolvimento da gestão, do planejamento estratégico, da transparência e da produção de dados pelos tribunais brasileiros. </p>
                    <p class="timeline-text">Neste ano, a portaria apresentada 27 itens e foram apresentadas diversas novidades: </p>
                    <ul class="timeline-list">
                        <li><b>Prêmio Excelência:</b> Premiação para o melhor tribunal do Poder Judiciário e com percentual de pontos acima de 90%.</li>
                        <li><b>Prêmio Melhor do Ano:</b> Premiação para o melhor tribunal ramo de justiça.</li>
                        <li><b>Criação dos eixos temáticos:</b> Os itens avaliativos foram agrupados em três eixos: Governança (15 itens), Produtividade (8 itens), Informação (4 itens).</li>
                        <li><b>Ranqueamento e limitação de premiados:</b> Os tribunais foram ranqueados pelo seu percentual de cumprimento dos itens e as premiações foram limitadas: 9 Diamantes, 22 Ouros e 28 Pratas.</li>
                        <li><b>Novos critérios:</b> Critérios sobre os seguintes temas: Acessibilidade, Conciliação, Infância e Juventude e Atendimento das Ouvidorias.</li>
                    </ul>
                </div>
            </div>
        </div>
    <div class="timeline-phase" style="margin-top: 40px;">Início: Selo Justiça em Números</div> 
        <div class="timeline-item" id="ano-20152016">
            <div class="timeline-card">
                <img src="app/static/historia/2015-2018.jpg" class="timeline-img" alt="Selo20152016">
                <div class="timeline-content">
                    <p class="timeline-year">2015 a 2018 - Evolução do Selo</p>
                    <p class="timeline-text">Diversos assuntos de interesse do Poder Judiciário Nacional foram agregados ao regulamento do Selo Justiça em Números durante entre 2015 e 2018, acarretando no crescimento de itens avaliativos ao certame. Abaixo temos a lista de temas adicionados durante os anos: </p>
                    <ul class="timeline-list">
                        <li><b>2015 (9 itens):</b> Transparência da gestão orçamentária e financeira, Desempenho do tribunal no questionário pelo Comitê Nacional de Gestão de Tecnologia da Informação e Comunicação e Repercussão Geral e Recursos Repetitivos.</li>
                        <li><b>2016 (15 itens):</b> Gestão Socioambiental, Política de Atenção à Saúde de Magistrados e Servidores, e Gestão Participativa e democrática das metas nacionais do Poder Judiciário.</li>
                        <li><b>2017 (16 itens):</b> Índice de Produtividade Comparada do Poder Judiciário  - IPC-Jus e Classificação por percentual de pontuação e classificações específicas para cada ramo de justiça.</li>
                        <li><b>2018 (19 itens):</b> Mês Nacional do Juri e Enfrentamento à Violência contra as Mulheres. </li>
                    </ul>
                    <p class="timeline-text">Em 2017 foi incrementada a possibilidade de apresentação de recursos ao resultado do Selo.</p>
                </div>
            </div>
        </div>
        <div class="timeline-item" id="ano-2013">
            <div class="timeline-card">
                <img src="app/static/historia/2013.jpg" class="timeline-img" alt="Criação em 2019">
                <div class="timeline-content">
                    <p class="timeline-year">2013 - Selo Justiça em Números</p>
                    <p class="timeline-text">O <b>Selo Justiça em Números</b> foi instituído oficialmente em 2013, por meio da <a href="https://atos.cnj.jus.br/atos/detalhar/atos-normativos?documento=1871" target="_blank"><b>Portaria CNJ n. 186/2013</b></a> com os seguintes objetivos: incentivar o aprimoramento do Sistema de Estatísticas do Poder Judiciário; promover a melhoria da qualidade da informação; e contribuir para produção de dados confiáveis sobre o Poder Judiciário.</p>
                    <p class="timeline-text">Foram definidos parâmetros rigorosos de avaliação , divididos da seguinte forma:</p>
                    <ul class="timeline-list">
                        <li><b>Requisitos Mínimos:</b> Os tribunais tinham que encaminhar dados estatísticas e realizar retificações em prazos pré-definidos.</li>
                        <li><b>Gestão da Informação:</b> Integração das TPU e organização via sistema automatizado dados de litigiosidade.</li>
                        <li><b>Extração de dados:</b> Extração via sistema automatizado dados de litigiosidade.</li>
                    </ul>
                    <p class="timeline-text">A partir deste momento, os tribunais passaram a ser classificados nas categorias Diamante, Ouro, Prata e Bronze gerando uma concorrência saudável e uma busca incessante pela modernização administrativa e tecnológica no judiciário brasileiro, visando atender a necessidade crescente do acesso público às informações estatísticas e aos indicadores do Judiciário brasileiro.</p>
                </div>
            </div>
        </div>
</div>
"""
    st.markdown(timeline_html, unsafe_allow_html=True)

with col_menu:
  with st.container(key="menu_nav"):
    menu_html = """
<div class="sticky-menu-container">
    <div class="sticky-title">Navegação Rápida</div>
    <div style="font-weight: 800; color: #1815dd; margin-top: 15px; margin-bottom: 5px; font-size: 14px; text-transform: uppercase;">Fase 2: Maturidade</div>
    <a href="#ano-2026" class="sticky-link" style="padding-left: 10px;">📍 2026 a 2027: Instituição do regulamento bienal</a>
    <a href="#ano-20242025" class="sticky-link" style="padding-left: 10px;">📍 2024 a 2025 – Evolução do Critério de Pontuação</a>
    <a href="#ano-2021" class="sticky-link" style="padding-left: 10px;">📍 2021 a 2022 - Criações de ferramentas de apoio aos tribunais</a>
    <a href="#ano-2020" class="sticky-link" style="padding-left: 10px;">📍 2020 - Criação do DATAJUD</a>
    <a href="#ano-2019" class="sticky-link" style="padding-left: 10px;">📍 2019 - Prêmio CNJ de Qualidade</a>
    <div style="font-weight: 800; color: #1815dd; margin-top: 25px; margin-bottom: 5px; font-size: 14px; text-transform: uppercase;">Fase 1: Estruturação</div>
    <a href="#ano-20152016" class="sticky-link" style="padding-left: 10px;">📍 2015 a 2018 - Evolução do Selo</a>
    <a href="#ano-2013" class="sticky-link" style="padding-left: 10px;">📍 2013 - Selo Justiça em Números</a>
</div>
    """
    st.markdown(menu_html, unsafe_allow_html=True)

# --- BOTÕES FLUTUANTES ---
st.markdown("""
    <a href="/" target="_self" class="floating-btn1">🏠</a>
    <a href="#topo" class="floating-btn">↑</a>
""", unsafe_allow_html=True)