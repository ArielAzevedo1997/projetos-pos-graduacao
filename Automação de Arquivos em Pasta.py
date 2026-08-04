# PROJETO CURSO


import pandas as pd
import os
from pathlib import Path
import shutil


# caminhos
caminho = Path(r"C:\Users\ariel.azevedo_beepsa\Desktop\relatorios")
nova_pasta = Path(os.path.join(caminho, r"relatorios_processados"))


# verificação da nova pasta
if nova_pasta.exists() == False:
    Path.mkdir(nova_pasta)
    print(f"Pasta criada com sucesso! {nova_pasta}")
else:
    print('Pasta já existe!')
   

# criando o DataFrame que vamos incluir os relatórios processados
if Path(fr'{caminho}\Relatorios_consolidados.xlsx').is_file():
    df = pd.read_excel(Path(fr'{caminho}\Relatorios_consolidados.xlsx'))
    print("Arquivo já existe")
else:
    df = pd.DataFrame()
    print("Arquivo criado")


# iteração pelos arquivos da pasta anterior
for arquivo in caminho.iterdir():

    #print(arquivo)

    # se os arquivos foram excel e já tiverem sido processados, vão mudar de pasta e serem incluídos no Arquivo Consolidado
    if arquivo.suffix == '.xlsx':
        nome_arquivo = arquivo.stem.split("_")
        
        if nome_arquivo[-1] == 'processado':
            
            df_arquivo = pd.read_excel(arquivo)
            df_arquivo['Arquivo_referencia'] = " ".join(arquivo.stem.split("_")[0:2])
            df = pd.concat([df, df_arquivo])
            
            shutil.move(arquivo, os.path.join(nova_pasta, arquivo.name))
    
    
print(df)
df.to_excel(f'{caminho}\Relatorios_consolidados.xlsx', index=False)

print('Fim da Rotina!')