import pandas as pd
import time
import os
import py_dss_interface
import dicionarios as dic
from multiprocessing import Pool
import re


# Função que lista todos os alimentadores
script_dir = os.path.dirname(os.path.abspath(__file__))


def prefixo_bdgd():
    for nome_arquivo in os.listdir(os.path.join(script_dir, 'Inputs')):
        if nome_arquivo.endswith('— SEGCON.csv'):  # usa o travessão (não o hífen!)
            pref = nome_arquivo.replace(' — SEGCON.csv', '')  # remove o final para obter o prefixo
            return pref
    raise FileNotFoundError("Nenhum arquivo com sufixo '— SEGCON.csv' foi encontrado na pasta.")

pref = prefixo_bdgd()

def feeders_list():
    # Carregar o arquivo CSV
    ctmt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — CTMT.csv', sep=',')


    feeders_list = ctmt['COD_ID'].tolist()
    feeders_list.sort()  # Ordenar a lista em ordem alfabética

    return feeders_list

#Função para gerar o arquivo Master.dss
def generate_master(x, y, z, w, feeder, dicionario_kv, dia_de_analise, mvasc1, mvasc3, output_dir=None):
    start_master = time.time()

    ctmt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — CTMT.csv', sep=',', low_memory=False)

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'Master_{feeder}_{dia_de_analise}.dss')

    with open(output_file_path, 'w') as arquivo:
        
        # Encontrar o cod_untrat e pac_ini correspondentes
        linha_feeder = ctmt[ctmt['COD_ID'] == feeder].iloc[0]
        pac_ini = linha_feeder['PAC_INI']  # Ponto de acoplamento comum elétrico inicial  
        kv = dicionario_kv[linha_feeder['TEN_NOM']]
        tape = linha_feeder['TEN_OPE']

   
        cont1 = [
            "Clear\n",
            f"New circuit.{feeder} bus1=source.1.2.3 basekv={kv} pu={tape} angle=0 phases=3 frequency=60 mvasc3={mvasc3} mvasc1={mvasc1}\n",
            f"New line.sub{feeder} bus1=source.1.2.3 bus2={pac_ini}.1.2.3 phases=3 length=0.0001 r1=0.0001 x1=0.0001 units=km\n\n",
            "Redirect linecode.dss\n",
            f"Redirect crvcrg_{dia_de_analise}.dss\n",
            f"Redirect ssdMT_{feeder}.dss\n",
            f"Redirect trafosMT_{feeder}.dss\n",
            f"Redirect ssdBT_{feeder}.dss\n",
            f"Redirect ramlig_{feeder}.dss\n",
            f"Redirect ucbt_{feeder}.dss\n",
            f"Redirect ucmt_{feeder}.dss\n",
            f"Redirect pip_{feeder}.dss\n",
        ]

        if x==1: cont2 = [f"!Redirect gds_{feeder}.dss\n"] 
        else: cont2 = []
        if y==1: cont3 = [f"Redirect capacitores_{feeder}.dss\n"]
        else: cont3 = []
        if z== 1: cont4 = [f"Redirect unseMTBT_{feeder}.dss\n"]
        else: cont4 = []
        if w==1: cont5 = [f"Redirect unremt_{feeder}.dss\n\n"]
        else: cont5 = ["\n"]

        cont6 = [

            f"Redirect energymeters{feeder}.dss\n",

            "set tolerance = 0.01\n",
            "set Maxiter=100\n",
            "set mode = daily\n",
            "set stepsize = 1h\n",
            "set number = 24\n\n\n\n",
            "!Solve\n\n",
            f"!Buscoords coord_{feeder}.dss"

        ]
        
        conteudo = cont1 + cont2 + cont3 + cont4 + cont5 + cont6
        arquivo.writelines(conteudo)
        end_master = time.time()
        print(f"Master{feeder}_{dia_de_analise} Finalizado! - Tempo: {end_master - start_master:.2f} s")


def generate_crvcrg(output_dir=None):
    start_crvcrg = time.time()
    crvcrg = pd.read_csv(rf'{script_dir}\Inputs\{pref} — CRVCRG.csv', sep=',', low_memory=False)

    if output_dir is None:
        output_dir = os.getcwd()

    # Define os caminhos dos arquivos de saída
    output_file_path1 = os.path.join(output_dir, 'crvcrg_SA.dss')
    output_file_path2 = os.path.join(output_dir, 'crvcrg_DO.dss')
    output_file_path3 = os.path.join(output_dir, 'crvcrg_DU.dss')

    # Processa as curvas de carga para o dia Sábado (SA)
    with open(output_file_path1, 'w') as arquivo:
        for index, linha in crvcrg.iterrows():
            cod_id = linha.iloc[crvcrg.columns.get_loc("COD_ID")]
            dia = linha.iloc[crvcrg.columns.get_loc("TIP_DIA")]
            # Soma das potências de POT_01 até POT_96
            soma_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].sum()

            # Verifica se a soma das potências é zero e ignora o loadshape se for
            if soma_pot == 0:
                continue

            if dia == "SA":  # Sábado
                # Calcula as médias para cada conjunto de 4 potências
                potencias = [
                    linha.iloc[crvcrg.columns.get_loc(f"POT_{i:02}") : crvcrg.columns.get_loc(f"POT_{i+3:02}")+1].mean()
                    for i in range(1, 97, 4)
                ]
                
                # Calcula o máximo das potências médias
                max_pot = max(potencias)
                
                # Normaliza as potências pelo valor máximo
                potencias_normalizadas = [pot / max_pot for pot in potencias]
                
                # Escreve os dados no arquivo
                arquivo.write(f"New LoadShape.{cod_id} npts=24 interval=1\n")
                arquivo.write("~ mult=(" + " ".join(map(str, potencias_normalizadas)) + ")\n")


    # Processa as curvas de carga para o dia Domingo (DO)
    with open(output_file_path2, 'w') as arquivo:
        for index, linha in crvcrg.iterrows():
            cod_id = linha.iloc[crvcrg.columns.get_loc("COD_ID")]
            dia = linha.iloc[crvcrg.columns.get_loc("TIP_DIA")]
            soma_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].sum()

            # Ignora se a soma das potências for zero
            if soma_pot == 0:
                continue

            if dia == "DO":  # Domingo
                # Calcula as médias para cada conjunto de 4 potências
                potencias = [
                    linha.iloc[crvcrg.columns.get_loc(f"POT_{i:02}") : crvcrg.columns.get_loc(f"POT_{i+3:02}")+1].mean()
                    for i in range(1, 97, 4)
                ]
                
                # Calcula o máximo das potências médias
                max_pot = max(potencias)
                
                # Normaliza as potências pelo valor máximo
                potencias_normalizadas = [pot / max_pot for pot in potencias]
                
                # Escreve os dados no arquivo
                arquivo.write(f"New LoadShape.{cod_id} npts=24 interval=1\n")
                arquivo.write("~ mult=(" + " ".join(map(str, potencias_normalizadas)) + ")\n")

    # Processa as curvas de carga para o dia Útil (DU)
    with open(output_file_path3, 'w') as arquivo:
        for index, linha in crvcrg.iterrows():
            cod_id = linha.iloc[crvcrg.columns.get_loc("COD_ID")]
            dia = linha.iloc[crvcrg.columns.get_loc("TIP_DIA")]
            soma_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].sum()

            # Ignora se a soma das potências for zero
            if soma_pot == 0:
                continue

            if dia == "DU":  # Dia Útil
                # Calcula as médias para cada conjunto de 4 potências
                potencias = [
                    linha.iloc[crvcrg.columns.get_loc(f"POT_{i:02}") : crvcrg.columns.get_loc(f"POT_{i+3:02}")+1].mean()
                    for i in range(1, 97, 4)
                ]
                
                # Calcula o máximo das potências médias
                max_pot = max(potencias)
                
                # Normaliza as potências pelo valor máximo
                potencias_normalizadas = [pot / max_pot for pot in potencias]
                
                # Escreve os dados no arquivo
                arquivo.write(f"New LoadShape.{cod_id} npts=24 interval=1\n")
                arquivo.write("~ mult=(" + " ".join(map(str, potencias_normalizadas)) + ")\n")

    end_crvcrg = time.time()
    print(f"Curvas de Cargas Finalizadas! - Tempo: {end_crvcrg - start_crvcrg:.2f} s")



