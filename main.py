import bdgd2dss as b2d
import time


if __name__ == "__main__":
    start_total = time.time()

    # Chamando a função para obter a lista de alimentadores disponíveis nessa BDGD
    feeders_all = b2d.feeders_list()
    #print(f"Alimentadores disponíveis: {feeders_all}") # Exibe a lista de alimentadores disponíveis na BDGD
    
    # Escolhe os alimentadores que deseja simular, pode ser apenas um, vários ou todos, no formato especificado
    feeders = ['ULAU11', 'ULAE714', 'ULAD202', 'ULAD203']  # Exemplo de alimentadores escolhidos
    # Chamando a função para modelar os alimentadores escolhidos usando processamento paralelo
    b2d.feeders_modelling(feeders)


    end_total = time.time()
    print(f"\nTempo total: {end_total - start_total} s") # Exibe o tempo total de execução do script

