import pandas as pd
import time
import re
import os


#Função para gerar o arquivo Master.dss
def generate_master(feeder, dicionario_kv, dicionario_kva, dia_de_analise, output_dir=None):
    start_master = time.time()

    eqtrat = pd.read_csv(r'Inputs\EQTRAT.csv', sep=',')
    untrat = pd.read_csv(r'Inputs\UNTRAT.csv', sep=',')
    ctmt = pd.read_csv(r'Inputs\CTMT.csv', sep=',')
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, f'Master_{feeder}.dss')

    with open(output_file_path, 'w') as arquivo:
        # Início da medição do tempo
        
        # Encontrar o cod_untrat e pac_ini correspondentes
        linha_feeder = ctmt[ctmt['COD_ID'] == feeder].iloc[0]
    
        cod_untrat = linha_feeder['UNI_TR_AT']
        pac_ini = linha_feeder['PAC_INI']  # Ponto de acoplamento comum elétrico inicial  

        # Encontrar a linha correspondente em eqtrat
        linha_untrat = eqtrat[eqtrat['UNI_TR_AT'] == cod_untrat].iloc[0]
        
        # Obter valores
        kv1 = dicionario_kv[linha_untrat['TEN_PRI']]
        kv2 = dicionario_kv[linha_untrat['TEN_SEC']]
        pot = dicionario_kva[linha_untrat['POT_NOM']]
        loadloss = linha_untrat['PER_TOT']
        noloadloss = linha_untrat['PER_FER']
        tape = linha_feeder['TEN_OPE']
        # Escrever no arquivo
        conteudo = [
            "Clear\n\n",
            f"New circuit.{feeder} bus1=source.1.2.3 basekv={kv1} pu={tape} angle=0 phases=3 frequency=60 mvasc3=5777.8 mvasc1=5794.4\n\n",
            f"New transformer.SUB windings=2.0 %loadloss={loadloss} %noloadloss={noloadloss} sub=yes\n",
            f"~ wdg=1 bus=source.1.2.3 kv={kv1} kva={pot} conn=delta\n",
            f"~ wdg=2 bus={pac_ini}.1.2.3 kv={kv2} kva={pot} conn=delta\n\n",
            "Redirect linecode.dss\n",
            f"Redirect crvcrg_{dia_de_analise}.dss\n",
            "Redirect ssdMT.dss\n",
            "Redirect ssdUNSEMT.dss\n",
            "Redirect trafosMT.dss\n",
            "Redirect ssdBT.dss\n",
            "Redirect ramlig.dss\n",
            "Redirect ucbt.dss\n",
            "Redirect ucmt.dss\n",
            "Redirect pip.dss\n",
            "Redirect gds.dss\n",
            "Redirect capacitores.dss\n\n",
            "New EnergyMeter.EM1     Element=transformer.SUB Terminal=1  Action=Save localonly=no\n",
            "New monitor.MON1 _current element=transformer.SUB terminal=2 mode=0\n\n",
            "set tolerance = 0.01\n",
            "set Maxiter=10\n",
            "set mode = daily\n",
            "set stepsize = 1h\n",
            "set number = 24\n\n",
        ]
        
        arquivo.writelines(conteudo)
        end_master = time.time()
        print(f"Master Finalizado! - Tempo: {end_master - start_master:.2f} s")


