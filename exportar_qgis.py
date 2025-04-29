import os
import time
import csv

inicio = time.time()

# Diretório onde os CSVs serão salvos
output_dir = "C:/abril/bdgd2dss/Inputs"  # Ajuste conforme necessário

# Definir os sufixos das camadas que serão exportadas
layers_to_export = ['CRVCRG', 'CTMT', 'EQRE', 'EQTRMT', 'PIP', 'RAMLIG', 'SEGCON', 'SSDBT', 'SSDMT', 'UCBT_tab', 'UCMT_tab', 'UGBT_tab', 'UGMT_tab', 'UNCRMT', 'UNREMT', 'UNSEBT', 'UNSEMT', 'UNTRMT']

# Definir valores de 'SUB' para filtro
sub_values = ('12873414', '')  # Defina os valores necessários


# Extrair o prefixo 'pref' automaticamente
all_layers = list(QgsProject.instance().mapLayers().values())

if not all_layers:
    raise Exception("Nenhuma camada carregada no projeto.")

first_layer_name = all_layers[0].name()
pref = first_layer_name.split(' — ')[0]  # Pega tudo antes do primeiro ' — '
print(f"Prefixo extraído: {pref}")

# Definir valores de 'SUB' para filtro
sub_values = ('12873414', '')  # Defina os valores necessários

# Filtrar as camadas
for layer in all_layers:
    if layer.type() == QgsMapLayer.VectorLayer:
        if 'SUB' in [field.name() for field in layer.fields()]:
            filter_expression = f"SUB IN {sub_values}"
            layer.setSubsetString(filter_expression)
            print(f"Camada {layer.name()} filtrada com SUB em {sub_values}.")

# Garantir que o diretório existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Exportar apenas as camadas especificadas
for layer in all_layers:
    if any(layer.name().endswith(f' — {suffix}') for suffix in layers_to_export):
        csv_filename = os.path.join(output_dir, f"{layer.name()}.csv")
        error = QgsVectorFileWriter.writeAsVectorFormat(layer, csv_filename, "utf-8", layer.crs(), "CSV")
        if error[0] == QgsVectorFileWriter.NoError:
            print(f"Camada {layer.name()} exportada com sucesso para {csv_filename}.")
        else:
            print(f"Erro ao exportar camada {layer.name()}.")

# Gerar o arquivo de coordenadas baseado na camada SSDMT
ssdmt_layer_name = f"{pref} — SSDMT"
ssdmt_layers = QgsProject.instance().mapLayersByName(ssdmt_layer_name)

if not ssdmt_layers:
    raise Exception(f"Camada '{ssdmt_layer_name}' não encontrada.")
    
ssdmt = ssdmt_layers[0]

file_path = os.path.join(output_dir, f"{pref} — Coordenadas.csv")

with open(file_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["CTMT", "PAC1", "Coord1", "PAC2", "Coord2"])

    for feature in ssdmt.getFeatures():
        ctmt = feature["CTMT"]
        pac_1 = feature["PAC_1"]
        pac_2 = feature["PAC_2"]
        geom = feature.geometry()

        if geom.isMultipart():
            line = geom.asMultiPolyline()[0]
        else:
            line = geom.asPolyline()

        if len(line) >= 2:
            coord_1_str = f"{line[0].x()}, {line[0].y()}"
            coord_2_str = f"{line[-1].x()}, {line[-1].y()}"
            writer.writerow([ctmt, pac_1, coord_1_str, pac_2, coord_2_str])

fim = time.time()
print("Arquivo coordenadas.csv gerado com sucesso!")
print(f"Tempo de execução: {fim - inicio:.2f} segundos.")
