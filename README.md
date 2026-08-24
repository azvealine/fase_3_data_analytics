 # Estado de Dados Brasil: SPECS e Dashboards Executivos

## 1. Objetivo

Este projeto transforma a base consolidada do State of Data Brasil em **SPECS analíticas** e dashboards executivos para apoiar decisões de tecnologia, pessoas e investimento em Inteligência Artificial.

As análises respondem às seguintes perguntas:

- Qual é o cenário de diversidade de gênero nas carreiras de dados?
- Quais tecnologias apresentam maior adoção?
- Qual é o índice de adoção de IA e qual é o seu impacto observado?
- Existem diferenças por região, senioridade ou modelo de trabalho?
- Quais oportunidades e desafios existem para empresas que investem em Dados e IA?

## 2. Fonte oficial e camada analítica

### SOT: Source of Truth

`dados/base_consolidada.parquet` é a **SOT do projeto**. Ela é a fonte oficial, consolidada e auditável dos respondentes dos surveys.

O notebook analítico **não recria a SOT**. Ele apenas a lê para produzir as estruturas derivadas.

### SPECS analíticas

As SPECS ficam em `dados/bases_analiticas/` e possuem finalidade analítica específica:

| SPEC | Finalidade | Granularidade principal |
|---|---|---|
| `spec_respondentes.parquet` | Perfil demográfico, profissional e de trabalho | Um registro por respondente e ano |
| `spec_adocao_tecnologias.parquet` | Tecnologias, plataformas, cloud e ETL utilizadas | Um registro por respondente, família e tecnologia |
| `spec_adocao_ia.parquet` | Indicadores de uso de IA e barreiras | Um registro por respondente e indicador |
| `spec_diversidade_carreira.parquet` | Análises de gênero, raça, formação e carreira | Um registro por respondente e ano |
| `spec_segmentacao_negocio.parquet` | Segmentação para decisões de negócio | Um registro por combinação de segmentos |

Fluxo de dados:

```text
base_consolidada.parquet (SOT)
	|
	v
transformação analítica
	|
	v
SPECS em dados/bases_analiticas/
	|
	v
indicadores e dashboards executivos
```

## 3. Notebook recomendado

O notebook principal para apresentação é:

`02_specs_analiticas_dashboards_executivos.ipynb`

Ele começa diretamente na camada analítica e contém oito células organizadas em quatro blocos:

1. **Consumo da SOT e geração das SPECS**
2. **Dashboards executivos de segmentação**
3. **Evolução anual**
4. **Resumo para diretoria**
