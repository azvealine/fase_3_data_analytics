import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlglot
from pathlib import Path

# -----------------------------------------------------------------------------
# Configuração da Página do Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Estado de Dados Brasil | Painel Executivo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Conexão e Carga de Dados via DuckDB
# -----------------------------------------------------------------------------
@st.cache_resource
def get_duckdb_connection():
    con = duckdb.connect()
    base_dir = Path(__file__).resolve().parent
    pasta_specs = base_dir / 'dados' / 'bases_analiticas'
    
    if not pasta_specs.exists():
        pasta_specs = Path('D:/d/pos/Fase 3/projeto/fase_3_data_analytics/dados/bases_analiticas')
        
    for f in pasta_specs.glob('*.parquet'):
        nome = f.stem
        con.execute(f"CREATE OR REPLACE VIEW {nome} AS SELECT * FROM read_parquet('{f.as_posix()}')")
        
    return con

con = get_duckdb_connection()

@st.cache_data
def query_duckdb(sql_query):
    query_val = sqlglot.parse_one(sql_query, read="duckdb")
    return con.sql(query_val.sql(dialect="duckdb")).df()

# -----------------------------------------------------------------------------
# Cabeçalho Principal
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">📊 Estado de Dados Brasil | Painel Executivo & Evolução Histórica</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Tech Challenge - Fase 3 | Análise Estratégica Multianual (2023 ➔ 2024 ➔ 2025) com PySpark & DuckDB</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar & Filtros
# -----------------------------------------------------------------------------
st.sidebar.image("https://raw.githubusercontent.com/streamlit/brand/master/streamlit-mark-color.png", width=60)
st.sidebar.title("🎛️ Filtros Globais")

anos_disponiveis = query_duckdb("SELECT DISTINCT ano_pesquisa FROM spec_respondentes ORDER BY 1")['ano_pesquisa'].tolist()
ano_selecionado = st.sidebar.selectbox("📅 Selecione o Ano de Referência:", ["Todos os Anos (2023–2025)"] + anos_disponiveis, index=0)

# Construção dos filtros SQL seguros (com e sem alias de tabela)
if ano_selecionado != "Todos os Anos (2023–2025)":
    filtro_ano_sql = f"WHERE ano_pesquisa = {ano_selecionado}"
    filtro_ano_and_r = f"AND r.ano_pesquisa = {ano_selecionado}"
    filtro_ano_and_a = f"AND a.ano_pesquisa = {ano_selecionado}"
    filtro_ano_and_t = f"AND t.ano_pesquisa = {ano_selecionado}"
    filtro_ano_where_r = f"WHERE r.ano_pesquisa = {ano_selecionado}"
    filtro_ano_where_t = f"WHERE t.ano_pesquisa = {ano_selecionado}"
    filtro_ano_where_a = f"WHERE a.ano_pesquisa = {ano_selecionado}"
    label_filtro = f"Ano {ano_selecionado}"
else:
    filtro_ano_sql = ""
    filtro_ano_and_r = ""
    filtro_ano_and_a = ""
    filtro_ano_and_t = ""
    filtro_ano_where_r = ""
    filtro_ano_where_t = ""
    filtro_ano_where_a = ""
    label_filtro = "Geral (2023–2025)"

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Arquitetura Analítica")
st.sidebar.markdown("""
* **SOT**: 14.005 respondentes
* **Processamento**: Apache Spark (PySpark)
* **Storage**: 7 SPECS em Parquet
* **Query Engine**: DuckDB SQL
* **Visualização**: Streamlit + Plotly
""")
st.sidebar.markdown("---")
st.sidebar.caption("Tech Challenge - Fase 3 | Data Analytics")

# -----------------------------------------------------------------------------
# KPIs Executivos Gerais
# -----------------------------------------------------------------------------
kpi_query = f"""
    SELECT COUNT(*) AS total_respondentes,
           ROUND(AVG(salario_estimado_num), 0) AS salario_medio,
           ROUND(100.0 * SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_mulheres,
           ROUND(100.0 * SUM(CASE WHEN modelo_trabalho_resumido = 'Remoto' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_remoto
    FROM spec_respondentes
    {filtro_ano_sql}
"""
df_kpi = query_duckdb(kpi_query)

