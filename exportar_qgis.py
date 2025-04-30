import os
import time
import csv

inicio = time.time()

output_dir = "C:/BA/bdgd2dss/Inputs"  # Ajuste conforme necessário

# Valores válidos para o campo SUB
sub_values = ('COD', 'BRE', 'BRN', '')

# Definir os sufixos das camadas que serão exportadas
layers_to_export = [
    'CRVCRG', 'CTMT', 'EQRE', 'EQTRMT', 'PIP', 'RAMLIG', 'SEGCON',
    'SSDBT', 'SSDMT', 'UCBT_tab', 'UCMT_tab', 'UGBT_tab', 'UGMT_tab',
    'UNCRMT', 'UNREMT', 'UNSEBT', 'UNSEMT', 'UNTRMT', 'SUB'
]


# Obter todas as camadas carregadas
all_layers = list(QgsProject.instance().mapLayers().values())

if not all_layers:
    raise Exception("Nenhuma camada carregada no projeto.")

# Extrair prefixo do nome da primeira camada
first_layer_name = all_layers[0].name()
pref = first_layer_name.split(' — ')[0]
print(f"Prefixo extraído: {pref}")

# Criar lista de camadas que não serão exportadas (a serem removidas)
layers_to_remove = [
    layer for layer in all_layers
    if not any(layer.name().endswith(f' — {suffix}') for suffix in layers_to_export)
]

# Remover essas camadas do projeto com segurança
for layer in layers_to_remove:
    layer_name = layer.name()  # <- ESSA LINHA É ESSENCIAL
    QgsProject.instance().removeMapLayer(layer)
    print(f"Camada {layer_name} removida do projeto.")

# Re-obter as camadas restantes após a remoção
filtered_layers = list(QgsProject.instance().mapLayers().values())

# Aplicar filtros condicionais nas camadas
for layer in filtered_layers:
    if layer.type() == QgsMapLayer.VectorLayer:
        layer_fields = [field.name() for field in layer.fields()]
        
        if layer.name().endswith(" — SUB") and 'COD_ID' in layer_fields:
            filter_expression = f"COD_ID IN {sub_values}"
            layer.setSubsetString(filter_expression)
            print(f"Camada {layer.name()} filtrada com COD_ID em {sub_values}.")
        
        elif 'SUB' in layer_fields:
            filter_expression = f"SUB IN {sub_values}"
            layer.setSubsetString(filter_expression)
            print(f"Camada {layer.name()} filtrada com SUB em {sub_values}.")


# Garantir que o diretório existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Exportar apenas as camadas especificadas
for layer in filtered_layers:
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