def generate_linecode(output_dir=None):
    start_linecode = time.time()
    segcon = pd.read_csv(rf'{script_dir}\Inputs\{pref} — SEGCON.csv', sep=',', low_memory=False) 
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'linecode.dss')   

    with open(output_file_path, 'w') as arquivo:


        for index, linha in segcon.iterrows():
            cod_id = linha["COD_ID"]
            r1 = linha["R1"]
            x1 = linha["X1"]
            cnom = linha["CMAX"]  

            arquivo.write(f"New linecode.{cod_id}_1 nphases=1 basefreq=60.0 units=km r1={r1} x1={x1} normamps={cnom}\n")
            arquivo.write(f"New linecode.{cod_id}_2 nphases=2 basefreq=60.0 units=km r1={r1} x1={x1} normamps={cnom}\n")
            arquivo.write(f"New linecode.{cod_id}_3 nphases=3 basefreq=60.0 units=km r1={r1} x1={x1} normamps={cnom}\n")
            arquivo.write(f"New linecode.{cod_id}_4 nphases=4 basefreq=60.0 units=km r1={r1} x1={x1} normamps={cnom}\n\n")


        
        end_linecode = time.time()
        print(f"Linecodes Finalizados! - Tempo: {end_linecode - start_linecode:.2f} s")

def generate_ssdmt(feeder, quant_fios, conex_fios, output_dir=None): #modificado n_phases para quant_fios (12/12)
    start_ssdmt = time.time()
    ssdMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — SSDMT.csv', sep=',', low_memory=False)
    # Filtrar apenas as linhas que pertencem ao alimentador escolhido
    ssdMT_filtered = ssdMT[ssdMT['CTMT'] == feeder]
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'ssdMT_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in ssdMT_filtered.iterrows():
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = linha["COMP"] / 1000  # Conversão metros (BDGD) para km (OpenDSS)
            linecode = linha["TIP_CND"]
            fases = linha["FAS_CON"]

            nfases = quant_fios.get(fases)
            conex = conex_fios.get(fases)
            

            arquivo.write(f"New line.mt{cod_id} phases={nfases} bus1={bus1}{conex} bus2={bus2}{conex} linecode={linecode}_{nfases} length={length} units=km \n")
        
        end_ssdmt = time.time()
        print(f"Linhas de Média do alimentador {feeder} Finalizadas! - Tempo: {end_ssdmt - start_ssdmt:.2f} s")

def generate_trafosMT(feeder, dicionario_kv, conex_fios_prim, conex_fios_sec, conex_fios_ter, mapeamento_conn, n_phases_trafo, output_dir=None):
    start_trafos = time.time()
    trafosMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNTRMT.csv', sep=',', low_memory=False)
    eqtrmt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — EQTRMT.csv', sep=',', low_memory=False)

    trafosMT = trafosMT[trafosMT['CTMT'] == feeder] 
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'trafosMT_{feeder}.dss') 

    trafo_n_localizado = []

    with open(output_file_path, 'w') as arquivo:
        for index, linha in trafosMT.iterrows():
            cod_id = str(linha["COD_ID"])  # Convertendo para string para garantir compatibilidade
            tape = linha["TAP"]
            tipo = linha["TIP_TRAFO"] 
            if tipo == "MT": windings = 3
            else: windings = 2
            

            eqtrmt_linha = eqtrmt[eqtrmt['UNI_TR_MT'].astype(str) == cod_id]  # Convertendo também para string

            if eqtrmt_linha.empty:
                trafo_n_localizado.append(cod_id)
                continue  # Pula para o próximo transformador

            xhl = eqtrmt_linha['XHL'].iloc[0]
            r = eqtrmt_linha['R'].iloc[0]
            cod_ten_pri = eqtrmt_linha['TEN_PRI'].iloc[0]
            cod_ten_sec = eqtrmt_linha['TEN_SEC'].iloc[0]
            cod_ten_ter = eqtrmt_linha['TEN_TER'].iloc[0]

            cod_lig_pri = eqtrmt_linha['LIG_FAS_P'].iloc[0]
            cod_lig_sec = eqtrmt_linha['LIG_FAS_S'].iloc[0]
            cod_lig_ter = eqtrmt_linha['LIG_FAS_T'].iloc[0]
            
            fases = n_phases_trafo.get(cod_lig_pri)  

            conex1 = conex_fios_prim.get(cod_lig_pri)
            conex2 = conex_fios_sec.get(cod_lig_sec)
            conn1 = mapeamento_conn.get(cod_lig_pri)
            conn2 = mapeamento_conn.get(cod_lig_sec)


            if linha["POT_NOM"]==0: continue
            
            loadloss = 100 * (linha["PER_TOT"] - linha["PER_FER"]) / (1000 * linha["POT_NOM"])
            noloadloss = 100 * (linha["PER_FER"]) / (1000 * linha["POT_NOM"])

            kva = linha["POT_NOM"]

            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            bus3 = linha["PAC_3"]


            if windings==2:
                arquivo.write(f"New transformer.{cod_id} phases={fases} xhl={xhl} %r={r} windings={windings} %loadloss={loadloss} %noloadloss={noloadloss}\n")
                arquivo.write(f"~ wdg=1 bus={bus1}{conex1} kv={dicionario_kv.get(cod_ten_pri, 'nao_localizado')} kva={kva} tap={tape} conn={conn1}\n")
                arquivo.write(f"~ wdg=2 bus={bus2}{conex2} kv={dicionario_kv.get(cod_ten_sec, 'nao_localizado')} kva={kva} tap={tape} conn={conn2}\n")
                arquivo.write(f'New Reactor.TF{cod_id} phases=1 bus1={bus2}.4 R=15 X=0 basefreq=60\n\n')

            if windings==3:
                xht = eqtrmt_linha['XHT'].iloc[0]
                if xht == 0: xht = xhl
                xlt = eqtrmt_linha['XLT'].iloc[0]
                if xlt == 0: xlt = xht

                conex3 = conex_fios_ter.get(cod_lig_ter)
                conn3 = mapeamento_conn.get(cod_lig_ter)



                arquivo.write(f"New transformer.{cod_id} phases={fases} xhl={xhl} xht={xht} xlt= {xlt} %r={r} windings={windings} %loadloss={loadloss} %noloadloss={noloadloss}\n")
                arquivo.write(f"~ wdg=1 bus={bus1}{conex1} kv={dicionario_kv.get(cod_ten_pri, 'nao_localizado')} kva={kva} tap={tape} conn={conn1}\n")
                arquivo.write(f"~ wdg=2 bus={bus2}{conex2} kv={dicionario_kv.get(cod_ten_sec, 'nao_localizado')} kva={kva} tap={tape} conn={conn2}\n")
                arquivo.write(f"~ wdg=3 bus={bus3}{conex3} kv={dicionario_kv.get(cod_ten_ter, 'nao_localizado')} kva={kva} tap={tape} conn={conn3}\n")
                arquivo.write(f'New Reactor.TF{cod_id} phases=1 bus1={bus2}.4 R=15 X=0 basefreq=60\n\n')

            
        end_trafos = time.time()

        if len(trafo_n_localizado) == 0:
            print(f"Tranformadores de Média do alimentador {feeder} Finalizados! - Tempo:{end_trafos - start_trafos:.2f} s")
        if len(trafo_n_localizado) > 0:
            print(f"Tranformadores de Média do alimentador {feeder} Finalizados! - Tempo:{end_trafos - start_trafos:.2f} s - Trafos não localizados: {trafo_n_localizado} ")

