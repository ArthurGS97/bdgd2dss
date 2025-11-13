import os
import time
import csv

inicio = time.time()

output_dir = "C:/CEMIG23/Inputs"  # Ajuste conforme necessário

# Valores válidos para o campo SUB
sub_values = ('1726720', '1726707', '1726712')

# Definir os sufixos das camadas que serão exportadas
layers_to_export = [
    'CRVCRG', 'CTMT', 'EQRE', 'EQTRMT', 'PIP', 'RAMLIG', 'SEGCON', 'SSDBT',
    'SSDMT', 'UCBT_tab', 'UCMT_tab', 'UGBT_tab', 'UGMT_tab', 'UNCRMT',
    'UNREMT', 'UNSEBT', 'UNSEMT', 'UNTRMT', 'SUB', 'UNTRD', 'EQTRD'
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
            print(f"Camada {layer.name()} filtrada com COD_ID em {sub_values}.\n")
        
        elif 'SUB' in layer_fields:
            filter_expression = f"SUB IN {sub_values}"
            layer.setSubsetString(filter_expression)
            print(f"Camada {layer.name()} filtrada com SUB em {sub_values}.\n")


# Garantir que o diretório existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Dicionário com as colunas a exportar por tipo de camada ---
# Basta adicionar novos tipos no formato:
# "NOME_DO_TIPO": ["COL1", "COL2", ...]
cols_por_tipo = {
    "EQRE": [
        "OBJECTID", "COD_ID", "UN_RE", "PAC_1", "PAC_2", "POT_NOM", "TEN_REG", 
        "LIG_FAS_P", "LIG_FAS_S", "REL_TP", "PER_FER", "PER_TOT", "R", "XHL"
    ],
    "EQTRMT": [
        "OBJECTID", "COD_ID", "UNI_TR_MT", "PAC_1", "PAC_2", "PAC_3", "CLAS_TEN", "POT_NOM", "LIG", 
        "FAS_CON", "TEN_PRI", "TEN_SEC", "TEN_TER", "LIG_FAS_P", "LIG_FAS_S", 
        "LIG_FAS_T", "PER_FER", "PER_TOT", "R", "XHL", "XHT", "XLT"
    ],
    "EQTRD": [
        "OBJECTID", "COD_ID", "PAC_1", "PAC_2", "PAC_3", "CLAS_TEN", "POT_NOM", "LIG", 
        "FAS_CON", "TEN_PRI", "TEN_SEC", "TEN_TER", "LIG_FAS_P", "LIG_FAS_S", 
        "LIG_FAS_T", "PER_FER", "PER_TOT", "R", "XHL", "XHT", "XLT"
    ],
    "PIP": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "UNI_TR_AT", "CTMT", "UNI_TR_D", "UNI_TR_MT", "FAS_CON", "TEN_FORN",
        "SIT_ATIV", "PAC", "TIP_CC", "ENE_01", "ENE_02", "ENE_03", "ENE_04", "ENE_05",
        "ENE_06", "ENE_07", "ENE_08", "ENE_09", "ENE_10", "ENE_11", "ENE_12"
    ],
    "RAMLIG": [
        "OBJECTID", "COD_ID","PAC_1", "PAC_2","UNI_TR_D", "UNI_TR_MT", "CTMT","FAS_CON",
        "UNI_TR_S", "UNI_TR_AT", "UNI_TR_AT", "SUB", "TIP_CND", "COMP"
    ],
    "SEGCON": [
        "OBJECTID", "COD_ID", "R1", "X1", "CMAX"
    ],
    "SSDBT": [
        "OBJECTID","COD_ID", "UNI_TR_D", "UNI_TR_MT", "CTMT", "UNI_TR_S", "UNI_TR_AT", "SUB", "FAS_CON", "PAC_1", "PAC_2", "TIP_CND", "COMP"
    ],
    "SSDMT": [
        "OBJECTID","COD_ID", "CTMT", "UNI_TR_S", "UNI_TR_AT", "SUB", "FAS_CON", "PAC_1", "PAC_2", "TIP_CND", "COMP"
    ],
    "UCBT_tab": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "UNI_TR_D", "UNI_TR_MT", "FAS_CON", "TEN_FORN",
        "SIT_ATIV", "PAC", "TIP_CC", "ENE_01", "ENE_02", "ENE_03", "ENE_04", "ENE_05",
        "ENE_06", "ENE_07", "ENE_08", "ENE_09", "ENE_10", "ENE_11", "ENE_12"
    ],
    "UCMT_tab": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "FAS_CON", "TEN_FORN",
        "SIT_ATIV", "PAC", "TIP_CC", "ENE_01", "ENE_02", "ENE_03", "ENE_04", "ENE_05",
        "ENE_06", "ENE_07", "ENE_08", "ENE_09", "ENE_10", "ENE_11", "ENE_12"
    ],
    "UGBT_tab": [
        "OBJECTID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "UNI_TR_D", "UNI_TR_MT", "FAS_CON", "TEN_FORN",
        "SIT_ATIV", "PAC", "TEN_CON", "POT_INST"
    ],
    "UGMT_tab": [
        "OBJECTID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "FAS_CON", "TEN_FORN",
        "SIT_ATIV", "PAC", "TEN_CON", "POT_INST"
    ],
    "UNCRMT": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "FAS_CON", "POT_NOM",
        "SIT_ATIV", "PAC_1", "PAC_2", "TIP_UNID"
    ],
    "UNREMT": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "FAS_CON", "POT_NOM",
        "SIT_ATIV", "PAC_1", "PAC_2", "TIP_UNID"
    ],
    "UNSEBT": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "FAS_CON", "POT_NOM",
        "SIT_ATIV", "PAC_1", "PAC_2", "TIP_UNID", "P_N_OPE", "CAP_ELO", "COR_NOM",
        "UNI_TR_D"
    ],
    "UNSEMT": [
        "OBJECTID", "COD_ID", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT", "FAS_CON", "POT_NOM",
        "SIT_ATIV", "PAC_1", "PAC_2", "TIP_UNID", "P_N_OPE", "CAP_ELO", "COR_NOM"
    ],
    "UNTRD": [
        "OBJECTID", "COD_ID", "PAC_1", "PAC_2", "PAC_3", "SUB", "UNI_TR_S", "UNI_TR_AT", "CTMT",
        "FAS_CON_P", "FAS_CON_S", "FAS_CON_T", "SIT_ATIV", "TEN_LIN_SE", "TAP",
        "POT_NOM", "PER_FER", "PER_TOT", "TIP_TRAFO"
    ],
    "UNTRMT": [
        "OBJECTID","COD_ID","PAC_1","PAC_2","PAC_3","FAS_CON_P","FAS_CON_S",
        "FAS_CON_T","SIT_ATIV","TIP_UNID","TEN_LIN_SE","TAP","POT_NOM","PER_FER",
        "PER_TOT","CTMT","UNI_TR_AT","SUB","TIP_TRAFO"
    ]
}

