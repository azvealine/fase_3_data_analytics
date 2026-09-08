# Estado de Dados Brasil: SPECS Analíticas, Dashboards Executivos & App Streamlit
**Tech Challenge - Fase 3 | Pós-Graduação em Data Analytics**

---

## 1. Visão Geral e Objetivo

Este projeto estabelece uma camada analítica robusta a partir da **SOT (Source of Truth)** do *State of Data Brasil*, gerando **7 SPECS analíticas especializadas** em formato Parquet para responder diretamente às 7 perguntas estratégicas de negócio e traçar a **evolução temporal histórica (2023 ➔ 2024 ➔ 2025)**:

1. **Como está estruturado o mercado brasileiro de Dados?**
2. **Quais perfis profissionais são mais valorizados pelo mercado?**
3. **Qual é o cenário de diversidade de gênero nas carreiras de dados?**
4. **Quais tecnologias apresentam maior adoção entre os profissionais?**
5. **Qual é o índice de adoção de Inteligência Artificial e seu impacto?**
6. **Existem diferenças relevantes entre regiões, senioridades ou modelos de trabalho?**
7. **Quais oportunidades e desafios podem ser identificados para empresas que desejam investir em Dados e IA?**

---

## 2. Arquitetura da Solução

```text
dados/base_consolidada.parquet (SOT Auditável - 14.005 respondentes)
       │
       ▼ [01_engenharia_specs_pyspark.ipynb] (Apache Spark Engine)
       ├── 1. spec_respondentes.parquet                  (14.005 linhas, 24 colunas)
       ├── 2. spec_adocao_tecnologias.parquet            (65.336 linhas, 17 colunas)
       ├── 3. spec_adocao_ia.parquet                     (30.355 linhas, 18 colunas)
       ├── 4. spec_diversidade_carreira.parquet          (681 linhas, 10 colunas)
       ├── 5. spec_segmentacao_negocio.parquet           (1.224 linhas, 11 colunas)
       ├── 6. spec_dinamica_trabalho_satisfacao.parquet  (14.005 linhas, 13 colunas)
       └── 7. spec_estrutura_times_empresa.parquet       (10.623 linhas, 9 colunas)
       │
       ├────────────────────────────────────────────────┐
       ▼                                                ▼
[02_dashboards_executivos.ipynb]             [app.py] (Aplicação Web Streamlit)
(Notebook Executivo Interativo Plotly/DuckDB)   (Painel Web com Filtros, KPIs & Abas)
```

---

## 3. Dicionário das SPECS Analíticas (`dados/bases_analiticas/`)

| # | SPEC | Finalidade & Pergunta Atendida | Granularidade | Principais Atributos |
|---|---|---|---|---|
| **1** | **`spec_respondentes.parquet`** | Dimensão consolidada do profissional com padronização salarial e macro-cargos (P1 & P2) | 1 registro por respondente/ano | `respondente_key`, `macro_cargo`, `faixa_idade`, `genero`, `nivel`, `salario_estimado_num`, `ordem_salarial`, `modelo_trabalho_resumido` |
| **2** | **`spec_adocao_tecnologias.parquet`** | Análise granular de adoção de stack tecnológico enriquecida com cargo e remuneração (P4 & P2) | 1 registro por respondente x tecnologia | `familia` (Linguagem, Cloud, Banco, ETL), `tecnologia`, `tecnologia_principal`, `macro_cargo`, `salario_estimado_num` |
| **3** | **`spec_adocao_ia.parquet`** | Separação explícita de uso ativo vs barreiras organizacionais e governança (P5 & P7) | 1 registro por respondente x indicador | `categoria_ia` (Uso Individual, Uso Corporativo, Barreira), `tipo_registro`, `indicador_ia_label`, `macro_cargo` |
| **4** | **`spec_diversidade_carreira.parquet`** | Visão agregada especializada em equidade salarial, efeito funil e pay gap (P3) | 1 registro por combinação de gênero, raça, cargo e nível | `macro_cargo`, `nivel`, `genero`, `cor_raca_etnia`, `respondentes`, `salario_medio`, `salario_mediano`, `remoto_pct` |
| **5** | **`spec_segmentacao_negocio.parquet`** | Segmentação executiva para planejamento de headcount, compensação e IA (P6 & P2) | 1 registro por cluster de negócio | `macro_cargo`, `nivel`, `regiao_onde_mora`, `modelo_trabalho_resumido`, `total_respondentes`, `salario_medio_estimado`, `pct_adotantes_ia`, `pct_mulheres` |
| **6** | **`spec_dinamica_trabalho_satisfacao.parquet`** | Análise de descompasso entre modelo de trabalho atual vs ideal e retenção de talentos (P6 & P7) | 1 registro por respondente | `modelo_trabalho_resumido`, `modelo_ideal_resumido`, `status_alinhamento`, `oportunidade_buscada`, `salario_estimado_num` |
| **7** | **`spec_estrutura_times_empresa.parquet`** | Composição, papéis e maturidade organizacional das equipes de dados nas empresas (P1 & P7) | 1 registro por respondente x papel da empresa | `setor`, `papel_na_empresa`, `papel_id`, `presente_na_empresa` |

---

## 4. Como Executar

### 1. Criar o Ambiente Virtual:

python -m venv venv

### 2. Ativar o Ambiente Virtual:
* *PowerShell*: `.\venv\Scripts\activate`
* *Git Bash*: `source .venv-1/Scripts/activate`

### 3. Instalar bibliotecas:
* *PowerShell*: `pip install -r .\requirements.txt`

### 4. Rodar a Aplicação Web Streamlit:
```bash
streamlit run app.py
```
Acesse no seu navegador: `http://localhost:8501`.

### 5. Rodar os Notebooks Jupyter:
* **Engenharia de Dados (PySpark)**: `jupyter notebook 01_engenharia_specs_pyspark.ipynb`
* **Dashboards Executivos (< 2s)**: `jupyter notebook 02_dashboards_executivos.ipynb`