kpi_ia = query_duckdb(f"""
    SELECT ROUND(100.0 * COUNT(DISTINCT r.respondente_key) / (SELECT COUNT(DISTINCT respondente_key) FROM spec_respondentes {filtro_ano_sql}), 1) as pct_ia
    FROM spec_adocao_ia a
    JOIN spec_respondentes r ON a.respondente_key = r.respondente_key
    WHERE a.tipo_registro = 'Uso Ativo' {filtro_ano_and_r}
""")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("👥 Total de Profissionais", f"{df_kpi['total_respondentes'][0]:,}")
with col2:
    st.metric("💰 Remuneração Média", f"R$ {df_kpi['salario_medio'][0]:,.0f}")
with col3:
    st.metric("🤖 Adoção Ativa de IA", f"{kpi_ia['pct_ia'][0]}%")
with col4:
    st.metric("👩 Representação Feminina", f"{df_kpi['pct_mulheres'][0]}%")
with col5:
    st.metric("🏠 Trabalho 100% Remoto", f"{df_kpi['pct_remoto'][0]}%")

st.markdown("---")

# -----------------------------------------------------------------------------
# Abas de Navegação por Pergunta Estratégica
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "🏢 P1: Estrutura do Mercado",
    "💰 P2: Valorização Salarial",
    "⚖️ P3: Diversidade & Equidade",
    "💻 P4: Stack Tecnológico",
    "🤖 P5: Adoção de IA",
    "🏠 P6: Modelos de Trabalho",
    "🎯 P7: Desafios & Roadmap",
    "📈 Balanço Temporal (2023-2025)"
])