# --- Exportar camadas ---
def export():
    for layer in filtered_layers:
        layer_name = layer.name()
        if any(layer_name.endswith(f' — {suffix}') for suffix in layers_to_export):

            # Extrai o sufixo (parte após o "—")
            tipo = layer_name.split(" — ")[-1].strip()

            # Verifica se existe uma lista de colunas para esse tipo
            if tipo in cols_por_tipo:
                keep_fields = [f.name() for f in layer.fields() if f.name() in cols_por_tipo[tipo]]
                layer_to_export = layer.materialize(
                    QgsFeatureRequest().setSubsetOfAttributes(keep_fields, layer.fields())
                )
                export_type = f"filtrada ({tipo})"
            else:
                # Caso não tenha regra específica, exporta completa
                layer_to_export = layer
                export_type = "completa"

            # Caminho de saída
            csv_filename = os.path.join(output_dir, f"{layer_name}.csv")

            # Exporta camada
            error = QgsVectorFileWriter.writeAsVectorFormat(
                layer_to_export, csv_filename, "utf-8", layer.crs(), "CSV"
            )

            # Status
            if error[0] == QgsVectorFileWriter.NoError:
                print(f"✅ Camada {layer_name} exportada ({export_type}) para {csv_filename}.\n")
            else:
                print(f"❌ Erro ao exportar camada {layer_name} ({export_type}).\n")


# Gerar o arquivo de coordenadas baseado na camada SSDMT
def coord():
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

export()
coord()