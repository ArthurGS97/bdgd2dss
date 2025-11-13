import re

feeder = "ULAU11"  # Altere para o alimentador desejado

# --- Caminhos dos seus arquivos DSS ---
arquivo_dss = arquivo_saida = rf"{feeder}\pip_{feeder}.dss"

# --- Conteúdo colado diretamente (copie e cole aqui o texto do seu arquivo TXT) ---
conteudo_txt = """
"Load.pip42867-1"  Buses:  "node#1911041366.1.2"
"Load.pip42867-2"  Buses:  "node#1911041366.1.2"
"Load.pip56207-1"  Buses:  "node#512219068.1.2"
"Load.pip56207-2"  Buses:  "node#512219068.1.2"
"Load.pip101074-1"  Buses:  "node#1770361869.2.3"
"Load.pip101074-2"  Buses:  "node#1770361869.2.3"
"Load.pip147599-1"  Buses:  "node#465408165.3.1"
"Load.pip147599-2"  Buses:  "node#465408165.3.1"
"Load.pip275087-1"  Buses:  "node#1770524507.3.1"
"Load.pip275087-2"  Buses:  "node#1770524507.3.1"
"Load.pip286815-1"  Buses:  "node#1768526026.1.2"
"Load.pip286815-2"  Buses:  "node#1768526026.1.2"
"Load.pip293415-1"  Buses:  "node#1770768246.1.2"
"Load.pip293415-2"  Buses:  "node#1770768246.1.2"
"Load.pip293581-1"  Buses:  "node#512219068.1.2"
"Load.pip293581-2"  Buses:  "node#512219068.1.2"
"Load.pip513619-1"  Buses:  "node#1769387647.1.2"
"Load.pip513619-2"  Buses:  "node#1769387647.1.2"
"Load.pip513703-1"  Buses:  "node#1769686012.1.2"
"Load.pip513703-2"  Buses:  "node#1769686012.1.2"
"Load.pip517531-1"  Buses:  "node#1769063781.2.3"
"Load.pip517531-2"  Buses:  "node#1769063781.2.3"
"Load.pip517608-1"  Buses:  "node#1769024772.3.1"
"Load.pip517608-2"  Buses:  "node#1769024772.3.1"
"Load.pip538817-1"  Buses:  "node#1769284488.2.3"
"Load.pip538817-2"  Buses:  "node#1769284488.2.3"
"Load.pip770316-1"  Buses:  "node#1768695288.2.3"
"Load.pip770316-2"  Buses:  "node#1768695288.2.3"
"Load.pip771495-1"  Buses:  "node#1770524091.3.1"
"Load.pip771495-2"  Buses:  "node#1770524091.3.1"
"Load.pip771522-1"  Buses:  "node#1770864831.3.1"
"Load.pip771522-2"  Buses:  "node#1770864831.3.1"
"Load.pip771526-1"  Buses:  "node#1770413980.2.3"
"Load.pip771526-2"  Buses:  "node#1770413980.2.3"
"Load.pip772027-1"  Buses:  "node#1768617668.2.3"
"Load.pip772027-2"  Buses:  "node#1768617668.2.3"
"Load.pip781286-1"  Buses:  "node#1770141972.3.1"
"Load.pip781286-2"  Buses:  "node#1770141972.3.1"
"Load.pip813885-1"  Buses:  "node#1770169924.3.1"
"Load.pip813885-2"  Buses:  "node#1770169924.3.1"
"Load.pip986535-1"  Buses:  "node#1770785276.1.2"
"Load.pip986535-2"  Buses:  "node#1770785276.1.2"
"Load.pip992348-1"  Buses:  "node#1769063614.1.2"
"Load.pip992348-2"  Buses:  "node#1769063614.1.2"
"Load.pip993858-1"  Buses:  "node#1770170623.2.3"
"Load.pip993858-2"  Buses:  "node#1770170623.2.3"
"Load.pip1003423-1"  Buses:  "node#1770441935.3.1"
"Load.pip1003423-2"  Buses:  "node#1770441935.3.1"
"Load.pip1005487-1"  Buses:  "node#512196088.1.2"
"Load.pip1005487-2"  Buses:  "node#512196088.1.2"
"Load.pip1008710-1"  Buses:  "node#1770504577.1.2"
"Load.pip1008710-2"  Buses:  "node#1770504577.1.2"
"Load.pip1008959-1"  Buses:  "node#1770170413.3.1"
"Load.pip1008959-2"  Buses:  "node#1770170413.3.1"
"Load.pip1009066-1"  Buses:  "node#1770875920.1.2"
"Load.pip1009066-2"  Buses:  "node#1770875920.1.2"
"Load.pip1034450-1"  Buses:  "node#1768775743.1.2"
"Load.pip1034450-2"  Buses:  "node#1768775743.1.2"
"Load.pip1050766-1"  Buses:  "node#462105437.1.2"
"Load.pip1050766-2"  Buses:  "node#462105437.1.2"
"Load.pip1232460-1"  Buses:  "node#1911045893.1.2"
"Load.pip1232460-2"  Buses:  "node#1911045893.1.2"
"Load.pip1246204-1"  Buses:  "node#1770492744.3.1"
"Load.pip1246204-2"  Buses:  "node#1770492744.3.1"
"Load.pip1255755-1"  Buses:  "node#1769861706.3.1"
"Load.pip1255755-2"  Buses:  "node#1769861706.3.1"
"Load.pip1262201-1"  Buses:  "node#1770593854.1.2"
"Load.pip1262201-2"  Buses:  "node#1770593854.1.2"
"Load.pip1271843-1"  Buses:  "node#1769127401.1.2"
"Load.pip1271843-2"  Buses:  "node#1769127401.1.2"
"Load.pip1271879-1"  Buses:  "node#1768618013.1.2"
"Load.pip1271879-2"  Buses:  "node#1768618013.1.2"
"Load.pip1289714-1"  Buses:  "node#1770195393.1.2"
"Load.pip1289714-2"  Buses:  "node#1770195393.1.2"
"Load.pip1440056-1"  Buses:  "node#1766001135.3.1"
"Load.pip1440056-2"  Buses:  "node#1766001135.3.1"
"Load.pip1461247-1"  Buses:  "node#1770481430.1.2"
"Load.pip1461247-2"  Buses:  "node#1770481430.1.2"
"Load.pip1463270-1"  Buses:  "node#1769621688.1.2"
"Load.pip1463270-2"  Buses:  "node#1769621688.1.2"
"Load.pip1465762-1"  Buses:  "node#1770461040.1.2"
"Load.pip1465762-2"  Buses:  "node#1770461040.1.2"
"Load.pip1468860-1"  Buses:  "node#1911045898.1.2"
"Load.pip1468860-2"  Buses:  "node#1911045898.1.2"
"Load.pip1485743-1"  Buses:  "node#1770364004.3.1"
"Load.pip1485743-2"  Buses:  "node#1770364004.3.1"
"Load.pip1492809-1"  Buses:  "node#1770036914.3.1"
"Load.pip1492809-2"  Buses:  "node#1770036914.3.1"
"Load.pip1500692-1"  Buses:  "node#1769421864.1.2"
"Load.pip1500692-2"  Buses:  "node#1769421864.1.2"
"Load.pip1699582-1"  Buses:  "node#1770525840.3.1"
"Load.pip1699582-2"  Buses:  "node#1770525840.3.1"
"Load.pip1717513-1"  Buses:  "node#512196093.1.2"
"Load.pip1717513-2"  Buses:  "node#512196093.1.2"
"Load.pip1720923-1"  Buses:  "node#1770195732.1.2"
"Load.pip1720923-2"  Buses:  "node#1770195732.1.2"
"Load.pip1730261-1"  Buses:  "node#1769861760.3.1"
"Load.pip1730261-2"  Buses:  "node#1769861760.3.1"
"Load.pip1731305-1"  Buses:  "node#1769909525.3.1"
"Load.pip1731305-2"  Buses:  "node#1769909525.3.1"
"Load.pip1736117-1"  Buses:  "node#1769422982.3.1"
"Load.pip1736117-2"  Buses:  "node#1769422982.3.1"
"Load.pip1914564-1"  Buses:  "node#1769387004.2.3"
"Load.pip1914564-2"  Buses:  "node#1769387004.2.3"
"Load.pip1935746-1"  Buses:  "node#1770075268.3.1"
"Load.pip1935746-2"  Buses:  "node#1770075268.3.1"
"Load.pip1938118-1"  Buses:  "node#1769387438.1.2"
"Load.pip1938118-2"  Buses:  "node#1769387438.1.2"
"Load.pip1940488-1"  Buses:  "node#1770413018.2.3"
"Load.pip1940488-2"  Buses:  "node#1770413018.2.3"
"Load.pip1954881-1"  Buses:  "node#512196093.1.2"
"Load.pip1954881-2"  Buses:  "node#512196093.1.2"
"Load.pip1954915-1"  Buses:  "node#512192898.1.2"
"Load.pip1954915-2"  Buses:  "node#512192898.1.2"
"Load.pip1976868-1"  Buses:  "node#1768597469.2.3"
"Load.pip1976868-2"  Buses:  "node#1768597469.2.3"
"Load.pip1977223-1"  Buses:  "node#1768560596.1.2"
"Load.pip1977223-2"  Buses:  "node#1768560596.1.2"
"Load.pip1984652-1"  Buses:  "node#1770086703.1.2"
"Load.pip1984652-2"  Buses:  "node#1770086703.1.2"
"Load.pip2181032-1"  Buses:  "node#1770285748.3.1"
"Load.pip2181032-2"  Buses:  "node#1770285748.3.1"
"Load.pip2181279-1"  Buses:  "node#1770311037.1.2"
"Load.pip2181279-2"  Buses:  "node#1770311037.1.2"
"Load.pip2192281-1"  Buses:  "node#512192898.1.2"
"Load.pip2192281-2"  Buses:  "node#512192898.1.2"
"Load.pip2196270-1"  Buses:  "node#1768617351.1.2"
"Load.pip2196270-2"  Buses:  "node#1768617351.1.2"
"Load.pip2238188-1"  Buses:  "node#1770260648.1.2"
"Load.pip2238188-2"  Buses:  "node#1770260648.1.2"
"Load.pip2239144-1"  Buses:  "node#1770361874.2.3"
"Load.pip2239144-2"  Buses:  "node#1770361874.2.3"


"""

# --- Passo 1: Extrair nomes das cargas ---
# procura Load.algumacoisa, ignorando aspas
cargas_isoladas = {
    carga.lower().replace('"', '').strip()
    for carga in re.findall(r'Load\.\S+', conteudo_txt)
}


print("Total de cargas isoladas:", len(cargas_isoladas))

# --- Passo 2: Ler o DSS e comentar as cargas isoladas ---
linhas_saida = []

with open(arquivo_dss, "r") as f:
    for linha in f:
        linha_original = linha.rstrip("\n")
        match = re.match(r'New\s+(load\.\S+)', linha_original, re.IGNORECASE)
        if match:
            nome_carga = match.group(1).lower()
            if nome_carga in cargas_isoladas:
                print("Comentando carga isolada:", nome_carga)
                linha_original = "!" + linha_original
        linhas_saida.append(linha_original)

# --- Passo 3: Salvar ---
with open(arquivo_saida, "w") as f:
    for linha in linhas_saida:
        f.write(linha + "\n")

print(f"Arquivo atualizado salvo em: {arquivo_saida}")