# =============================================================================
# ABA 1: Estrutura do Mercado
# =============================================================================
with tabs[0]:
    st.header("🏢 Pergunta 1: Como está estruturado o mercado brasileiro de Dados e como ele evoluiu?")
    st.markdown("""
    * **Distribuição Geral**: O mercado é liderado por **Análise de Dados & BI (25.8%)**, **Engenharia & Arquitetura de Dados (16.3%)** e **Ciência de Dados (13.2%)**.
    * **📈 Evolução Histórica (2023 ➔ 2025)**:
      * **Machine Learning & IA (+129.2% de crescimento)**: Saltou de 2.4% para 5.5% entre os perfis centrais.
      * **Engenharia de Dados (+9.7% de expansão)**: Subiu de 26.9% para 29.5%.
      * **Análise de Dados & BI (-10.5% de recuo)**: Recuou de 47.4% para 42.4% devido à especialização do mercado.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        df_cargos_yoy = query_duckdb("""
            SELECT ano_pesquisa, macro_cargo,
                   COUNT(*) AS total,
                   ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 1) AS pct_ano
            FROM spec_respondentes
            WHERE macro_cargo IN ('Análise de Dados & BI', 'Engenharia & Arquitetura de Dados', 'Ciência de Dados', 'Machine Learning & IA')
            GROUP BY 1, 2
            ORDER BY ano_pesquisa, pct_ano DESC
        """)
        fig1 = px.bar(
            df_cargos_yoy, x='ano_pesquisa', y='pct_ano', color='macro_cargo', barmode='group',
            title="<b>Evolução da Participação dos Macro-Cargos (2023–2025)</b>",
            labels={'ano_pesquisa': 'Ano', 'pct_ano': '% do Mercado', 'macro_cargo': 'Cargo'},
            color_discrete_map={'Análise de Dados & BI': '#1f77b4', 'Engenharia & Arquitetura de Dados': '#2ca02c', 'Ciência de Dados': '#9467bd', 'Machine Learning & IA': '#ff7f0e'},
            text='pct_ano'
        )
        fig1.update_traces(texttemplate='%{text}%', textposition='outside')
        fig1.update_layout(template='plotly_white', height=450, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_b:
        filtro_times = f"WHERE ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else ""
        df_equipes = query_duckdb(f"""
            SELECT papel_na_empresa,
                   COUNT(DISTINCT respondente_key) AS total_empresas,
                   ROUND(100.0 * COUNT(DISTINCT respondente_key) / (SELECT COUNT(DISTINCT respondente_key) FROM spec_estrutura_times_empresa {filtro_times}), 1) AS penetracao_pct
            FROM spec_estrutura_times_empresa
            {filtro_times}
            GROUP BY 1 ORDER BY penetracao_pct ASC
        """)
        fig2 = px.bar(
            df_equipes, x='penetracao_pct', y='papel_na_empresa', orientation='h',
            title=f"<b>Presença de Funções nas Empresas ({label_filtro})</b>",
            labels={'penetracao_pct': '% das Empresas com o Papel', 'papel_na_empresa': 'Papel na Empresa'},
            color_discrete_sequence=['#20c997'],
            text='penetracao_pct'
        )
        fig2.update_traces(texttemplate='%{text}%', textposition='outside')
        fig2.update_layout(template='plotly_white', height=450)
        st.plotly_chart(fig2, use_container_width=True)

# =============================================================================
# ABA 2: Valorização Salarial
# =============================================================================
with tabs[1]:
    st.header("💰 Pergunta 2: Quais perfis são mais valorizados e como a remuneração evoluiu?")
    st.markdown("""
    * **Liderança Salarial**: **Machine Learning & IA** recebe a maior remuneração média nacional (**R$ 16.186**), seguida por **Engenharia de Dados** (**R$ 12.603**) e **Ciência de Dados** (**R$ 11.560**).
    * **📈 Explosão Salarial em ML & IA (+51.7%)**: O salário médio em IA saltou de **R$ 12.573 (2023)** para **R$ 19.080 (2025)**.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        df_sal_evolucao = query_duckdb("""
            SELECT ano_pesquisa, macro_cargo,
                   ROUND(AVG(salario_estimado_num), 0) AS salario_medio
            FROM spec_respondentes
            WHERE macro_cargo IN ('Machine Learning & IA', 'Engenharia & Arquitetura de Dados', 'Ciência de Dados', 'Análise de Dados & BI')
              AND salario_estimado_num IS NOT NULL
            GROUP BY 1, 2
            ORDER BY macro_cargo, ano_pesquisa
        """)
        fig3 = px.line(
            df_sal_evolucao, x='ano_pesquisa', y='salario_medio', color='macro_cargo', markers=True,
            title="<b>Evolução da Remuneração Média (R$) por Especialidade (2023–2025)</b>",
            labels={'ano_pesquisa': 'Ano', 'salario_medio': 'Salário Médio (R$)', 'macro_cargo': 'Cargo'},
            color_discrete_map={'Análise de Dados & BI': '#1f77b4', 'Engenharia & Arquitetura de Dados': '#2ca02c', 'Ciência de Dados': '#9467bd', 'Machine Learning & IA': '#ff7f0e'}
        )
        fig3.update_traces(textposition="top center")
        fig3.update_layout(template='plotly_white', height=450, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig3, use_container_width=True)
        
    with col_b:
        filtro_tech = f"WHERE salario_estimado_num IS NOT NULL AND ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else "WHERE salario_estimado_num IS NOT NULL"
        df_premio_stack = query_duckdb(f"""
            SELECT tecnologia, familia,
                   ROUND(AVG(salario_estimado_num), 0) AS media_salarial,
                   COUNT(DISTINCT respondente_key) AS total_usuarios
            FROM spec_adocao_tecnologias
            {filtro_tech}
            GROUP BY 1, 2
            HAVING COUNT(DISTINCT respondente_key) >= 50
            ORDER BY media_salarial ASC LIMIT 8
        """)
        fig4 = px.bar(
            df_premio_stack, x='media_salarial', y='tecnologia', orientation='h',
            title=f"<b>Top Tecnologias com Maior Salário Médio ({label_filtro})</b>",
            labels={'media_salarial': 'Salário Médio (R$)', 'tecnologia': 'Tecnologia'},
            color_discrete_sequence=['#f08c46'],
            text='media_salarial'
        )
        fig4.update_traces(texttemplate='R$ %{text:,.0f}', textposition='inside')
        fig4.update_layout(template='plotly_white', height=450)
        st.plotly_chart(fig4, use_container_width=True)

