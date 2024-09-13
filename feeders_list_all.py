import pandas as pd
import os

# Obter o diretório onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Carregar o arquivo CSV
ctmt = pd.read_csv(r'Inputs\CTMT.csv', sep=',')


    # Lista de todos os feeders
def get_cod_id_list():
    cod_id_list = ctmt['COD_ID'].tolist()
    cod_id_list.sort()  # Ordenar a lista em ordem alfabética

    return cod_id_list


# Chamar a função para obter a lista de feeders
cod_id_list = get_cod_id_list()
print(cod_id_list)