def generate_crvcrg(output_dir=None):
    start_crvcrg = time.time()
    crvcrg = pd.read_csv(r'Inputs\CRVCRG.csv', sep=',')

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path1 = os.path.join(output_dir, 'crvcrg_SA.dss')
    output_file_path2 = os.path.join(output_dir, 'crvcrg_DO.dss')
    output_file_path3 = os.path.join(output_dir, 'crvcrg_DU.dss')
    
    with open(output_file_path1, 'w') as arquivo:        
        for index, linha in crvcrg.iterrows():
            cod_id = linha.iloc[crvcrg.columns.get_loc("COD_ID")]
            dia = linha.iloc[crvcrg.columns.get_loc("TIP_DIA")]
            if dia == "SA": # Dia Útil
                # Encontra a potência máxima
                max_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].max()
                mean_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].mean()
                # Calcula as potências normalizadas
                potencias = [
                    linha.iloc[crvcrg.columns.get_loc(f"POT_{i:02}") : crvcrg.columns.get_loc(f"POT_{i+3:02}")+1].mean() / (mean_pot) 
                    for i in range(1, 97, 4)
                ]
                # Escreve os dados no arquivo
                arquivo.write(f"New LoadShape.{cod_id} npts=24 interval=1\n")
                arquivo.write("~ mult=(" + " ".join(map(str, potencias)) + ")\n")

    with open(output_file_path2, 'w') as arquivo:
        for index, linha in crvcrg.iterrows():
            cod_id = linha.iloc[crvcrg.columns.get_loc("COD_ID")]
            dia = linha.iloc[crvcrg.columns.get_loc("TIP_DIA")]
            if dia == "DO": # Dia Útil
                # Encontra a potência máxima
                max_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].max()
                mean_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].mean()
                # Calcula as potências normalizadas
                potencias = [
                    linha.iloc[crvcrg.columns.get_loc(f"POT_{i:02}") : crvcrg.columns.get_loc(f"POT_{i+3:02}")+1].mean() / (mean_pot) 
                    for i in range(1, 97, 4)
                ]
                # Escreve os dados no arquivo
                arquivo.write(f"New LoadShape.{cod_id} npts=24 interval=1\n")
                arquivo.write("~ mult=(" + " ".join(map(str, potencias)) + ")\n")

    with open(output_file_path3, 'w') as arquivo:
        for index, linha in crvcrg.iterrows():
            cod_id = linha.iloc[crvcrg.columns.get_loc("COD_ID")]
            dia = linha.iloc[crvcrg.columns.get_loc("TIP_DIA")]
            if dia == "DU": # Dia Útil
                # Encontra a potência máxima
                max_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].max()
                mean_pot = linha.iloc[crvcrg.columns.get_loc("POT_01"):crvcrg.columns.get_loc("POT_96")+1].mean()
                # Calcula as potências normalizadas
                potencias = [
                    linha.iloc[crvcrg.columns.get_loc(f"POT_{i:02}") : crvcrg.columns.get_loc(f"POT_{i+3:02}")+1].mean() / (mean_pot) 
                    for i in range(1, 97, 4)
                ]
                # Escreve os dados no arquivo
                arquivo.write(f"New LoadShape.{cod_id} npts=24 interval=1\n")
                arquivo.write("~ mult=(" + " ".join(map(str, potencias)) + ")\n")

        end_crvcrg = time.time()
        print(f"Curvas de Cargas Finalizadas! - Tempo: {end_crvcrg - start_crvcrg:.2f} s")


