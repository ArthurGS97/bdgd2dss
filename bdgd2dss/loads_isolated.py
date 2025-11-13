import re

feeder = "ULAU11"  # Altere para o alimentador modelado

# --- Caminhos dos seus arquivos DSS ---
arquivo_dss = arquivo_saida = rf"{feeder}\pip_{feeder}.dss" #pip, ucbt ou ucmt

# --- Conteúdo colado diretamente (copie e cole aqui o texto do seu arquivo TXT) ---
conteudo_txt = """
        Cole aqui o conteúdo do seu arquivo TXT que lista as cargas isoladas
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