def generate_ssdBT(feeder, conex_fios, quant_fios, output_dir=None):
    start_ssdbt = time.time()
    ssdBT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — SSDBT.csv', sep=',', low_memory=False)
    ssdBT_filtered = ssdBT[ssdBT['CTMT'] == feeder]
    trafos_MT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNTRMT.csv', sep=',', low_memory=False)
    trafos_MT = trafos_MT[trafos_MT['CTMT'] == feeder]
    
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'ssdBT_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in ssdBT_filtered.iterrows():
            trafo = linha["UNI_TR_MT"]
            trafo_linha = trafos_MT[trafos_MT['COD_ID'] == trafo]
            if trafo_linha.empty: continue

            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = linha["COMP"] / 1000.0  # Convertendo metros para km
            linecode = linha["TIP_CND"]
            fases = linha["FAS_CON"]

            conex = conex_fios.get(fases)
            phases = quant_fios.get(fases)

            arquivo.write(f"New line.bt{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode}_{phases}\n")
        
        end_ssdbt = time.time()
        print(f"Linhas de Baixa do alimentador {feeder} Finalizadas! - Tempo: {end_ssdbt - start_ssdbt:.2f} s")

def generate_ucmt(feeder, conex_fios, mapeamento_conn_load, dicionario_kv, n_phases_load, output_dir=None): #modificado dicionario conex_fios_prim para conex_fios e n_phases para n_phases_load, conex_fios para mapeamento_conn_load (12/12)
    start_ucmt = time.time()
    ucmt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UCMT_tab.csv', sep=',', low_memory=False)
    ucmt_filtered = ucmt[ucmt['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'ucmt_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:

        for index, linha in ucmt_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            potencia = sum(linha[f"ENE_{i:02}"] for i in range(1, 13)) / (365 * 24)
            if potencia == 0: continue
            curvacarga = linha["TIP_CC"]


            lig = linha["FAS_CON"]

            phases = n_phases_load.get(lig)
            conex = conex_fios.get(lig)
            conn = mapeamento_conn_load.get(lig)

            kv = dicionario_kv.get(linha["TEN_FORN"])
            fp = 0.92

            #arquivo.write(f"New load.mt{cod_id} phases={phases} bus={bus}{conex} kv={kv} kw={potencia} pf={fp} conn=delta model = 8 ZIPV = [0.5 0 0.5 0 0 1 0.9]  daily={curvacarga}\n")

            arquivo.write(f"New load.mt{cod_id}-1 phases={phases} bus={bus}{conex} model=2 kv={kv} kw={potencia/2} pf={fp} conn={conn} status=variable vmaxpu=1.5 vminpu=0.92 daily={curvacarga}\n")
            arquivo.write(f"New load.mt{cod_id}-2 phases={phases} bus={bus}{conex} model=3 kv={kv} kw={potencia/2} pf={fp} conn={conn} status=variable vmaxpu=1.5 vminpu=0.92 daily={curvacarga}\n\n")


        end_ucmt = time.time()
        print(f"Unidades Consumidoras de Média do alimentador {feeder} Finalizadas! - Tempo: {end_ucmt - start_ucmt:.2f} s")

def generate_ucbt(feeder, dicionario_kv, n_phases_load, conex_fios, mapeamento_conn_load, output_dir=None): #modificado n_phases para n_phases_load, mapeamento_conn para mapeamento_conn_load (12/12)
    start_ucbt = time.time()
    ucbt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UCBT_tab.csv', sep=',', low_memory=False)
    trafosMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNTRMT.csv', sep=',', low_memory=False)
    trafosMT = trafosMT[trafosMT['CTMT'] == feeder]
    ucbt_filtered = ucbt[ucbt['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'ucbt_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:

        for index, linha in ucbt_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            fases = linha["FAS_CON"]
            codkv = linha["TEN_FORN"]


            phases = n_phases_load.get(fases)
            conex = conex_fios.get(fases)
            conn = mapeamento_conn_load.get(fases)
            kv = dicionario_kv.get(codkv)

            if phases == 1 and conn == "wye": #ajuste de tensão para monofásico (casos de erro de cadastro)
                trafo = linha["UNI_TR_MT"]
                trafo_linha = trafosMT[trafosMT['COD_ID'] == trafo]
                if trafo_linha.empty: continue
                if not trafo_linha.empty and "T" in trafo_linha['TIP_TRAFO'].iloc[0]:
                    kv = round((trafo_linha['TEN_LIN_SE'].iloc[0] / (3**0.5)),4)  # Dividir por raiz de 3 para obter a tensão de fase

            if phases == 1 or phases == 3: 
                if conn == "delta":
                    trafo = linha["UNI_TR_MT"]
                    trafo_linha = trafosMT[trafosMT['COD_ID'] == trafo]
                    if trafo_linha.empty: continue
                    if not trafo_linha.empty and "T" in trafo_linha['TIP_TRAFO'].iloc[0]:
                        kv = round((trafo_linha['TEN_LIN_SE'].iloc[0]),4)




            # Cálculo da potência média diária
            potencia = sum(linha[f"ENE_{i:02}"] for i in range(1, 13)) / (365 * 24)
            if potencia == 0: continue

            
            # Demais variáveis
            curvacarga = linha["TIP_CC"]
            fp = 0.92

            #arquivo.write(f"New load.bt{cod_id} phases={phases} bus={bus}{conex} kv={kv} kw={potencia} pf={fp} conn={conn} model = 8 ZIPV = [0.5 0 0.5 0 0 1 0.9] daily={curvacarga}\n")

            arquivo.write(f"New load.bt{cod_id}-1 phases={phases} bus={bus}{conex} model=2 kv={kv} kw={potencia/2} pf={fp} conn={conn} status=variable vmaxpu=1.5 vminpu=0.92 daily={curvacarga}\n")
            arquivo.write(f"New load.bt{cod_id}-2 phases={phases} bus={bus}{conex} model=3 kv={kv} kw={potencia/2} pf={fp} conn={conn} status=variable vmaxpu=1.5 vminpu=0.92 daily={curvacarga}\n")

        end_ucbt = time.time()
        print(f"Unidades Consumidoras de Baixa do alimentador {feeder} Finalizadas! - Tempo: {end_ucbt - start_ucbt:.2f} s")



def generate_pip(feeder, dicionario_kv, n_phases_load, conex_fios, mapeamento_conn_load, output_dir=None): #modificado n_phases para n_phases_load, mapeamento_conn para mapeamento_conn_load (12/12)
    start_pip = time.time()
    pip = pd.read_csv(rf'{script_dir}\Inputs\{pref} — PIP.csv', sep=',', low_memory=False)
    pip_filtered = pip[pip['CTMT'] == feeder]
    trafosMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNTRMT.csv', sep=',', low_memory=False)
    trafosMT = trafosMT[trafosMT['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'pip_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in pip_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            fases = linha["FAS_CON"]
            codkv = linha["TEN_FORN"]

            phases = n_phases_load.get(fases)
            conex = conex_fios.get(fases)
            conn = mapeamento_conn_load.get(fases)
            kv = dicionario_kv.get(codkv)

            if phases == 1 and conn == "wye":
                trafo = linha["UNI_TR_MT"]
                trafo_linha = trafosMT[trafosMT['COD_ID'] == trafo]
                if trafo_linha.empty: continue
                if not trafo_linha.empty and "T" in trafo_linha['TIP_TRAFO'].iloc[0]:
                    kv = round((trafo_linha['TEN_LIN_SE'].iloc[0] / (3**0.5)),4)  # Dividir por raiz de 3 para obter a tensão de fase

            # Cálculo da potência média diária
            potencia = sum(linha[f"ENE_{i:02}"] for i in range(1, 13)) / (365 * 24)
            if potencia == 0:
                continue

            curvacarga = linha["TIP_CC"]
            fp = 0.92

            #arquivo.write(f"New load.pip{cod_id} phases={phases} bus={bus}{conex} kv={kv} kw={potencia} pf={fp} conn={conn} model = 8 ZIPV = [0.5 0 0.5 0 0 1 0.9] daily={curvacarga}\n")

            arquivo.write(f"New load.pip{cod_id}-1 phases={phases} bus={bus}{conex} model=2 kv={kv} kw={potencia/2} pf={fp} conn={conn} status=variable vmaxpu=1.5 vminpu=0.92 daily={curvacarga}\n")
            arquivo.write(f"New load.pip{cod_id}-2 phases={phases} bus={bus}{conex} model=3 kv={kv} kw={potencia/2} pf={fp} conn={conn} status=variable vmaxpu=1.5 vminpu=0.92 daily={curvacarga}\n\n")

        end_pip = time.time()
        print(f"Ponto de Iluminação Pública do alimentador {feeder} Finalizadas! - Tempo: {end_pip - start_pip:.2f} s")

def generate_ssdunsemt(feeder, dicionario_tip_unid, conex_fios, n_phases, output_dir=None): #modificcado quant_fios para n_phases (12/12)
    start_ssdunsemt = time.time()
    ssdUNSEMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNSEMT.csv', sep=',', low_memory=False)
    ssdUNSEBT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNSEBT.csv', sep=',', low_memory=False)

    ssdUNSEMT_filtered = ssdUNSEMT[ssdUNSEMT['CTMT'] == feeder]
    ssdUNSEBT_filtered = ssdUNSEBT[ssdUNSEBT['CTMT'] == feeder]
    if ssdUNSEMT_filtered.empty and ssdUNSEBT_filtered.empty: return

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'unseMTBT_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in ssdUNSEMT_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            chave = linha["P_N_OPE"]
            if chave == 'A': chc = 'F'
            else: chc = 'T'

            length = 1 / 1000  # Valor fixo conforme lógica especificada
            r1 = 0.001
            lig = linha["FAS_CON"]

            conex = conex_fios.get(lig)
            phases = n_phases.get(lig)


            tip_unid = linha["TIP_UNID"]
            tipo_unidade = dicionario_tip_unid.get(tip_unid, "")

            if not str(bus1).startswith("SEGM") and tip_unid != 33 and tip_unid !=34: #condição para não escrever as linhas de seccionamento da subestação
                arquivo.write(f"New line.SEC{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km r1={r1} r0={r1} x1=0 x0=0 c1=0 c0=0 switch={chc} !unid={tip_unid}={tipo_unidade}\n\n")
            
            if tip_unid==33 or tip_unid==34:
                arquivo.write(f"!New line.SEC{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km r1={r1} r0={r1} x1=0 x0=0 c1=0 c0=0 switch={chc} !unid={tip_unid}={tipo_unidade}\n")

        for index, linha in ssdUNSEBT_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            chave = linha["P_N_OPE"]
            if chave == 'A': chc = 'F'
            else: chc = 'T'

            length = 1 / 1000
            r1 = 0.001
            lig = linha["FAS_CON"]

            conex = conex_fios.get(lig)
            phases = n_phases.get(lig)

            tip_unid = linha["TIP_UNID"]
            tipo_unidade = dicionario_tip_unid.get(tip_unid, "")

            arquivo.write(f"New line.SEC{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km r1={r1} r0={r1} x1=0 x0=0 c1=0 c0=0 switch={chc} !unid={tip_unid}={tipo_unidade}\n\n")
        
        end_ssdunsemt = time.time()
        print(f"SSDUNSEMT do alimentador {feeder} Finalizada! - Tempo: {end_ssdunsemt - start_ssdunsemt:.2f} s")
    
    return 1

def generate_ramlig(feeder, quant_fios, conex_fios, output_dir=None):
    start_ramlig = time.time()
    ramlig = pd.read_csv(rf'{script_dir}\Inputs\{pref} — RAMLIG.csv', sep=',', low_memory=False)
    ramlig = ramlig[ramlig['CTMT'] == feeder]
    trafos_MT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNTRMT.csv', sep=',', low_memory=False)
    trafos_MT = trafos_MT[trafos_MT['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'ramlig_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for _, linha in ramlig.iterrows():

            trafo = linha["UNI_TR_MT"]
            trafo_linha = trafos_MT[trafos_MT['COD_ID'] == trafo]
            if trafo_linha.empty: continue

            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = (linha["COMP"]) / 1000
            linecode = linha["TIP_CND"]
            fases = linha["FAS_CON"]
            
            phases = quant_fios.get(fases)
            conex = conex_fios.get(fases)
            
            arquivo.write(f"New line.ram{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode}_{phases}\n")
    
    end_ramlig = time.time()

    print(f"Ramal de Ligação do alimentador {feeder} Finalizado! - Tempo: {end_ramlig - start_ramlig:.2f} s")

def generate_gds(feeder, dicionario_kv, n_phases, n_phases_load, conex_fios, mapeamento_conn_load, output_dir=None): #modificado dicionario conex_fios_prim para conex_fios do UGMT, adicionado n_phases_load para ugbt, mapeamento_conn para mapeamento_conn_load (12/12)
    start_gds = time.time()
    ugmt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UGMT_tab.csv', sep=',', low_memory=False)
    ugbt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UGBT_tab.csv', sep=',', low_memory=False)
    ugmt_filtered = ugmt[ugmt['CTMT'] == feeder]
    ugbt_filtered = ugbt[ugbt['CTMT'] == feeder]

    trafosMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNTRMT.csv', sep=',', low_memory=False)
    trafosMT = trafosMT[trafosMT['CTMT'] == feeder]
    if ugmt_filtered.empty and ugbt_filtered.empty: return
    
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'gds_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        arquivo.write("New Loadshape.MyIrrad npts=24 interval=1 mult=[0 0 0 0 0 0 0.03 0.18 0.44 0.7 0.9 0.98 1 0.94 0.8 0.6 0.35 0.14 0.016 0 0 0 0 0] \n")
        arquivo.write("New Tshape.MyTemp npts=24 interval=1 temp=[21.5 21 20.6 20.2 19.8 19.5 19.2 20.2 25.5 34.3 42.6 49.3 53.6 55.1 54.4 51.3 45.6 38.4 31.1 25.7 24.0 23.2 22.5 22] \n")
        arquivo.write("New XYCurve.MyPvsT npts=4 xarray=[0 25 75 100] yarray=[1.2 1.0 0.8 0.6] \n")
        arquivo.write("New XYCurve.MyEff npts=4 xarray=[0.1 0.2 0.4 1.0] yarray=[0.86 0.90 0.93 0.97] \n\n")

        for index, linha in ugmt_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            kv = dicionario_kv.get(linha["TEN_CON"], 13.8)
            potencia = linha["POT_INST"]

            #if potencia <= 1: potencia = 10 #Muitos UGMT de Uberlândia não possuem a potência instalada correta, então foi feito um tratamento para que a potência seja 10kVA
            
            fp = 1  # Fator de potência da maioria dos inversores do Brasil
            fases = linha["FAS_CON"]

            phases = n_phases.get(fases)
            conex = conex_fios.get(fases)
            conn = mapeamento_conn_load.get(fases)

            arquivo.write(f"New PVSystem.MT{cod_id} bus1={bus}{conex} phases={phases} conn={conn} kv={kv} kva={potencia} pf={fp} irrad=0.84 pmpp={potencia} temperature=25 %cutin=0.1 %cutout=0.1 effcurve=MyEff p-tcurve=MyPvsT Daily=MyIrrad TDaily=MyTemp \n\n")

        for index, linha in ugbt_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            kv = dicionario_kv.get(linha["TEN_CON"], 0.22)
            potencia = linha["POT_INST"]
            if potencia == 0: continue

            fp = 1  # Fator de potência da maioria dos inversores do Brasil
            fases = linha["FAS_CON"]

            phases = n_phases_load.get(fases)
            conex = conex_fios.get(fases)
            conn = mapeamento_conn_load.get(fases)

            if phases == 1 and conn == "wye": #ajuste de tensão para monofásico (casos de erro de cadastro)
                trafo = linha["UNI_TR_MT"]
                trafo_linha = trafosMT[trafosMT['COD_ID'] == trafo]
                if trafo_linha.empty: continue
                if not trafo_linha.empty and "T" in trafo_linha['TIP_TRAFO'].iloc[0]:
                    kv = round((trafo_linha['TEN_LIN_SE'].iloc[0] / (3**0.5)),4)  # Dividir por raiz de 3 para obter a tensão de fase

            if phases == 1 or phases == 3: 
                if conn == "delta":
                    trafo = linha["UNI_TR_MT"]
                    trafo_linha = trafosMT[trafosMT['COD_ID'] == trafo]
                    if trafo_linha.empty: continue
                    if not trafo_linha.empty and "T" in trafo_linha['TIP_TRAFO'].iloc[0]:
                        kv = round((trafo_linha['TEN_LIN_SE'].iloc[0]),4)

            arquivo.write(f"New PVSystem.BT{cod_id} bus1={bus}{conex} phases={phases} conn={conn} kv={kv} kva={potencia} pf={fp} irrad=0.84 pmpp={potencia} temperature=25 %cutin=0.1 %cutout=0.1 effcurve=MyEff p-tcurve=MyPvsT Daily=MyIrrad TDaily=MyTemp \n")

        end_gds = time.time()
        print(f"GDs de baixa e média do alimentador {feeder} Finalizadas! - Tempo:{end_gds - start_gds:.2f} s")
    return 1

def generate_coordenadas(feeder, output_dir=None):
    start_coord = time.time()
    coord = pd.read_csv(rf'{script_dir}\Inputs\{pref} — Coordenadas.csv', sep=',', low_memory=False)
    coord_filtered = coord[coord['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'coord_{feeder}.dss') 
    
    unique_coords = set()

    for index, row in coord_filtered.iterrows():
        # Extrai coordenadas PAC1 e adiciona ao conjunto
        pac1 = row['PAC1']
        pac1_x, pac1_y = row['Coord1'].strip("()").split(", ")
        unique_coords.add((pac1, pac1_x, pac1_y))
        
        # Extrai coordenadas PAC2 e adiciona ao conjunto
        pac2 = row['PAC2']
        pac2_x, pac2_y = row['Coord2'].strip("()").split(", ")
        unique_coords.add((pac2, pac2_x, pac2_y))

    with open(output_file_path, 'w') as file:
        # Itera sobre o conjunto de coordenadas únicas e escreve no arquivo
        for pac, x, y in unique_coords:
            file.write(f"{pac} {x} {y}\n")

        end_coord = time.time()
        print(f"Coordenadas Finalizadas! - Tempo:{end_coord - start_coord:.2f} s")

def generate_capacitores(feeder, dicionario_capacitores, n_fases, conex_fios, output_dir=None):
    start_cap = time.time()
    cap = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNCRMT.csv', sep=',', low_memory=False)
    cap_filtered = cap[cap['CTMT'] == feeder]
    if cap_filtered.empty: return

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'capacitores_{feeder}.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in cap_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["COD_ID"]
            lig = linha["FAS_CON"]
            fases = n_fases.get(lig)
            conex = conex_fios.get(lig)
            pac1 = linha["PAC_1"]
            kvar = dicionario_capacitores.get(linha["POT_NOM"], 100)

            arquivo.write(f"new Capacitor.cap{cod_id} phases={fases} bus1={pac1}{conex} bus2={pac1}.4.4.4 kvar={kvar}\n")

        end_cap = time.time()
        print(f"Capacitores do alimentador {feeder} Finalizados! - Tempo:{end_cap - start_cap:.2f} s")
    
    return 1


def generate_unremt(feeder, conex_fios, n_phases_trafo, dicionario_kva, tp, mapeamento_conn, output_dir=None):
    start_unremt = time.time()

    # Ler as planilhas de entrada
    unremt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNREMT.csv', sep=',', low_memory=False)
    uqre = pd.read_csv(rf'{script_dir}\Inputs\{pref} — EQRE.csv', sep=',', low_memory=False)

    # Filtrar os dados pelo alimentador especificado
    unremt_filtered = unremt[unremt['CTMT'] == feeder]
    if unremt_filtered.empty: return

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'unremt_{feeder}.dss') 

    with open(output_file_path, 'w') as arquivo:
        for index, linha in unremt_filtered.iterrows():
            sit_ativ = linha["SIT_ATIV"] 
            if sit_ativ == "DS": continue
            cod_id = linha["COD_ID"]
            pac1 = linha["PAC_1"]
            pac2 = linha["PAC_2"]


            # Filtrar a planilha UQRE para obter os dados do transformador correspondente ao cod_id
            uqre_filtered = uqre[uqre['UN_RE'] == cod_id]
            if uqre_filtered.empty:
                print(f"Aviso: Transformador {cod_id} não encontrado na planilha UQRE.")
                continue
            
            num_linhas = uqre_filtered.shape[0]

            if num_linhas == 1:
                pot = dicionario_kva.get(uqre_filtered.iloc[0]['POT_NOM'])
                tape = uqre_filtered.iloc[0]['TEN_REG']
                lig = uqre_filtered.iloc[0]['LIG_FAS_P']
                conex = conex_fios.get(lig)
                conn = mapeamento_conn.get(lig)
                fases = n_phases_trafo.get(lig)
                rel_tp = tp.get(uqre_filtered.iloc[0]['REL_TP'], 120)
                per_ferro = uqre_filtered.iloc[0]['PER_FER']
                noloadloss = (per_ferro / (pot*1000)) *  100
                per_totais = uqre_filtered.iloc[0]['PER_TOT']
                loadloss = ((per_totais-per_ferro) / (pot*1000)) * 100
                r = uqre_filtered.iloc[0]['R']
                xhl = uqre_filtered.iloc[0]['XHL']
                cod_id = uqre_filtered.iloc[0]['COD_ID']
                kvs = 13.8
                if conn == 'wye': kvs = 13.8 / (3 ** 0.5)

                arquivo.write(f'New "Transformer.TFreg{cod_id}" phases={fases} windings=2 buses=["{pac1}{conex}" "{pac2}{conex}"] conns=[{conn} {conn}] kvs=[{kvs} {kvs}] kvas=[{pot} {pot}] xhl={xhl} r={r} %loadloss={loadloss} %noloadloss={noloadloss}\n')
                arquivo.write(f'New "Regcontrol.reg{cod_id}" transformer="TFreg{cod_id}" winding=2 vreg={rel_tp} band=2 ptratio={(tape / rel_tp) * (kvs * 1000)}\n')
                arquivo.write(f'New Reactor.TFreg{cod_id}-1 phases=1 bus1={pac1}.4 R=15 X=0 basefreq=60\n')
                arquivo.write(f'New Reactor.TFreg{cod_id}-2 phases=1 bus1={pac2}.4 R=15 X=0 basefreq=60\n\n')

            
            if num_linhas ==2:
                pot = dicionario_kva.get(uqre_filtered.iloc[0]['POT_NOM'])
                tape = uqre_filtered.iloc[0]['TEN_REG']
                lig1 = uqre_filtered.iloc[0]['LIG_FAS_P']
                conex1 = conex_fios.get(lig1)
                conn1 = mapeamento_conn.get(lig1)
                fases1 = n_phases_trafo.get(lig1)
                cod_id1 = uqre_filtered.iloc[0]['COD_ID']

                lig2 = uqre_filtered.iloc[1]['LIG_FAS_P']
                conex2 = conex_fios.get(lig2)
                conn2 = mapeamento_conn.get(lig2)
                fases2 = n_phases_trafo.get(lig2)
                cod_id2 = uqre_filtered.iloc[1]['COD_ID']

                rel_tp = tp.get(uqre_filtered.iloc[0]['REL_TP'], 120)
                per_ferro = uqre_filtered.iloc[0]['PER_FER']
                noloadloss = (per_ferro / (pot*1000)) *  100
                per_vazio = uqre_filtered.iloc[0]['PER_TOT']
                loadloss = (per_vazio / (pot*1000)) * 100
                r = uqre_filtered.iloc[0]['R']
                xhl = uqre_filtered.iloc[0]['XHL']
                kvs = 13.8
                if conn1 == 'wye': kvs = 13.8 / (3 ** 0.5)

                arquivo.write(f'New "Transformer.TFreg{cod_id1}" phases={fases1} windings=2 buses=["{pac1}{conex1}" "{pac2}{conex1}"] conns=[{conn1} {conn1}] kvs=[{kvs} {kvs}] kvas=[{pot} {pot}] xhl={xhl} r={r} %loadloss={loadloss} %noloadloss={noloadloss}\n')
                arquivo.write(f'New "Regcontrol.reg{cod_id1}" transformer="TFreg{cod_id1}" winding=2 vreg={rel_tp} band=2 ptratio={(tape / rel_tp) * (kvs * 1000)}\n')
                arquivo.write(f'New Reactor.TFreg{cod_id1}-1 phases=1 bus1={pac1}.4 R=15 X=0 basefreq=60\n')
                arquivo.write(f'New Reactor.TFreg{cod_id1}-2 phases=1 bus1={pac2}.4 R=15 X=0 basefreq=60\n\n')

                arquivo.write(f'New "Transformer.TFreg{cod_id2}" phases={fases2} windings=2 buses=["{pac1}{conex2}" "{pac2}{conex2}"] conns=[{conn2} {conn2}] kvs=[{kvs} {kvs}] kvas=[{pot} {pot}] xhl={xhl} r={r} %loadloss={loadloss} %noloadloss={noloadloss}\n')
                arquivo.write(f'New "Regcontrol.reg{cod_id2}" transformer="TFreg{cod_id2}" winding=2 vreg={rel_tp} band=2 ptratio={(tape / rel_tp) * (kvs * 1000)}\n')
                arquivo.write(f'New Reactor.TFreg{cod_id2}-1 phases=1 bus1={pac1}.4 R=15 X=0 basefreq=60\n')
                arquivo.write(f'New Reactor.TFreg{cod_id2}-2 phases=1 bus1={pac2}.4 R=15 X=0 basefreq=60\n\n')

            if num_linhas == 3:
                pot = dicionario_kva.get(uqre_filtered.iloc[0]['POT_NOM'])
                tape = uqre_filtered.iloc[0]['TEN_REG']
                lig1 = uqre_filtered.iloc[0]['LIG_FAS_P']
                conex1 = conex_fios.get(lig1)
                conn1 = mapeamento_conn.get(lig1)
                fases1 = n_phases_trafo.get(lig1)
                cod_id1 = uqre_filtered.iloc[0]['COD_ID']

                lig2 = uqre_filtered.iloc[1]['LIG_FAS_P']
                conex2 = conex_fios.get(lig2)
                conn2 = mapeamento_conn.get(lig2)
                fases2 = n_phases_trafo.get(lig2)
                cod_id2 = uqre_filtered.iloc[1]['COD_ID']

                lig3 = uqre_filtered.iloc[2]['LIG_FAS_P']
                conex3 = conex_fios.get(lig3)
                conn3 = mapeamento_conn.get(lig3)
                fases3 = n_phases_trafo.get(lig3)
                cod_id3 = uqre_filtered.iloc[2]['COD_ID']

                rel_tp = tp.get(uqre_filtered.iloc[0]['REL_TP'], 120)
                per_ferro = uqre_filtered.iloc[0]['PER_FER']
                noloadloss = (per_ferro / (pot*1000)) *  100
                per_vazio = uqre_filtered.iloc[0]['PER_TOT']
                loadloss = (per_vazio / (pot*1000)) * 100
                r = uqre_filtered.iloc[0]['R']
                xhl = uqre_filtered.iloc[0]['XHL']
                kvs = 13.8
                if conn1 == 'wye': kvs = 13.8 / (3 ** 0.5)

                arquivo.write(f'New "Transformer.TFreg{cod_id1}" phases={fases1} windings=2 buses=["{pac1}{conex1}" "{pac2}{conex1}"] conns=[{conn1} {conn1}] kvs=[{kvs} {kvs}] kvas=[{pot} {pot}] xhl={xhl} r={r} %loadloss={loadloss} %noloadloss={noloadloss}\n')
                arquivo.write(f'New "Regcontrol.reg{cod_id1}" transformer="TFreg{cod_id1}" winding=2 vreg={rel_tp} band=2 ptratio={(tape / rel_tp) * (kvs * 1000)}\n')
                arquivo.write(f'New Reactor.TFreg{cod_id1}-1 phases=1 bus1={pac1}.4 R=15 X=0 basefreq=60\n')
                arquivo.write(f'New Reactor.TFreg{cod_id1}-2 phases=1 bus1={pac2}.4 R=15 X=0 basefreq=60\n\n')

                arquivo.write(f'New "Transformer.TFreg{cod_id2}" phases={fases2} windings=2 buses=["{pac1}{conex2}" "{pac2}{conex2}"] conns=[{conn2} {conn2}] kvs=[{kvs} {kvs}] kvas=[{pot} {pot}] xhl={xhl} r={r} %loadloss={loadloss} %noloadloss={noloadloss}\n')
                arquivo.write(f'New "Regcontrol.reg{cod_id2}" transformer="TFreg{cod_id2}" winding=2 vreg={rel_tp} band=2 ptratio={(tape / rel_tp) * (kvs * 1000)}\n')
                arquivo.write(f'New Reactor.TFreg{cod_id2}-1 phases=1 bus1={pac1}.4 R=15 X=0 basefreq=60\n')
                arquivo.write(f'New Reactor.TFreg{cod_id2}-2 phases=1 bus1={pac2}.4 R=15 X=0 basefreq=60\n\n')

                arquivo.write(f'New "Transformer.TFreg{cod_id3}" phases={fases3} windings=2 buses=["{pac1}{conex3}" "{pac2}{conex3}"] conns=[{conn3} {conn3}] kvs=[{kvs} {kvs}] kvas=[{pot} {pot}] xhl={xhl} r={r} %loadloss={loadloss} %noloadloss={noloadloss}\n')
                arquivo.write(f'New "Regcontrol.reg{cod_id3}" transformer="TFreg{cod_id3}" winding=2 vreg={rel_tp} band=2 ptratio={(tape / rel_tp) * (kvs * 1000)}\n')
                arquivo.write(f'New Reactor.TFreg{cod_id3}-1 phases=1 bus1={pac1}.4 R=15 X=0 basefreq=60\n')
                arquivo.write(f'New Reactor.TFreg{cod_id3}-2 phases=1 bus1={pac2}.4 R=15 X=0 basefreq=60\n\n')

    end_unremt = time.time()
    print(f"UNREMT do alimentador {feeder} Finalizado! - Tempo: {end_unremt - start_unremt:.2f} s")
    
    return 1

def generate_energymeters(feeder, output_dir=None):

    tempo_meters = time.time()
    ssdUNSEMT = pd.read_csv(rf'{script_dir}\Inputs\{pref} — UNSEMT.csv', sep=',' , low_memory=False)
    ssdUNSEMT_filtered = ssdUNSEMT[ssdUNSEMT['CTMT'] == feeder]

    if ssdUNSEMT_filtered.empty: return

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'energyMeters{feeder}.dss')

    num = 1

    with open(output_file_path, 'w') as arquivo:

        arquivo.write(f"New EnergyMeter.EM1     Element=line.sub{feeder} Terminal=1  Action=Save localonly=no\n")
        arquivo.write(f"New monitor.MON1 _current element=line.sub{feeder} terminal=2 mode=0\n\n")
        for index, linha in ssdUNSEMT_filtered.iterrows():
            cod_id = linha["COD_ID"]
            tip_unid = linha["TIP_UNID"]
            ope = linha["P_N_OPE"]
            untrat = linha["UNI_TR_AT"]
            aux=0
            if untrat != 0 and untrat != None: aux=1 #condição para não escrever os medidores dos religadores das SEs (já escrita no Master.dss)
            if tip_unid == 32 and aux==1 and ope == 'F':
                num += 1
                arquivo.write(f"New EnergyMeter.EM{num}     Element=line.SEC{cod_id} Terminal=1  Action=Save localonly=no\n")
                arquivo.write(f"New monitor.MON{num} _current element=line.SEC{cod_id} terminal=2 mode=0\n\n")
    
    tempo_meters_end = time.time()
    print(f"Medidores de Energia do alimentador {feeder} Finalizados! - Tempo: {tempo_meters_end - tempo_meters:.2f} s")


# Função que valida os alimentadores comparando as potências simuladas com as potências do BDGD
def feeders_feasibility(feeders_list):

    # Obter o diretório onde o script está localizado
    
    parent_dir = os.path.dirname(script_dir)

    # Carregar o arquivo CSV
    ctmt = pd.read_csv(rf'{script_dir}\Inputs\{pref} — CTMT.csv', sep=',')

    # Inicializa a interface do PyDSS
    dss = py_dss_interface.DSSDLL()

    # Lista para armazenar os dados de cada feeder
    data_list = []

    def montar_planilha():
        time_start = time.time()
        for feeder in feeders_list:
            # Filtra a tabela para o feeder específico
            filtered_ctmt = ctmt[ctmt['COD_ID'] == feeder]

            # Soma das colunas de energia (ENE_01 até ENE_12)
            energy_columns = [f'ENE_{str(i).zfill(2)}' for i in range(1, 13)]
            energyBDGD = filtered_ctmt[energy_columns].sum().sum()

            energymeter = [0,0,0]
            n=0
            for dia in ["DU", "SA", "DO"]:
                print(f" Processando Feeder {feeder} - Dia {dia}")

                dss.file = rf"{parent_dir}\{feeder}\Master_{feeder}_{dia}.dss" #Verificar se o caminho está correto

                dss.text(f"compile {dss.file}")
                # Resolve o circuito
                dss.solution_solve()
                # Seleciona o medidor "EM1"
                dss.meters_write_name("EM1")

                energymeter[n] = dss.meters_register_values()[0]
                n+=1

                if dia == "DU":
                    teste_conv = dss.solution_read_converged()  # Verifica se convergiu (1) ou não (0)
                    if teste_conv == 0:
                        conv = 'Não'
                        energymeteryear = 'N/A'
                    else:
                        conv = 'Sim'
            energymeteryear = energymeter[0] * 252 + energymeter[1] * 53 + energymeter[2] * 60
            if conv == 'Não':
                energymeteryear = 0
                energymeter = [0,0,0]
            # Adicionar os dados na lista
            data_list.append({
                "Feeder": feeder,
                "Converged": conv,
                "Energy Meter DU": energymeter[0],
                "Energy Meter SA": energymeter[1],
                "Energy Meter DO": energymeter[2],
                "Energy Meter Year": energymeteryear,
                "Energy BDGD": energyBDGD
            })


        # Criar o DataFrame final com todos os feeders
        df = pd.DataFrame(data_list)
        #print(df)

        # Extrair a concessionária e o ano do prefixo
        match_conc = re.match(r"([A-Za-z\-]+_[A-Za-z]+)", pref)
        concessionaria = match_conc.group(1) if match_conc else ""
        match_ano = re.search(r"_(\d{4})-", pref)
        ano = match_ano.group(1) if match_ano else ""

        # Junta para formar o novo prefixo
        nome = f"{concessionaria}_{ano}"
        

        # Salvar o DataFrame em uma planilha Excel
        filename = os.path.join(script_dir, f"{nome}.xlsx")
        df.to_excel(filename, index=False)

        for index, row in df.iterrows():
            if pd.isna(row["Energy Meter Year"]) or row["Energy Meter Year"] == 0:
                df.at[index, "Converged"] = "Não"
                df.at[index, "Energy Meter Year"] = "N/A"

        # Salvar as alterações na planilha
        df.to_excel(filename, index=False)


        time_end = time.time()
        print(f"ComparativoFeeders.xlsx criada e formatada com sucesso em {time_end-time_start}!")

    montar_planilha()


#########################################################################################################
# Função para processar cada alimentador
def process_feeder(args):
    feeder, mvasc3, mvasc1 = args

    pasta_path = str(feeder)
    os.makedirs(pasta_path, exist_ok=True)
    print(f'\n\nPasta criada: {pasta_path}')



    generate_crvcrg(output_dir=pasta_path)
    generate_linecode(output_dir=pasta_path)
    generate_ssdmt(feeder, dic.quant_fios, dic.conex_fios, output_dir=pasta_path)
    generate_trafosMT(feeder, dic.dicionario_kv, dic.conex_fios_prim, dic.conex_fios_sec, dic.conex_fios_terc, dic.mapeamento_conn, dic.n_phases_trafo, output_dir=pasta_path)
    generate_ssdBT(feeder, dic.conex_fios, dic.quant_fios, output_dir=pasta_path)
    generate_ucmt(feeder, dic.conex_fios, dic.mapeamento_conn_load, dic.dicionario_kv, dic.n_phases_load, output_dir=pasta_path)
    generate_ucbt(feeder, dic.dicionario_kv, dic.n_phases_load, dic.conex_fios, dic.mapeamento_conn_load, output_dir=pasta_path)
    generate_pip(feeder, dic.dicionario_kv, dic.n_phases_load, dic.conex_fios, dic.mapeamento_conn_load, output_dir=pasta_path)
    generate_ramlig(feeder, dic.quant_fios, dic.conex_fios, output_dir=pasta_path)
    x = generate_gds(feeder, dic.dicionario_kv, dic.n_phases, dic.n_phases_load, dic.conex_fios, dic.mapeamento_conn_load, output_dir=pasta_path)
    y = generate_capacitores(feeder, dic.dicionario_capacitores, dic.n_phases, dic.conex_fios, output_dir=pasta_path)
    generate_coordenadas(feeder, output_dir=pasta_path)
    z = generate_ssdunsemt(feeder, dic.dicionario_tip_unid, dic.conex_fios, dic.n_phases, output_dir=pasta_path)
    w = generate_unremt(feeder, dic.conex_fios, dic.n_phases_trafo, dic.dicionario_kva, dic.rel_tp, dic.mapeamento_conn, output_dir=pasta_path)
    generate_energymeters(feeder, output_dir=pasta_path)
    for dia_de_analise in ["DU", "SA", "DO"]:
        generate_master(x, y, z, w, feeder, dic.dicionario_kv, dia_de_analise, mvasc3, mvasc1, output_dir=pasta_path)
    
# Função principal que modela os alimentadores de interesse usando processamento paralelo
def feeders_modelling(feeders_list, mvasc3, mvasc1):
    # Utilizando Pool do multiprocessing para paralelizar o processo
    feeders_list = [int(f) if f.isdigit() else f for f in feeders_list] # Tenta converter cada alimentador para int; se não for puramente numérico, mantém como string
    args_list = [(feeder, mvasc3, mvasc1) for feeder in feeders_list]
    with Pool() as pool:
        pool.map(process_feeder, args_list)


