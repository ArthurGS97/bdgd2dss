import os
import pandas as pd
import py_dss_interface
import math
import re

######## Entrada de dados ########
feeders_list = ['ULAU11']
##################################

script_dir = os.getcwd()

def feeders_feasibility(feeders_list):
    
    pref, nome, ano = nomes()
   
    # Carrega o arquivo CSV
    ctmt = pd.read_csv(rf'Inputs\{pref} — CTMT.csv', sep=',')

    # Inicializa o PyDSS
    dss = py_dss_interface.DSSDLL()

    data_list = []

    for feeder in feeders_list:
        filtered_ctmt = ctmt[ctmt['COD_ID'] == feeder]

        # Soma das colunas ENE_01 a ENE_12
        energy_columns = [f'ENE_{str(i).zfill(2)}' for i in range(1, 13)]
        energyBDGD = filtered_ctmt[energy_columns].sum().sum()

        energymeter = [0, 0, 0]
        conv = 'Sim'
        n = 0

        for dia in ["DU", "SA", "DO"]:
            print(f" Processando Feeder {feeder} - Dia {dia}")

            dss.file = rf"{script_dir}\{feeder}\Master_{feeder}_{dia}.dss"
            dss.text(f"compile {dss.file}")
            dss.solution_solve()
            dss.meters_write_name("EM1")

            valor = dss.meters_register_values()[0]

            # Verifica se o valor é inválido ou absurdo
            if (not isinstance(valor, (int, float))) or math.isnan(valor) or abs(valor) > 1e9:
                valor = "error"

            energymeter[n] = valor
            n += 1
            
            du, sa, do = contador_dias(ano)
            # Verifica convergência apenas para o dia útil
            if dia == "DU":
                teste_conv = dss.solution_read_converged()
                if teste_conv == 0:
                    conv = 'Não'

        # Se não convergiu, marca energia anual como "error"
        if conv == 'Não':
            energymeteryear = "error"
        else:
            # Se algum valor diário for "error", energia anual também vira "error"
            if any(isinstance(e, str) and e == "error" for e in energymeter):
                energymeteryear = "error"
            else:
                energymeteryear = energymeter[0] * du + energymeter[1] * sa + energymeter[2] * do

        data_list.append({
            "Feeder": feeder,
            "Converged": conv,
            "Energia DU (kWh)": energymeter[0],
            "Energia SA (kWh)": energymeter[1],
            "Energia DO (kWh)": energymeter[2],
            "Energia Ano Simulada (kWh)": energymeteryear,
            "Energia CTMT (kWh)": energyBDGD,
        })

    # Cria DataFrame final
    df = pd.DataFrame(data_list)


    filename = os.path.join(script_dir, f"{nome}.xlsx")
    df.to_excel(filename, index=False)


def nomes():
    for nome_arquivo in os.listdir(os.path.join(script_dir, 'Inputs')):
        if nome_arquivo.endswith('— SEGCON.csv'):  
            pref = nome_arquivo.replace(' — SEGCON.csv', '')
    
    partes = pref.split('_')
    ano = None
    indice_ano = None
    for i, parte in enumerate(partes):
        match = re.search(r'\b(20\d{2})\b', parte)
        if match:
            ano = match.group(1)
            indice_ano = i
            break

    partes_conc = [p for p in partes[:indice_ano] if not p.isdigit()]
    nome = f"{'_'.join(partes_conc)}_{ano}"

    return pref, nome, ano

def contador_dias(ano):
    ano = int(ano)
    if ano == 2016:
        return 252, 53, 61
    elif ano == 2017:
        return 249, 52, 64
    elif ano == 2018:
        return 250, 52, 63
    elif ano == 2019:
        return 253, 52, 60
    elif ano == 2020:
        return 251, 52, 61
    elif ano == 2021:
        return 252, 52, 61
    elif ano == 2022:
        return 252, 53, 60
    elif ano == 2023:
        return 249, 52, 64
    elif ano == 2024:
        return 254, 52, 59
    elif ano == 2025:
        return 253, 52, 60
# Contagem de dias (DU, SA e DO) para cada ano. Fonte: https://www.dias-uteis.com/
    
feeders_feasibility(feeders_list)
