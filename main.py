import bdgd2dss as b2d
import time

################################################## DADOS DE ENTRADA ##################################################
mvasc3 = 227.8  # potência de curto-circuito trifásico, se quiser utilizar o padrão do OpenDSS, deixar 0
mvasc1 = 234.9  # potência de curto-circuito monofásico, se quiser utilizar o padrão do OpenDSS, deixar 0
######################################################################################################################

if __name__ == "__main__":
    start_total = time.time()

    # Chamando a função para obter a lista de alimentadores disponíveis nessa BDGD
    feeders_all = b2d.feeders_list()
    print(f"Alimentadores disponíveis: {feeders_all}") # Exibe a lista de alimentadores disponíveis na BDGD
    
    # Escolhe os alimentadores que deseja simular, pode ser apenas um, vários ou todos, no formato especificado
    #feeders = ['51696837', '51696838']

    # Chamando a função para modelar os alimentadores escolhidos usando processamento paralelo
    #b2d.feeders_modelling(feeders, mvasc3, mvasc1)

    # Chamando a função para verificar a viabilidade dos alimentadores
    #b2d.feeders_feasibility(feeders)

    end_total = time.time()
    print(f"\nTempo total: {end_total - start_total} s") # Exibe o tempo total de execução do script

