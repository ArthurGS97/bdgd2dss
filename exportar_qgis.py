import os
import time
import csv


inicio = time.time()

# Defina o diretório onde os arquivos CSV serão salvos
output_dir = "C:/0411/PB/Inputs"  # Substitua com o caminho onde deseja salvar os arquivos CSV

pref = "Energisa_PB_6600_2022-12-31_V11_20230919-0837"

# Definir a lista de valores para o campo 'SUB'
sub_values = ('12873414', '12873483', '12873416', '12873415', '12873479')



# Iterar sobre todas as camadas carregadas no projeto
for layer in QgsProject.instance().mapLayers().values():
    # Verificar se a camada é do tipo vetorial
    if layer.type() == QgsMapLayer.VectorLayer:
        # Verificar se a camada tem o atributo "SUB"
        if 'SUB' in [field.name() for field in layer.fields()]:
            # Aplicar filtro com múltiplos valores usando a cláusula IN
            filter_expression = f"SUB IN {sub_values}"
            layer.setSubsetString(filter_expression)
            print(f"Camada {layer.name()} filtrada com SUB em {sub_values}.")




ssdmt = QgsProject.instance().mapLayersByName(f"{pref} — SSDMT")[0] 

# Verifique se o diretório existe, caso contrário, crie-o
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Iterar sobre todas as camadas carregadas no projeto
for layer in QgsProject.instance().mapLayers().values():
    # Definir o nome do arquivo CSV para a camada
    csv_filename = os.path.join(output_dir, f"{layer.name()}.csv")
    
    # Exportar a camada para CSV
    error = QgsVectorFileWriter.writeAsVectorFormat(layer, csv_filename, "utf-8", layer.crs(), "CSV")

file_path = os.path.join(output_dir, "coordenadas.csv")

    # Abrindo o arquivo CSV para escrita
with open(file_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    writer.writerow(["CTMT", "PAC1", "Coord1", "PAC2", "Coord2"])

    
    # Iterando sobre as features (linhas) da camada
    for feature in ssdmt.getFeatures():
        # Pegando os valores dos atributos PAC_1 e PAC_2
        ctmt = feature["CTMT"]
        pac_1 = feature["PAC_1"]
        pac_2 = feature["PAC_2"]
        
        # Obtendo a geometria da linha
        geom = feature.geometry()
        
        # Verificando se a geometria é MultiLineString ou LineString
        if geom.isMultipart():
            # Se for MultiLineString, pegamos a primeira linha do conjunto
            line = geom.asMultiPolyline()[0]
        else:
            # Se for uma LineString simples, pegamos a linha diretamente
            line = geom.asPolyline()
        
        # Verificando se a linha tem ao menos dois pontos
        if len(line) >= 2:
            # Ponto inicial e ponto final da linha
            coord_1 = line[0]  # Coordenada inicial
            coord_2 = line[-1] # Coordenada final
            
            # Formatando as coordenadas como strings
            coord_1_str = f"{coord_1.x()}, {coord_1.y()}"
            coord_2_str = f"{coord_2.x()}, {coord_2.y()}"
            
            # Escrevendo a linha no CSV
            writer.writerow([ctmt,pac_1, coord_1_str, pac_2, coord_2_str])

fim = time.time()
print("Arquivo coordenadas gerado com sucesso!")
print (fim - inicio)

    