def generate_linecode(output_dir=None):
    start_linecode = time.time()
    segcon = pd.read_csv(r'Inputs\SEGCON.csv', sep=',') 
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'linecode.dss')   

    with open(output_file_path, 'w') as arquivo:

        linecodes_unsemt = [
            "New linecode.CAB108_3_1 nphases=1 basefreq=60.0 units=km\n",
            "~ r1=0.2006 x1=0.7049 c1=0.0 c0=0.0\n",
            "!~ cnom=576.0 cmax=748.8\n\n",
            "New linecode.CAB108_3_2 nphases=2 basefreq=60.0 units=km\n",
            "~ r1=0.2006 x1=0.7049 c1=0.0 c0=0.0\n",
            "!~ cnom=576.0 cmax=748.8\n\n",
            "New linecode.CAB108_3_3 nphases=3 basefreq=60.0 units=km\n",
            "~ r1=0.2006 x1=0.7049 c1=0.0 c0=0.0\n",
            "!~ cnom=576.0 cmax=748.8\n\n",
        ]
        arquivo.writelines(linecodes_unsemt) #garantir os linecodes configurados para o unsemt

        for index, linha in segcon.iterrows():
            cod_id = linha["COD_ID"]
            r1 = linha["R1"]
            x1 = linha["X1"]
            cnom = linha["CNOM"]  # Dados apenas para visualização
            cmax = linha["CMAX"]  # Dados apenas para visualização
            phases = 0

            # Verifica se a linha é monofásica, bifásica ou trifásica a partir se tiver material ou não em cada fase
            if linha["MAT_FAS_1"] != 0:
                phases += 1
            if linha["MAT_FAS_2"] != 0:
                phases += 1
            if linha["MAT_FAS_3"] != 0:
                phases += 1
            if phases == 0:
                phases = 1

            arquivo.write(f"New linecode.{cod_id} nphases={phases} basefreq=60.0 units=km\n")
            arquivo.write(f"~ r1={r1} x1={x1} c1=0.0 c0=0.0\n")
            arquivo.write(f"!~ cnom={cnom} cmax={cmax}\n\n") # Dados apenas para visualização
        
        end_linecode = time.time()
        print(f"Linecodes Finalizados! - Tempo: {end_linecode - start_linecode:.2f} s")

def generate_ssdmt(feeder, output_dir=None):
    start_ssdmt = time.time()
    ssdMT = pd.read_csv(r'Inputs\SSDMT.csv', sep=',')
    # Filtrar apenas as linhas que pertencem ao alimentador escolhido
    ssdMT_filtered = ssdMT[ssdMT['CTMT'] == feeder]
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'ssdMT.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in ssdMT_filtered.iterrows():
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = linha["COMP"] / 1000  # Conversão metros (BDGD) para km (OpenDSS)
            linecode = linha["TIP_CND"]
            fases = linha["FAS_CON"]
            if fases == "A": nfases = 1; conex = ".1"
            elif fases == "B": nfases = 1; conex = ".2"
            elif fases == "C": nfases = 1; conex = ".3"
            else: nfases = 3; conex = ".1.2.3"
            

            arquivo.write(f"New line.mt{cod_id} phases={nfases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode}\n")
        
        end_ssdmt = time.time()
        print(f"Linhas de Média Finalizadas! - Tempo: {end_ssdmt - start_ssdmt:.2f} s")

