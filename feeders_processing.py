import os
import bdgd2dss
import time

start_total = time.time()
dicionario_kv = {
    3: 0.120,
    6: 0.127,
    10: 0.220,
    13: 0.240,
    23: 2.2,
    38: 6.93,
    39: 7.96,
    45: 12.7,
    49: 13.8,
    61: 22.0,
    62: 23.0,
    69: 27.0,
    71: 33.0,
    72: 34.5,
    77: 35.0,
    82: 69.0,
    94: 138.0,
    95: 145.0
}
dicionario_kva = {
    54:2500,
    59:3300,
    62:4200,
    64:5000,
    67:7000,
    68:7500,
    72:9375,
    74:10000,
    76:12500,
    77:13300,
    78:15000,
    82:20000,
    83:25000,
    87:30000,
    89:33000,
    90:33300,
    91:40000,
    94:64000
}
dicionario_tip_unid = {
    19: "Chave Faca",
    20: "Chave Faca Tripolar Abertura com Carga",
    22: "Chave Fusivel",
    29: "Disjuntor",
    32: "Religador",
    33: "Seccionadora Tripolar da SE",
    34: "Seccionadora Unipolar da SE",
    35: "Seccionalizador"
}
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


"""Escolher o dia de análise:
    DU: Curva típica de dia útil
    SA: Curva típica de sábado
    DO: Curva típica de domingos e feriados"""
dia_de_analise = 'DU'
base_dir = os.getcwd()
for alimentador in alimentadoresudia:
    feeder = alimentador
    pasta_path = os.path.join(base_dir, alimentador)
    os.makedirs(pasta_path, exist_ok=True)
    print(f'Pasta criada: {pasta_path}')

    bdgd2dss.generate_master(feeder, dicionario_kv, dicionario_kva, dia_de_analise, output_dir=pasta_path)
    bdgd2dss.generate_crvcrg(output_dir=pasta_path)
    bdgd2dss.generate_linecode(output_dir=pasta_path)
    bdgd2dss.generate_ssdmt(feeder, output_dir=pasta_path)
    bdgd2dss.generate_trafosMT(feeder, output_dir=pasta_path)
    bdgd2dss.generate_ssdBT(feeder, output_dir=pasta_path)
    bdgd2dss.generate_ucmt(feeder, output_dir=pasta_path)
    bdgd2dss.generate_ucbt(feeder, output_dir=pasta_path)
    bdgd2dss.generate_pip(feeder, output_dir=pasta_path)
    bdgd2dss.generate_ssdunsemt(dicionario_tip_unid, feeder, output_dir=pasta_path)
    bdgd2dss.generate_ramlig(feeder, output_dir=pasta_path)
    bdgd2dss.generate_gds(feeder, output_dir=pasta_path)
    bdgd2dss.generate_coordenadas(feeder, output_dir=pasta_path)
    bdgd2dss.generate_capacitores(feeder, output_dir=pasta_path)

end_total = time.time()
print(f"\nSimulação total demorou: {end_total - start_total} s")

