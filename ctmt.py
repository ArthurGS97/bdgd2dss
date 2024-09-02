import pandas as pd

# Carregar o arquivo CSV
ctmt = pd.read_csv(r'Inputs\CTMT_Uberlandia.csv', sep=',')

# Lista dos alimentadores desejados
alimentadoresudia = [
    'ULAU01', 'ULAU02', 'ULAU03', 'ULAU05', 'ULAU11', 'ULAU12', 'ULAU13',
    'ULAU14', 'ULAU15', 'ULAU35', 'ULAU36', 'ULAU37', 'ULAU38', 'ULAU41',
    'ULAD202', 'ULAD203', 'ULAD204', 'ULAD205', 'ULAD206', 'ULAD208',
    'ULAD209', 'ULAD210', 'ULAD211', 'ULAD212', 'ULAD215', 'ULAD216',
    'ULAD217', 'ULAD218', 'ULAD219', 'ULAS602', 'ULAS603', 'ULAS604',
    'ULAS606', 'ULAS607', 'ULAS609', 'ULAS610', 'ULAS612', 'ULAS613',
    'ULAS614', 'ULAS626', 'ULAS627', 'ULAS628', 'ULAS629', 'ULAS633',
    'ULAS634', 'ULAE704', 'ULAE705', 'ULAE707', 'ULAE708', 'ULAE709',
    'ULAE712', 'ULAE713', 'ULAE714', 'ULAE716', 'ULAE718', 'ULAE721',
    'ULAE722', 'ULAE724', 'ULAE726', 'ULAE728', 'ULAN902', 'ULAN903'
]

# Filtrar o DataFrame pelos alimentadores desejados
ctmt_filtered = ctmt[ctmt['COD_ID'].isin(alimentadoresudia)]

# Calcular a soma da potência ao longo do ano para cada alimentador
ctmt_filtered['Potencia_Anual'] = ctmt_filtered[['ENE_01', 'ENE_02', 'ENE_03', 'ENE_04', 'ENE_05', 'ENE_06', 'ENE_07', 'ENE_08', 'ENE_09', 'ENE_10', 'ENE_11', 'ENE_12']].sum(axis=1)

# Gerar o arquivo de texto com o nome do alimentador e a potência anual
with open('potencia_anual.txt', 'w') as f:
    for index, row in ctmt_filtered.iterrows():
        f.write(f"{row['COD_ID']} {row['Potencia_Anual']}\n")