def generate_trafosMT(feeder, dicionario_kv, mapeamento_conex, lig_trafo, output_dir=None):
    start_trafos = time.time()
    trafosMT = pd.read_csv(r'Inputs\UNTRMT.csv', sep=',')
    eqtrmt = pd.read_csv(r'Inputs\EQTRMT.csv', sep=',')

    trafosMT = trafosMT[trafosMT['CTMT'] == feeder] 
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'trafosMT.dss') 

    with open(output_file_path, 'w') as arquivo:
        for index, linha in trafosMT.iterrows():
            cod_id = str(linha["COD_ID"])  # Convertendo para string para garantir compatibilidade
            eqtrmt_linha = eqtrmt[eqtrmt['UNI_TR_MT'].astype(str) == cod_id]  # Convertendo também para string

            #if not eqtrmt_linha.empty:
            xhl = eqtrmt_linha['XHL'].iloc[0]
            r = eqtrmt_linha['R'].iloc[0]
            cod_ten_pri = eqtrmt_linha['TEN_PRI'].iloc[0]
            cod_ten_sec = eqtrmt_linha['TEN_SEC'].iloc[0]
            cod_ten_ter = eqtrmt_linha['TEN_TER'].iloc[0]
            cod_lig_pri = eqtrmt_linha['LIG_FAS_P'].iloc[0]
            cod_lig_sec = eqtrmt_linha['LIG_FAS_S'].iloc[0]
            cod_lig_ter = eqtrmt_linha['LIG_FAS_T'].iloc[0]

            lig = eqtrmt_linha['LIG'].iloc[0]
            conn1, conn2 = lig_trafo.get(lig, ("delta", "wye"))

            
            loadloss = 100 * (linha["PER_TOT"]) / (1000 * linha["POT_NOM"])
            noloadloss = 100 * (linha["PER_FER"]) / (1000 * linha["POT_NOM"])

            kva = linha["POT_NOM"]

            windings = 2 
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            bus3 = linha["PAC_3"]

            #if bus3.isdigit() or bus3 == "0": #comentei essa linha para que o código não dê erro, mas não tenho certeza se está correto
                #windings = 3    

            if windings==2:
                arquivo.write(f"New transformer.{cod_id} xhl={xhl} %r={r} windings={windings} %loadloss={loadloss} %noloadloss={noloadloss}\n")
                arquivo.write(f"~ wdg=1 bus={bus1}{mapeamento_conex.get(cod_lig_pri)} kv={dicionario_kv.get(cod_ten_pri, 0)} kva={kva} conn={conn1}\n")
                arquivo.write(f"~ wdg=2 bus={bus2}{mapeamento_conex.get(cod_lig_sec)} kv={dicionario_kv.get(cod_ten_sec, 0)} kva={kva} conn={conn2}\n\n")

            if windings==3:
                arquivo.write(f"New transformer.{cod_id} xhl={xhl} %r={r} windings={windings} %loadloss={loadloss} %noloadloss={noloadloss}\n")
                arquivo.write(f"~ wdg=1 bus={bus1}{mapeamento_conex.get(cod_lig_pri)} kv={dicionario_kv.get(cod_ten_pri, 0)} kva={kva} conn={conn1}\n")
                arquivo.write(f"~ wdg=2 bus={bus2}{mapeamento_conex.get(cod_lig_sec)} kv={dicionario_kv.get(cod_ten_sec, 0)} kva={kva} conn={conn2}\n")
                arquivo.write(f"~ wdg=3 bus={bus3}{mapeamento_conex.get(cod_lig_ter)} kv={dicionario_kv.get(cod_ten_ter, 0)} kva={kva} conn={conn2}\n\n")

            
        end_trafos = time.time()

        print(f"Tranformadores de Média Finalizados! - Tempo:{end_trafos - start_trafos:.2f} s")

def generate_ssdBT(feeder, mapeamento_conex, mapeamento_phases, output_dir=None):
    start_ssdbt = time.time()
    ssdBT = pd.read_csv(r'Inputs\SSDBT.csv', sep=',')
    ssdBT_filtered = ssdBT[ssdBT['CTMT'] == feeder]
    
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'ssdBT.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in ssdBT_filtered.iterrows():
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = linha["COMP"] / 1000.0  # Convertendo metros para km
            linecode = linha["TIP_CND"]
            fases = linha["FAS_CON"]

            conex = mapeamento_conex.get(fases, ".1")
            phases = mapeamento_phases.get(fases, 1)

            arquivo.write(f"New line.bt{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode}\n")
        
        end_ssdbt = time.time()
        print(f"Linhas de Baixa Finalizadas! - Tempo: {end_ssdbt - start_ssdbt:.2f} s")

