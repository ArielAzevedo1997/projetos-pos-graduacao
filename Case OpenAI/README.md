# Case OpenAI — Classificação de Tickets de Suporte com LLM

Projeto de portfólio desenvolvido para aplicar conceitos de **Engenharia de Dados, Analytics e IA Generativa** usando Python e a OpenAI API.

## Objetivo

Simular um pipeline de dados para uma plataforma de suporte ao cliente. O case parte de uma base bruta com problemas intencionais de qualidade, realiza profiling e limpeza dos dados e usa uma LLM para transformar o texto livre dos tickets em atributos estruturados para análise.

## Fluxo do projeto

```text
tickets_case.csv
      ↓
Data Profiling
      ↓
Data Cleaning
      ↓
Deduplicação
      ↓
OpenAI API + Structured Outputs
      ↓
Classificação dos tickets
      ↓
tickets_curated.xlsx / tickets_curated.parquet
      ↓
resultado.json
```

## Dataset

A base bruta contém **220 registros**, com **20 duplicações exatas intencionais** (200 registros únicos), além de inconsistências inseridas propositalmente para exercício de Data Quality:

- datas em formatos diferentes;
- datas inválidas e ausentes;
- espaços extras;
- diferenças entre maiúsculas e minúsculas;
- estado informado por extenso;
- valores categóricos com variações de escrita.

Dimensões disponíveis para análise:

- cliente;
- gênero;
- cidade;
- estado;
- plano;
- canal;
- texto do ticket.

## Enriquecimento com IA

A OpenAI API é utilizada com **Structured Outputs** e um schema Pydantic para classificar cada ticket em:

- `categoria`: cobranca, acesso, bug, funcionalidade, elogio ou outros;
- `prioridade`: baixa, media ou alta;
- `resumo`: resumo do ticket em uma frase;
- `sentimento`: positivo, neutro ou negativo.

O pipeline também captura o motivo de encerramento da geração, contabiliza tokens e possui tratamento de exceções para rate limit, falhas de conexão, erros de status da API e erros não previstos.

## Métricas da execução disponibilizada

- Tickets classificados: **198**
- Tokens de entrada: **34.546**
- Tokens de saída: **6.200**
- Tokens totais: **40.746**
- Custo estimado pela tarifa utilizada no código: **US$ 0,008902**

> Os artefatos de saída incluídos no repositório refletem a execução registrada em `resultado.json`.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `case_api_openai.py` | Código principal do case |
| `tickets_case.csv` | Camada raw / dataset de entrada |
| `tickets_curated.xlsx` | Saída curated em Excel |
| `tickets_curated.parquet` | Saída curated em Parquet |
| `resultado.json` | Classificações e métricas agregadas de tokens/custo |
| `requirements.txt` | Dependências Python |

## Tecnologias

- Python
- Pandas
- OpenAI API
- Pydantic
- JSON
- Parquet
- Google Colab

## Execução

O código foi desenvolvido no **Google Colab**.

1. Instale as dependências:

```python
!pip install -r requirements.txt
```

2. Faça upload do arquivo `tickets_case.csv` para o ambiente do Colab.
3. Cadastre sua chave como secret `OPENAI_API_KEY` no Colab.
4. Execute o código.

A chave da API **não é armazenada no repositório**.

## Conceitos praticados

- Data Profiling
- Data Cleaning
- Data Quality
- Deduplicação
- Tratamento de datas
- Integração com API
- Structured Outputs
- Validação de schema com Pydantic
- Tratamento de exceções
- Monitoramento de tokens
- Estimativa de custo de LLM
- Persistência em CSV, Excel, Parquet e JSON
- Enriquecimento de dados não estruturados com IA generativa

## Observação

Os dados deste projeto são **sintéticos e utilizados exclusivamente para fins educacionais e de portfólio**.