# =============================================================================
# ABA 3: Diversidade de Gênero & Equidade
# =============================================================================
with tabs[2]:
    st.header("⚖️ Pergunta 3: Qual é o cenário de diversidade de gênero nas carreiras de dados?")
    st.markdown("""
    * **Sub-representação Geral**: Mulheres compõem apenas **23.6%** do mercado brasileiro de dados.
    * **Efeito Funil ("Teto de Vidro")**: A participação feminina cai continuamente conforme a senioridade avança (**Júnior: 27.2% ➔ Especialista: 16.2%**).
    * **Pay Gap Homens vs Mulheres**: O gap salarial médio ampliou de **18.0% em 2023 (R$ 1.970/mês)** para **19.4% em 2025 (R$ 2.680/mês)**.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        filtro_funil = f"WHERE nivel IN ('Júnior', 'Pleno', 'Sênior', 'Especialista/Staff+') AND ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else "WHERE nivel IN ('Júnior', 'Pleno', 'Sênior', 'Especialista/Staff+')"
        df_funil_atual = query_duckdb(f"""
            SELECT nivel,
                   ROUND(100.0 * SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_mulheres
            FROM spec_respondentes
            {filtro_funil}
            GROUP BY nivel
            ORDER BY CASE nivel WHEN 'Júnior' THEN 1 WHEN 'Pleno' THEN 2 WHEN 'Sênior' THEN 3 WHEN 'Especialista/Staff+' THEN 4 END
        """)
        fig5 = px.bar(
            df_funil_atual, x='nivel', y='pct_mulheres',
            title=f"<b>Funil de Representação Feminina por Nível ({label_filtro})</b>",
            labels={'nivel': 'Nível de Senioridade', 'pct_mulheres': '% Mulheres'},
            color_discrete_sequence=['#e377c2'],
            text='pct_mulheres'
        )
        fig5.update_traces(texttemplate='%{text}%', textposition='outside')
        fig5.update_layout(template='plotly_white', height=450)
        fig5.update_yaxes(range=[0, 35])
        st.plotly_chart(fig5, use_container_width=True)
        
    with col_b:
        df_gap_yoy = query_duckdb("""
            SELECT ano_pesquisa,
                   ROUND(AVG(CASE WHEN genero = 'Masculino' THEN salario_estimado_num END), 0) AS sal_homens,
                   ROUND(AVG(CASE WHEN genero = 'Feminino' THEN salario_estimado_num END), 0) AS sal_mulheres
            FROM spec_respondentes
            WHERE genero IN ('Masculino', 'Feminino')
            GROUP BY 1 ORDER BY 1
        """)
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(x=df_gap_yoy['ano_pesquisa'].astype(str), y=df_gap_yoy['sal_homens'], name='Homens (R$)', marker_color='#1f77b4', text=df_gap_yoy['sal_homens'].apply(lambda v: f"R$ {v:,.0f}"), textposition='auto'))
        fig6.add_trace(go.Bar(x=df_gap_yoy['ano_pesquisa'].astype(str), y=df_gap_yoy['sal_mulheres'], name='Mulheres (R$)', marker_color='#e377c2', text=df_gap_yoy['sal_mulheres'].apply(lambda v: f"R$ {v:,.0f}"), textposition='auto'))
        fig6.update_layout(
            title="<b>Evolução da Remuneração Média: Homens vs Mulheres (2023–2025)</b>",
            template='plotly_white', height=450, barmode='group',
            legend=dict(orientation="h", y=-0.25)
        )
        st.plotly_chart(fig6, use_container_width=True)

# =============================================================================
# ABA 4: Stack Tecnológico
# =============================================================================
with tabs[3]:
    st.header("💻 Pergunta 4: Quais tecnologias apresentam maior adoção entre os profissionais?")
    st.markdown("""
    * **Linguagens Líderes**: **SQL (57.6%)** e **Python (54.9%)** formam a base incontestável.
    * **Evolução de Cloud & Lakehouse**:
      * **AWS (+38.7%)**: Lidera em nuvem, saltando de 20.9% para **29.0%** em 2025.
      * **Databricks (+29.6%)**: Subiu de 15.2% para **19.7%**, consolidando a liderança em Lakehouse.
      * **Snowflake (+31.0%)**: Subiu de 4.2% para **5.5%**.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        df_cloud_yoy = query_duckdb("""
            SELECT t.ano_pesquisa, t.tecnologia,
                   ROUND(100.0 * COUNT(DISTINCT t.respondente_key) / r.total_ano, 1) AS pct_adocao
            FROM spec_adocao_tecnologias t
            JOIN (SELECT ano_pesquisa, COUNT(DISTINCT respondente_key) AS total_ano FROM spec_respondentes GROUP BY 1) r
              ON t.ano_pesquisa = r.ano_pesquisa
            WHERE t.tecnologia IN ('AWS', 'Azure', 'Google Cloud (GCP)', 'Databricks', 'Snowflake')
            GROUP BY 1, 2, r.total_ano
            ORDER BY t.tecnologia, t.ano_pesquisa
        """)
        fig7 = px.line(
            df_cloud_yoy, x='ano_pesquisa', y='pct_adocao', color='tecnologia', markers=True,
            title="<b>Evolução da Adoção de Cloud & Lakehouse (2023–2025)</b>",
            labels={'ano_pesquisa': 'Ano', 'pct_adocao': '% de Adoção', 'tecnologia': 'Plataforma'},
            color_discrete_map={'AWS': '#ff7f0e', 'Azure': '#1f77b4', 'Google Cloud (GCP)': '#34a853', 'Databricks': '#e24a4a', 'Snowflake': '#29b5e8'}
        )
        fig7.update_layout(template='plotly_white', height=450, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig7, use_container_width=True)
        
    with col_b:
        filtro_tech_rank = f"WHERE t.ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else ""
        total_resp_base = f"(SELECT COUNT(DISTINCT respondente_key) FROM spec_respondentes {filtro_ano_sql})"
        df_tech_ranking = query_duckdb(f"""
            WITH ranked AS (
                SELECT t.familia, t.tecnologia,
                       COUNT(DISTINCT t.respondente_key) AS adotantes,
                       ROUND(100.0 * COUNT(DISTINCT t.respondente_key) / {total_resp_base}, 1) AS pct_mercado,
                       ROW_NUMBER() OVER(PARTITION BY t.familia ORDER BY COUNT(DISTINCT t.respondente_key) DESC) AS rnk
                FROM spec_adocao_tecnologias t
                {filtro_tech_rank}
                GROUP BY 1, 2
            )
            SELECT familia, tecnologia, pct_mercado
            FROM ranked WHERE rnk <= 4
            ORDER BY pct_mercado ASC
        """)
        fig8 = px.bar(
            df_tech_ranking, x='pct_mercado', y='tecnologia', orientation='h', color='familia',
            title=f"<b>Top Tecnologias mais Adotadas ({label_filtro})</b>",
            labels={'pct_mercado': '% do Mercado', 'tecnologia': 'Tecnologia', 'familia': 'Família'}
        )
        fig8.update_layout(template='plotly_white', height=450, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig8, use_container_width=True)

# =============================================================================
# ABA 5: Adoção de Inteligência Artificial
# =============================================================================
with tabs[4]:
    st.header("🤖 Pergunta 5: Qual é o índice de adoção de Inteligência Artificial e seu impacto?")
    st.markdown("""
    * **Amadurecimento Corporativo (+33.8%)**: A taxa de empresas com IA integrada a produtos e processos internos subiu de **21.6% em 2023** para **28.9% em 2025**.
    * **Setores Líderes**: **Consultorias (34.1%)**, **Finanças/Bancos (33.4%)** e **Tecnologia (33.2%)** lideram o uso institucional de IA no Brasil.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        df_ia_evolucao = query_duckdb("""
            SELECT r.ano_pesquisa,
                   ROUND(100.0 * COUNT(DISTINCT a.respondente_key) / COUNT(DISTINCT r.respondente_key), 1) AS taxa_adocao_geral,
                   ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.indicador_ia_id IN ('ia_produtos_internos', 'ia_produtos_externos', 'ia_principal_frente_negocio') THEN a.respondente_key END) / COUNT(DISTINCT r.respondente_key), 1) AS taxa_ia_corporativa
            FROM spec_respondentes r
            LEFT JOIN spec_adocao_ia a ON r.respondente_key = a.respondente_key AND a.tipo_registro = 'Uso Ativo'
            GROUP BY 1 ORDER BY 1
        """)
        fig9 = go.Figure()
        fig9.add_trace(go.Bar(x=df_ia_evolucao['ano_pesquisa'].astype(str), y=df_ia_evolucao['taxa_adocao_geral'], name='Uso Geral de IA (%)', marker_color='#0b7285', text=df_ia_evolucao['taxa_adocao_geral'].apply(lambda v: f"{v}%"), textposition='auto'))
        fig9.add_trace(go.Bar(x=df_ia_evolucao['ano_pesquisa'].astype(str), y=df_ia_evolucao['taxa_ia_corporativa'], name='IA em Produtos/Processos (%)', marker_color='#f08c46', text=df_ia_evolucao['taxa_ia_corporativa'].apply(lambda v: f"{v}%"), textposition='auto'))
        fig9.update_layout(
            title="<b>Evolução da Adoção de IA no Brasil (2023–2025)</b>",
            template='plotly_white', height=450, barmode='group',
            legend=dict(orientation="h", y=-0.25)
        )
        st.plotly_chart(fig9, use_container_width=True)
        
    with col_b:
        filtro_ia_setor = f"WHERE r.ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else "WHERE r.setor IS NOT NULL"
        df_ia_setores = query_duckdb(f"""
            SELECT r.setor,
                   ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.indicador_ia_id IN ('ia_produtos_internos', 'ia_produtos_externos', 'ia_principal_frente_negocio') THEN a.respondente_key END) / COUNT(DISTINCT r.respondente_key), 1) AS pct_ia_corporativa
            FROM spec_respondentes r
            LEFT JOIN spec_adocao_ia a ON r.respondente_key = a.respondente_key AND a.tipo_registro = 'Uso Ativo'
            {filtro_ia_setor}
            GROUP BY 1 HAVING COUNT(DISTINCT r.respondente_key) >= 100
            ORDER BY pct_ia_corporativa ASC
        """)
        fig10 = px.bar(
            df_ia_setores, x='pct_ia_corporativa', y='setor', orientation='h',
            title=f"<b>Maturidade de IA Corporativa por Setor ({label_filtro})</b>",
            labels={'pct_ia_corporativa': '% com IA em Processos/Produtos', 'setor': 'Setor'},
            color_discrete_sequence=['#20c997'], text='pct_ia_corporativa'
        )
        fig10.update_traces(texttemplate='%{text}%', textposition='outside')
        fig10.update_layout(template='plotly_white', height=450)
        st.plotly_chart(fig10, use_container_width=True)

# =============================================================================
# ABA 6: Modelos de Trabalho
# =============================================================================
with tabs[5]:
    st.header("🏠 Pergunta 6: Quais diferenças existem em modelos de trabalho e retenção?")
    st.markdown("""
    * **O Retorno Forçado ao Escritório**: O trabalho 100% remoto recuou de **46.3% em 2023** para **39.7% em 2025** (-6.6 p.p.), enquanto os modelos presenciais/híbridos fixos avançaram para **40.8%**.
    * **Descompasso & Risco de Turnover**: **48.3% dos profissionais** em modelos presenciais/híbridos fixos desejam maior flexibilidade. Somente **1.2%** consideram o regime presencial como ideal.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        df_modelos_yoy = query_duckdb("""
            SELECT ano_pesquisa, modelo_trabalho_resumido,
                   ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(PARTITION BY ano_pesquisa), 1) AS pct_ano
            FROM spec_respondentes
            WHERE modelo_trabalho_resumido IN ('Remoto', 'Híbrido Flexível', 'Híbrido Fixo', 'Presencial')
            GROUP BY 1, 2
            ORDER BY modelo_trabalho_resumido, ano_pesquisa
        """)
        fig11 = px.bar(
            df_modelos_yoy, x='ano_pesquisa', y='pct_ano', color='modelo_trabalho_resumido', barmode='group',
            title="<b>Evolução dos Modelos de Trabalho (2023–2025)</b>",
            labels={'ano_pesquisa': 'Ano', 'pct_ano': '% dos Profissionais', 'modelo_trabalho_resumido': 'Modelo'},
            color_discrete_map={'Remoto': '#2b8a3e', 'Híbrido Flexível': '#1f77b4', 'Híbrido Fixo': '#f59f00', 'Presencial': '#e03131'},
            text='pct_ano'
        )
        fig11.update_traces(texttemplate='%{text}%', textposition='outside')
        fig11.update_layout(template='plotly_white', height=450, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig11, use_container_width=True)
        
    with col_b:
        filtro_alinhamento = f"WHERE status_alinhamento != 'Não informado' AND ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else "WHERE status_alinhamento != 'Não informado'"
        df_alinhamento_atual = query_duckdb(f"""
            SELECT status_alinhamento,
                   COUNT(*) AS total,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM spec_dinamica_trabalho_satisfacao {filtro_alinhamento}), 1) AS pct
            FROM spec_dinamica_trabalho_satisfacao
            {filtro_alinhamento}
            GROUP BY 1 ORDER BY pct ASC
        """)
        fig12 = px.bar(
            df_alinhamento_atual, x='pct', y='status_alinhamento', orientation='h',
            title=f"<b>Alinhamento entre Regime Atual vs Ideal ({label_filtro})</b>",
            labels={'pct': '% dos Profissionais', 'status_alinhamento': 'Status'},
            color_discrete_sequence=['#845ef7'], text='pct'
        )
        fig12.update_traces(texttemplate='%{text}%', textposition='inside')
        fig12.update_layout(template='plotly_white', height=450)
        st.plotly_chart(fig12, use_container_width=True)