def generate_ucmt(feeder, mapeamento_conex, dicionario_kv, output_dir=None):
    start_ucmt = time.time()
    ucmt = pd.read_csv(r'Inputs\UCMT.csv', sep=',')
    ucmt_filtered = ucmt[ucmt['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'ucmt.dss') 
    
    with open(output_file_path, 'w') as arquivo:

        for index, linha in ucmt_filtered.iterrows():
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            potencia = sum(linha[f"ENE_{i:02}"] for i in range(1, 13)) / (365 * 24)
            curvacarga = linha["TIP_CC"]


            lig = linha["FAS_CON"]

            if lig == "ABN" or lig == "BCN" or lig == "CAN": 
                phases = 2
                conn = 'wye'
            if lig == "ABCN": 
                phases = 3
                conn = 'wye' 
            else: 
                phases = 3
                conn = 'delta'

            model = 1
            kv = dicionario_kv.get(linha["TEN_FORN"], 13.8)
            fp = 0.92

            arquivo.write(f"New load.mt{cod_id} phases={phases} bus={bus}{mapeamento_conex.get(lig)} model={model} kv={kv} kw={potencia} pf={fp} conn={conn} daily={curvacarga}\n")

        end_ucmt = time.time()
        print(f"Unidades Consumidoras de Média Finalizadas! - Tempo: {end_ucmt - start_ucmt:.2f} s")

def generate_ucbt(feeder, dicionario_kv, mapeamento_phases, mapeamento_conex, mapeamento_conn, output_dir=None):
    start_ucbt = time.time()
    ucbt = pd.read_csv(r'Inputs\UCBT.csv', sep=',')
    ucbt_filtered = ucbt[ucbt['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'ucbt.dss') 
    
    with open(output_file_path, 'w') as arquivo:

        for index, linha in ucbt_filtered.iterrows():
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            fases = linha["FAS_CON"]

            phases = mapeamento_phases.get(fases, 1)
            conex = mapeamento_conex.get(fases, ".1")
            conn = mapeamento_conn.get(fases, "wye")

            # Mapeamento de codkv para kv
            codkv = linha["TEN_FORN"]
            kv = dicionario_kv.get(codkv, 0.22)

            # Cálculo da potência média diária
            potencia = sum(linha[f"ENE_{i:02}"] for i in range(1, 13)) / (365 * 24)
            
            # Demais variáveis
            curvacarga = linha["TIP_CC"]
            fp = 0.92
            model = 1

            arquivo.write(f"New load.bt{cod_id} phases={phases} bus={bus}{conex} model={model} kv={kv} kw={potencia} pf={fp} conn={conn} daily={curvacarga}\n")

        end_ucbt = time.time()
        print(f"Unidades Consumidoras de Baixa Finalizadas! - Tempo: {end_ucbt - start_ucbt:.2f} s")


def generate_pip(feeder, dicionario_kv, mapeamento_phases, mapeamento_conex, mapeamento_conn, output_dir=None):
    start_pip = time.time()
    pip = pd.read_csv(r'Inputs\PIP.csv', sep=',')
    pip_filtered = pip[pip['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'pip.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in pip_filtered.iterrows():
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            fases = linha["FAS_CON"]

            phases = mapeamento_phases.get(fases, 1)
            conex = mapeamento_conex.get(fases, ".1")
            conn = mapeamento_conn.get(fases, "wye")


            codkv = linha["TEN_FORN"]
            kv = dicionario_kv.get(codkv, 0.22)

            # Cálculo da potência média diária
            potencia = sum(linha[f"ENE_{i:02}"] for i in range(1, 13)) / (365 * 24)
            
            curvacarga = linha["TIP_CC"]
            fp = 0.92
            model = 1

            arquivo.write(f"New load.pip{cod_id} phases={phases} bus={bus}{conex} model={model} kv={kv} kw={potencia} pf={fp} conn={conn} daily={curvacarga}\n")

        end_pip = time.time()
        print(f"Ponto de Iluminação Pública Finalizadas! - Tempo: {end_pip - start_pip:.2f} s")

def generate_ssdunsemt(feeder, dicionario_tip_unid, output_dir=None):
    start_ssdunsemt = time.time()
    ssdUNSEMT = pd.read_csv(r'Inputs\UNSEMT.csv', sep=',')
    ssdUNSEMT_filtered = ssdUNSEMT[ssdUNSEMT['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'ssdUNSEMT.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in ssdUNSEMT_filtered.iterrows():
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = 1 / 1000  # Valor fixo conforme lógica especificada

            lig = linha["FAS_CON"]

            if lig == "A": conex = ".1"; phases = 1; linecode = 'CAB108_3_1'
            if lig == "B": conex = ".2"; phases = 1; linecode = 'CAB108_3_1'
            if lig == "C": conex = ".3"; phases = 1; linecode = 'CAB108_3_1'
            elif lig == "ABC": conex = ".1.2.3"; phases = 3; linecode = 'CAB108_3_3'


            tip_unid = linha["TIP_UNID"]
            tipo_unidade = dicionario_tip_unid.get(tip_unid, "")

            #arquivo.write(f"!Tipo_de_unidade={tip_unid}{tipo_unidade}\n")
            if not bus1.startswith("SEGM") and tip_unid != 33 and tip_unid !=34: #condição para não escrever as linhas de seccionamento da subestação
                arquivo.write(f"New line.SEC{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode} !unid={tip_unid}={tipo_unidade}\n")
            
            if tip_unid==33 or tip_unid==34:
                arquivo.write(f"!New line.SEC{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode} !unid={tip_unid}={tipo_unidade}\n")


        end_ssdunsemt = time.time()
        print(f"SSDUNSEMT Finalizada! - Tempo: {end_ssdunsemt - start_ssdunsemt:.2f} s")

def generate_ramlig(feeder, mapeamento_phases, mapeamento_conex, output_dir=None):
    start_ramlig = time.time()
    ramlig = pd.read_csv(r'Inputs\RAMLIG.csv', sep=',')
    ramlig = ramlig[ramlig['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'ramlig.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for _, linha in ramlig.iterrows():
            cod_id = linha["COD_ID"]
            bus1 = linha["PAC_1"]
            bus2 = linha["PAC_2"]
            length = (linha["COMP"]) / 1000
            linecode = linha["TIP_CND"]
            fases = linha["FAS_CON"]
            
            phases = mapeamento_phases.get(fases, 1)
            conex = mapeamento_conex.get(fases, ".1")
            
            arquivo.write(f"New line.ram{cod_id} phases={phases} bus1={bus1}{conex} bus2={bus2}{conex} length={length} units=km linecode={linecode}\n")
    
    end_ramlig = time.time()

    print(f"Ramal de Ligação Finalizado! - Tempo: {end_ramlig - start_ramlig:.2f} s")

def generate_gds(feeder, dicionario_kv, mapeamento_phases, mapeamento_conex, mapeamento_conn, output_dir=None):
    start_gds = time.time()
    ugmt = pd.read_csv(r'Inputs\UGMT.csv', sep=',')
    ugbt = pd.read_csv(r'Inputs\UGBT.csv', sep=',')
    ugmt_filtered = ugmt[ugmt['CTMT'] == feeder]
    ugbt_filtered = ugbt[ugbt['CTMT'] == feeder]
    
    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'gds.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        arquivo.write("New Loadshape.MyIrrad npts=24 interval=1 mult=[0 0 0 0 0 0 0.03 0.18 0.44 0.7 0.9 0.98 1 0.94 0.8 0.6 0.35 0.14 0.016 0 0 0 0 0] \n")
        arquivo.write("New Tshape.MyTemp npts=24 interval=1 temp=[21.5 21 20.6 20.2 19.8 19.5 19.2 20.2 25.5 34.3 42.6 49.3 53.6 55.1 54.4 51.3 45.6 38.4 31.1 25.7 24.0 23.2 22.5 22] \n")
        arquivo.write("New XYCurve.MyPvsT npts=4 xarray=[0 25 75 100] yarray=[1.2 1.0 0.8 0.6] \n")
        arquivo.write("New XYCurve.MyEff npts=4 xarray=[0.1 0.2 0.4 1.0] yarray=[0.86 0.90 0.93 0.97] \n\n")

        for index, linha in ugmt_filtered.iterrows():
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            kv = dicionario_kv.get(linha["TEN_CON"], 13.8)
            potencia = linha["POT_INST"]

            if potencia <= 1: potencia = 10 #Muitos UGMT de Uberlândia não possuem a potência instalada correta, então foi feito um tratamento para que a potência seja 10kVA
            
            fp = 1  # Fator de potência da maioria dos inversores do Brasil
            fases = linha["FAS_CON"]

            phases = mapeamento_phases.get(fases, 2)
            conex = mapeamento_conex.get(fases, ".1.2")
            conn = mapeamento_conn.get(fases, "delta")


            arquivo.write(f"New PVSystem.MT{cod_id} bus1={bus}{conex} phases={phases} conn={conn} kv={kv} kva={potencia} pf={fp} irrad=0.84 pmpp=5.1 temperature=25 %cutin=0.1 %cutout=0.1 effcurve=MyEff p-tcurve=MyPvsT Daily=MyIrrad TDaily=MyTemp \n\n")

        for index, linha in ugbt_filtered.iterrows():
            cod_id = linha["OBJECTID"]
            bus = linha["PAC"]
            kv = dicionario_kv.get(linha["TEN_CON"], 0.22)
            potencia = linha["POT_INST"]
            fp = 1  # Fator de potência da maioria dos inversores do Brasil
            fases = linha["FAS_CON"]

            phases = mapeamento_phases.get(fases, 2)
            conex = mapeamento_conex.get(fases, ".1.2")
            conn = mapeamento_conn.get(fases, "delta")

            arquivo.write(f"New PVSystem.BT{cod_id} bus1={bus}{conex} phases={phases} conn={conn} kv={kv} kva={potencia} pf={fp} irrad=0.84 pmpp=5.1 temperature=25 %cutin=0.1 %cutout=0.1 effcurve=MyEff p-tcurve=MyPvsT Daily=MyIrrad TDaily=MyTemp \n")

        end_gds = time.time()
        print(f"GDs de baixa e média Finalizadas! - Tempo:{end_gds - start_gds:.2f} s")

def generate_coordenadas(feeder, output_dir=None):
    start_coord = time.time()
    coord = pd.read_csv(r'Inputs\Coord.csv', sep=';')
    coord_filtered = coord[coord['CTMT'] == feeder]
    # Conjunto para armazenar pontos únicos
    pontos_unicos = set()

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'coordenadasMT.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in coord_filtered.iterrows():
            coluna1 = linha["wkt_geom"]
            padrao = r"[-+]?\d*\.\d+|\d+"
            coordenadas = re.findall(padrao, coluna1)
            
            coord1, coord2, coord3, coord4 = map(float, coordenadas[:4])
            pac1, pac2 = linha["PAC_1"], linha["PAC_2"]

            # Verificar se o ponto já foi registrado como único
            if (pac1, coord1, coord2) not in pontos_unicos:
                arquivo.write(f"{pac1} {coord1} {coord2}\n")
                pontos_unicos.add((pac1, coord1, coord2))
            if (pac2, coord3, coord4) not in pontos_unicos:
                arquivo.write(f"{pac2} {coord3} {coord4}\n")
                pontos_unicos.add((pac2, coord3, coord4))

        end_coord = time.time()
        print(f"Coordenadas Finalizadas! - Tempo:{end_coord - start_coord:.2f} s")

def generate_capacitores(feeder, dicionario_capacitores, output_dir=None):
    start_cap = time.time()
    cap = pd.read_csv(r'Inputs\UNCRMT.csv', sep=',')
    cap_filtered = cap[cap['CTMT'] == feeder]

    if output_dir is None:
        output_dir = os.getcwd()
    output_file_path = os.path.join(output_dir, 'capacitores.dss') 
    
    with open(output_file_path, 'w') as arquivo:
        for index, linha in cap_filtered.iterrows():
            cod_id = linha["COD_ID"]
            fases = 3 
            pac1 = linha["PAC_1"]
            kvar = dicionario_capacitores.get(linha["POT_NOM"], 100)

            arquivo.write(f"new load.cap{cod_id} phases={fases} model=1 bus1={pac1}.1.2.3 kvar={kvar}\n")

        end_cap = time.time()
        print(f"Capacitores Finalizados! - Tempo:{end_cap - start_cap:.2f} s")
