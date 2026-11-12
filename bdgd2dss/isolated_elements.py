import re

feeder = "P045RNE"

arq_dss_ucbt = rf"{feeder}\ucbt_{feeder}.dss" 
arq_dss_ucmt = rf"{feeder}\ucmt_{feeder}.dss"
arq_dss_pip = rf"{feeder}\pip_{feeder}.dss"
arq_dss_ramlig = rf"{feeder}\ramlig_{feeder}.dss"
arq_dss_ssdBT = rf"{feeder}\ssdBT_{feeder}.dss"
arq_dss_ssdMT = rf"{feeder}\ssdMT_{feeder}.dss"
arq_dss_chc = rf"{feeder}\chavesMTBT_{feeder}.dss"

arq_isolated = rf"{feeder}\{feeder}_Isolated.txt"

with open(arq_isolated, "r", encoding="utf-8") as f:
    texto = f.read()

match = re.search(
    r'THE FOLLOWING SUB NETWORKS ARE ISOLATED \*+\s*(.*?)\s*\*\*\*\s+THE FOLLOWING BUSES ARE NOT CONNECTED',
    texto,
    re.DOTALL | re.IGNORECASE
)

conteudo_txt = match.group(1) if match else ""

# --- Extrai cargas ---
todas_cargas = [
    carga.lower().strip()
    for carga in re.findall(r'Load\.\S+', conteudo_txt, re.IGNORECASE)
]

# --- Extrai linhas de ramais de ligação, linhas bt e chaves --- 
todas_linhas = [
    carga.lower().strip()
    for carga in re.findall(r'Line\.\S+', conteudo_txt, re.IGNORECASE)
]


cargas_pip = {c for c in todas_cargas if c.startswith("load.pip")}
cargas_bt  = {c for c in todas_cargas if c.startswith("load.bt")}
cargas_mt  = {c for c in todas_cargas if c.startswith("load.mt")}
ramlig = {c for c in todas_linhas if c.startswith("line.ram")}
linhas_bt = {c for c in todas_linhas if c.startswith("line.bt")}
linhas_mt = {c for c in todas_linhas if c.startswith("line.mt")}
chaves = {c for c in todas_linhas if c.startswith("line.sec")}

def comentar_elementos(arq_dss, conjunto_elementos, tipo_elemento, descricao="elementos"):
    linhas_saida = []
    padrao = rf'\s*New\s+({tipo_elemento}\.\S+)'

    with open(arq_dss, "r") as f:
        for linha in f:
            linha_original = linha.rstrip("\n")

            match = re.match(padrao, linha_original, re.IGNORECASE)

            if match:
                nome_elemento = match.group(1).lower()

                if nome_elemento in conjunto_elementos:
                    #print(f"[{arq_dss}] Comentando:", nome_elemento)
                    linha_original = "!" + linha_original

            linhas_saida.append(linha_original)

    with open(arq_dss, "w") as f:
        for linha in linhas_saida:
            f.write(linha + "\n")
    print(f"Arquivo atualizado: {arq_dss} - {len(conjunto_elementos)} {descricao}")


# --- Processamento de cada tipo ---
comentar_elementos(arq_dss_ucmt, cargas_mt, "load", "cargas MT\n")
comentar_elementos(arq_dss_ucbt, cargas_bt, "load", "cargas BT\n")
comentar_elementos(arq_dss_pip, cargas_pip, "load", "cargas PIP\n")
comentar_elementos(arq_dss_ramlig, ramlig, "line", "ramais de ligação\n")
comentar_elementos(arq_dss_ssdBT, linhas_bt, "line", "linhas SSDBT\n")
comentar_elementos(arq_dss_ssdMT, linhas_mt, "line", "linhas SSDMT\n")
comentar_elementos(arq_dss_chc, chaves, "line", "chaves\n")