# =============================================================================
# ABA 7: Desafios & Roadmap Estratégico
# =============================================================================
with tabs[6]:
    st.header("🎯 Pergunta 7: Quais oportunidades e desafios foram identificados para investimento?")
    st.markdown("""
    * **A Grande Mudança de Gargalo**: A preocupação com **Dados Despreparados / Falta de Governança** aumentou **+29.2%** entre 2023 e 2025.
    * **Roadmap de Ação Executivo**: Estruturar governança e qualidade antes de adquirir ferramentas enterprise caras de IA.
    """)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        filtro_barreiras = f"WHERE tipo_registro = 'Barreira' AND ano_pesquisa = {ano_selecionado}" if ano_selecionado != "Todos os Anos (2023–2025)" else "WHERE tipo_registro = 'Barreira'"
        df_barreiras = query_duckdb(f"""
            SELECT indicador_ia_label AS barreira,
                   COUNT(DISTINCT respondente_key) AS ocorrencias,
                   ROUND(100.0 * COUNT(DISTINCT respondente_key) / (SELECT COUNT(DISTINCT respondente_key) FROM spec_adocao_ia {filtro_barreiras}), 1) AS pct_barreiras
            FROM spec_adocao_ia
            {filtro_barreiras}
            GROUP BY 1 ORDER BY pct_barreiras ASC
        """)
        fig13 = px.bar(
            df_barreiras, x='pct_barreiras', y='barreira', orientation='h',
            title=f"<b>Principais Barreiras para Adoção de IA ({label_filtro})</b>",
            labels={'pct_barreiras': '% das Empresas com a Barreira', 'barreira': 'Barreira'},
            color_discrete_sequence=['#c92a2a'], text='pct_barreiras'
        )
        fig13.update_traces(texttemplate='%{text}%', textposition='inside')
        fig13.update_layout(template='plotly_white', height=450)
        st.plotly_chart(fig13, use_container_width=True)
        
    with col_b:
        st.markdown("### 📋 Roadmap Estratégico para Diretoria")
        resumo_diretoria = pd.DataFrame([
            {"Pilar": "Pessoas & Diversidade", "Diagnóstico": "Mulheres estagnadas em 23% e pay gap de 19.4%.", "Ação": "Auditoria de faixas salariais e metas afirmativas para liderança técnica."},
            {"Pilar": "Stack Tecnológico", "Diagnóstico": "Expansão de Databricks (+29.6%) e AWS (+38.7%).", "Ação": "Consolidar Lakehouse e padronizar pipelines distribuídos com PySpark/SQL."},
            {"Pilar": "Investimento em IA", "Diagnóstico": "Falta de governança de dados cresceu +29.2%.", "Ação": "Priorizar catálogo e qualidade de dados antes de contratar LLMs caras."}
        ])
        st.dataframe(resumo_diretoria, hide_index=True, use_container_width=True)

