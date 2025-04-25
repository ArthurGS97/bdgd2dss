import bdgd2dss as b2d
import time

################################################## DADOS DE ENTRADA ##################################################
pref = "CEMIG-D_4950_2022-12-31_V11_20230920-1643.gdb" #Nome do arquivo de entrada, da BDGD
mvasc3 = 227.8  # potência de curto-circuito trifásico, se quiser utilizar o padrão do OpenDSS, deixar 0
mvasc1 = 234.9  # potência de curto-circuito monofásico, se quiser utilizar o padrão do OpenDSS, deixar 0
######################################################################################################################

if __name__ == "__main__":
    start_total = time.time()

    # Chamando a função para obter a lista de alimentadores disponíveis nessa BDGD
    feeders_all = b2d.feeders_list(pref)
    # Escolhe os alimentadores que deseja simular, pode ser apenas um, vários ou todos
    feeders = ['ULAU15', 'ULAD215']

    # Chamando a função para modelar os alimentadores escolhidos usando processamento paralelo
    b2d.feeders_modelling(feeders, pref, mvasc3, mvasc1)

    # Chamando a função para verificar a viabilidade dos alimentadores
    #b2d.feeders_feasibility(feeders, pref)

    end_total = time.time()
    print(f"\nTempo total: {end_total - start_total} s") # Exibe o tempo total de execução do script

