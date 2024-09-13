import os
import bdgd2dss
import time
import dicionarios

start_total = time.time()


#alimentador = 5001990

alimentadores =  ['ULAD202', 'ULAD203', 'ULAD204', 'ULAD205', 'ULAD206', 'ULAD208', 'ULAD209', 'ULAD210', 'ULAD211', 
                  'ULAD212', 'ULAD215', 'ULAD216', 'ULAD217', 'ULAD218', 'ULAD219', 'ULAE704', 'ULAE705', 'ULAE707', 
                  'ULAE708', 'ULAE709', 'ULAE712', 'ULAE713', 'ULAE714', 'ULAE716', 'ULAE718', 'ULAE721', 'ULAE722', 
                  'ULAE724', 'ULAE726', 'ULAE728', 'ULAN902', 'ULAN903', 'ULAS602', 'ULAS603', 'ULAS604', 'ULAS606', 
                  'ULAS607', 'ULAS609', 'ULAS610', 'ULAS612', 'ULAS613', 'ULAS614', 'ULAS626', 'ULAS627', 'ULAS628', 
                  'ULAS629', 'ULAS633', 'ULAS634', 'ULAU01', 'ULAU02', 'ULAU03', 'ULAU05', 'ULAU11', 'ULAU12', 'ULAU13', 
                  'ULAU14', 'ULAU15', 'ULAU35', 'ULAU36', 'ULAU37', 'ULAU38', 'ULAU41']

"""Escolher o dia de análise:
    DU: Curva típica de dia útil
    SA: Curva típica de sábado
    DO: Curva típica de domingos e feriados"""

dia_de_analise = 'DU'
base_dir = os.getcwd()

start_total = time.time()

for alimentador in alimentadores:
    pasta_path = str(alimentador)
    os.makedirs(pasta_path, exist_ok=True)
    print(f'\nPasta criada: {pasta_path}')
    
    bdgd2dss.generate_master(alimentador, dicionarios.dicionario_kv, dicionarios.dicionario_kva, dia_de_analise, output_dir=pasta_path)
    bdgd2dss.generate_crvcrg(output_dir=pasta_path)
    bdgd2dss.generate_linecode(output_dir=pasta_path)
    bdgd2dss.generate_ssdmt(alimentador, output_dir=pasta_path)
    bdgd2dss.generate_trafosMT(alimentador,dicionarios.dicionario_kv, dicionarios.mapeamento_conex, dicionarios.lig_trafo, output_dir=pasta_path)
    bdgd2dss.generate_ssdBT(alimentador, dicionarios.mapeamento_conex, dicionarios.mapeamento_phases, output_dir=pasta_path)
    bdgd2dss.generate_ucmt(alimentador, dicionarios.mapeamento_conex, dicionarios.dicionario_kv, output_dir=pasta_path)
    bdgd2dss.generate_ucbt(alimentador, dicionarios.dicionario_kv, dicionarios.mapeamento_phases, dicionarios.mapeamento_conex, dicionarios.mapeamento_conn, output_dir=pasta_path)
    bdgd2dss.generate_pip(alimentador, dicionarios.dicionario_kv, dicionarios.mapeamento_phases, dicionarios.mapeamento_conex, dicionarios.mapeamento_conn, output_dir=pasta_path)
    bdgd2dss.generate_ssdunsemt(alimentador, dicionarios.dicionario_tip_unid, output_dir=pasta_path)
    bdgd2dss.generate_ramlig(alimentador, dicionarios.mapeamento_phases, dicionarios.mapeamento_conex, output_dir=pasta_path)
    bdgd2dss.generate_gds(alimentador, dicionarios.dicionario_kv, dicionarios.mapeamento_phases, dicionarios.mapeamento_conex, dicionarios.mapeamento_conn, output_dir=pasta_path)
    bdgd2dss.generate_capacitores(alimentador, dicionarios.dicionario_capacitores, output_dir=pasta_path)
    bdgd2dss.generate_coordenadas(alimentador, output_dir=pasta_path)

end_total = time.time()
print(f"\nSimulação total demorou: {end_total - start_total} s")