# =============================================================================
# ABA 8: Balanço Temporal Multianual
# =============================================================================
with tabs[7]:
    st.header("📈 Balanço Temporal Multianual (2023 ➔ 2024 ➔ 2025)")
    st.markdown("Visão executiva consolidada de todas as taxas de crescimento (**evolução**) e recuo (**regressão**) do mercado brasileiro:")
    
    tabela_yoy = pd.DataFrame([
        {"Eixo Estratégico": "Especialistas em Machine Learning & IA", "2023": "2.4%", "2024": "3.4%", "2025": "5.5%", "Variação (2023-2025)": "+129.2%", "Status": "🚀 Forte Evolução"},
        {"Eixo Estratégico": "Salário Médio em Machine Learning & IA", "2023": "R$ 12.573", "2024": "R$ 15.840", "2025": "R$ 19.080", "Variação (2023-2025)": "+51.7%", "Status": "💰 Forte Evolução"},
        {"Eixo Estratégico": "IA Integrada a Processos/Produtos", "2023": "21.6%", "2024": "29.8%", "2025": "28.9%", "Variação (2023-2025)": "+33.8%", "Status": "📈 Evolução"},
        {"Eixo Estratégico": "Adoção de Databricks (Lakehouse)", "2023": "15.2%", "2024": "21.4%", "2025": "19.7%", "Variação (2023-2025)": "+29.6%", "Status": "📈 Evolução"},
        {"Eixo Estratégico": "Liderança de Nuvem (AWS)", "2023": "20.9%", "2024": "30.4%", "2025": "29.0%", "Variação (2023-2025)": "+38.7%", "Status": "📈 Evolução"},
        {"Eixo Estratégico": "Trabalho 100% Remoto", "2023": "46.3%", "2024": "45.7%", "2025": "39.7%", "Variação (2023-2025)": "-6.6 p.p.", "Status": "⚠️ Regressão (Retorno ao Escritório)"},
        {"Eixo Estratégico": "Representatividade Feminina Geral", "2023": "24.3%", "2024": "23.3%", "2025": "23.0%", "Variação (2023-2025)": "-1.3 p.p.", "Status": "⚠️ Estagnação / Leve Regressão"},
        {"Eixo Estratégico": "Pay Gap Salarial Homens vs Mulheres", "2023": "18.0%", "2024": "19.3%", "2025": "19.4%", "Variação (2023-2025)": "+1.4 p.p.", "Status": "⚠️ Regressão (Aumento do Gap)"},
        {"Eixo Estratégico": "Criticidade de Governança de Dados em IA", "2023": "4.8%", "2024": "5.5%", "2025": "6.2%", "Variação (2023-2025)": "+29.2%", "Status": "⚠️ Alerta Crítico"}
    ])
    
    st.dataframe(tabela_yoy, hide_index=True, use_container_width=True)
    
    csv_data = tabela_yoy.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Tabela de Evolução Histórica (CSV)",
        data=csv_data,
        file_name="evolucao_historica_dados_ia_brasil_2023_2025.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("💡 *Painel Executivo desenvolvido com Streamlit, DuckDB e Plotly | Tech Challenge - Fase 3*")
