# -*- coding: utf-8 -*-
# Case OpenAI - código desenvolvido no Google Colab

# No Colab: !pip install openai pydantic --quiet

# importando as bibliotecas
import pandas as pd
from google.colab import userdata
import os
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError
from pydantic import BaseModel, Field
from typing import Literal
import json

# tabela raw

df = pd.read_csv('tickets_case.csv')
df.head()

# Data Profiling

print(df.shape)
print(df.info())

colunas = ['data', 'genero', 'cidade', 'estado', 'plano', 'canal']

for coluna in df.columns:
  if coluna in colunas:
    print(df[coluna].value_counts().sort_index(), "\n")

# problema de data
# problema de letra maiscula/minuscula
# problema de espaço
# problema de estado por extenso

# Data Cleaning

# para as colunas 'cidade', 'plano', 'canal'

colunas_limpeza = ['cidade', 'plano', 'canal']

df[colunas_limpeza] = df[colunas_limpeza].apply(lambda coluna: coluna.str.strip().str.title())

for coluna in df.columns:
  if coluna in colunas_limpeza:
    print(df[coluna].value_counts(), '\n')

# para a coluna de estado

df['estado'] = df['estado'].str.strip().str.upper()

df.loc[df['estado']=='RIO GRANDE DO SUL', 'estado'] = 'RS'

df['estado'].value_counts()

# para a coluna de data

df["data_tratada"] = pd.to_datetime(
    df["data"],
    errors="coerce",
    dayfirst=True,
    format="mixed"
)

print(df["data_tratada"].dtype)

print(df.loc[df['data_tratada'].isna()])

print(df.loc[df['cliente']=='Murilo M.'])
print(df.loc[df['cliente']=='Fernanda H.'])

df["status_data"] = "válida"
df.loc[df["data"].isna(), "status_data"] = "ausente"
df.loc[
    df["data"].notna() & df["data_tratada"].isna(),
    "status_data"
] = "inválida"

# ajustes finais de deduplicação

print(df.info())

df = df.drop_duplicates()
df.drop(columns=['data'], inplace=True)

print(df.info())

# chamando a API

os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")

cliente = OpenAI()

# definindo os padrões de resposta

class TicketClassificado(BaseModel):
    categoria: Literal["cobranca", "acesso", "bug", "funcionalidade", "elogio", "outros"]
    prioridade: Literal["baixa", "media", "alta"]
    resumo: str = Field(description="Resumo do ticket em uma único frase curta.")
    sentimento: Literal["positivo", "neutro", "negativo"]

# criando a função

def chamando_api(ticket):
  resposta = cliente.beta.chat.completions.parse(
      model="gpt-4o-mini",
      messages=[
          {
              "role": "system",
              "content": "Você classifica tickets de suporte da empresa Xpto."
          },
          {
              "role": "user",
              "content": ticket
          }
      ],
      response_format=TicketClassificado
  )
  return [
      resposta.choices[0].message.parsed,
      resposta.choices[0].finish_reason,
      [resposta.usage.completion_tokens, resposta.usage.prompt_tokens, resposta.usage.total_tokens]
      ]

dict_resultados = {}
dict_custo = {
    'token_resposta_ia': 0,
    'token_pergunta_user': 0,
    'token_total': 0
}

# iterando nas linhas do df
for i in df.index:

  id = df.loc[i, 'id']
  ticket = df.loc[i, 'texto']

  try:

    # chamando a api
    resultado = chamando_api(ticket)

    # registrado o consumo da chamada
    df.loc[i, 'token_resposta_ia'] = resultado[2][0]
    df.loc[i, 'token_pergunta_user'] = resultado[2][1]
    df.loc[i, 'token_total'] = resultado[2][2]

    dict_custo['token_resposta_ia'] += resultado[2][0]
    dict_custo['token_pergunta_user'] += resultado[2][1]
    dict_custo['token_total'] += resultado[2][2]

    # analisando o resultado da chamada
    encerramento_chamada = resultado[1]

    if encerramento_chamada == 'stop':

      resposta_estruturada = resultado[0]

      if resposta_estruturada is not None:

        dict_resultados[int(id)] = {
            'categoria': resultado[0].categoria,
            'prioridade': resultado[0].prioridade,
            'resumo': resultado[0].resumo,
            'sentimento': resultado[0].sentimento
        }

        df.loc[i, 'categoria'] = resultado[0].categoria
        df.loc[i, 'prioridade'] = resultado[0].prioridade
        df.loc[i, 'resumo'] = resultado[0].resumo
        df.loc[i, 'sentimento'] = resultado[0].sentimento

    elif encerramento_chamada == 'length':
      print(f'Ticket {id}: API atingiu limite de tokens')

    else:
      print(f'Ticket {id}: API terminou por outro motivo: {encerramento_chamada}')

  except RateLimitError as erro:
    print(f'Ticket {id}: limite de requisições da API.')
    continue

  except APIConnectionError as erro:
    print(f'Ticket {id}: erro de conexão com a API.')
    continue

  except APIStatusError as erro:
    print(f'Ticket {id}: erro da API - status {erro.status_code}.')
    continue

  except Exception as erro:
    print(f'Ticket {id}: erro desconhecido - {erro}')
    continue

# calculando o custo da LLM

input_tokens = dict_custo['token_pergunta_user']
output_tokens = dict_custo['token_resposta_ia']

custo_input = (input_tokens / 1_000_000) * 0.15
custo_output = (output_tokens / 1_000_000) * 0.60

custo_total = custo_input + custo_output

dict_custo['custo_pergunta'] = custo_input
dict_custo['custo_resposta'] = custo_output
dict_custo['custo_total'] = custo_total

dict_custo

# salvando o dataframe curated em excel e parquet

df.to_excel('tickets_curated.xlsx', index=False)
df.to_parquet("tickets_curated.parquet", index=False)

df.head()

# salvando o resultado em json

dict_final = {
    'resultados': dict_resultados,
    'custos': dict_custo
}

with open("resultado.json", "w", encoding="utf-8") as arquivo:
    json.dump(dict_final, arquivo, ensure_ascii=False, indent=4)

dict_final
