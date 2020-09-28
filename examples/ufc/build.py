# https://www.kaggle.com/dgokeeffe/ufc-fight-data-refactored
#
# Cada linha do dataset representa os dados de uma luta e os dados de
# um dos lutadores dessa luta. Ou seja, há duas linhas por luta, uma
# para cada lutador, e os dados das lutas em si são redundantes mesmo.
#
# Objetivo deste código: rede em que os nós são lutadores e as arestas
# (dirigidas) representam vitórias. Existe aresta A->B se A venceu B
# em alguma luta. Como dois lutadores podem ter lutado mais de uma vez,
# vamos colocar na aresta um peso correspondente ao número de vitórias.

from csv import reader

from unidecode import unidecode


def main():

    # Cada lutador tem um id único e um nome. Vamos usar um dicionário para
    # guardar essas duas informações de uma vez (chave id, valor nome).
    names = {}

    # Cada luta tem um id único e pode ter um lutador vencedor e um lutador
    # perdedor. Vamos ignorar as lutas que foram empate ou foram anuladas.
    fights = set() # ids de lutas
    winners = {} # chave id da luta, valor id do lutador vencedor
    losers = {} # chave id da luta, valor id do lutador perdedor

    # Abre arquivo para leitura.
    with open('ufc.csv') as file:

        # Lê uma linha do arquivo e não faz nada com ela. Nem sequer joga ela
        # para uma variável. Isso é feito apenas para ignorar o cabeçalho.
        file.readline()

        # A função reader do módulo csv já faz todo o trabalho duro de quebrar
        # a linha em vírgulas, levando aspas em consideração. Não tente fazer
        # isso por conta própria para se poupar de sofrimento desnecessário.
        #
        # Vamos também usar um enumerate para saber o número da linha em cada.
        # iteração. Se o dataset estiver inconsistente, isso ajuda a saber onde.
        #
        # A contagem começa de 2 para levar em consideração o cabeçalho.
        for i, row in enumerate(reader(file), 2):

            # O id do lutador é a décima-quinta coluna (índice 14, pois
            # começa de zero). Esse é o tipo de coisa que você precisa ler
            # a documentação do dataset ou ver o CSV na mão para descobrir.
            n = row[14]

            # o nome do lutador é a décima-sétima coluna.
            name = row[16]

            # Por desencargo, vamos ver se o dataset está consistente. Se
            # o lutador já estiver no dicionário, vamos confirmar que o
            # nome desse lutador é o mesmo.
            if n in names.keys():
                if names[n] != name:
                    # Se o dataset estiver inconsistente, avisa e aborta a
                    # leitura. Em alguns casos, é fácil e talvez inevitável
                    # consertar o dataset na mão. Em outros casos, dá para
                    # ignorar o problema e considerar simplesmente o
                    # último. E em alguns casos talvez valha a pena fazer
                    # uma limpeza no valor antes de comparar.
                    #
                    # Nesse caso em particular, eu fiz uma limpeza na mão.
                    # Você pode ver o arquivo ufc-original.csv para saber
                    # como era antes da limpeza.
                    raise ValueError('Linha {}: {} != {}'.format(i, names[n], name))
            # Se o lutador não estiver no dicionário, colocamos ele.
            else:
                names[n] = name

            # O id da luta é a quarta coluna.
            fight = row[3]

            # O corner vencedor é a sexta coluna, e é "draw" se foi empate
            # e "no contest" se a luta foi anulada, então temos que ignorar
            # explicitamente esses dois casos.
            winner = row[5]
            if winner != 'draw' and winner != 'no contest':
                # Como fights é um set, não nos preocupamos com repetições.
                fights.add(fight)

                # O corner do lutador é a sétima coluna. Logo, se for igual
                # ao corner vencedor, ele venceu.
                if row[6] == winner:
                    # Se já tínhamos definido um vencedor antes para essa
                    # mesma luta, alguma coisa está errada no dataset.
                    if fight in winners.keys():
                        raise ValueError('Linha {}: mais que um vencedor'.format(i))
                    winners[fight] = n
                # Senão, ele perdeu.
                else:
                    # Se já tínhamos definido um perdedor antes para essa
                    # mesma luta, alguma coisa está errada no dataset.
                    if fight in losers.keys():
                        raise ValueError('Linha {}: mais que um perdedor'.format(i))
                    losers[fight] = n

    # A leitura do dataset acabou, então a partir de agora estamos fora
    # do primeiro with. Cuidado para não estender o escopo do with para
    # além do necessário.

    # Vamos agora usar fights, winners e losers para construir as arestas.
    # A chave do dicionário será o par vencedor-perdedor e o valor será
    # o número de vitórias.
    weights = {}
    for fight in fights:
        n = winners[fight]
        m = losers[fight]
        if (n, m) not in weights:
            weights[n, m] = 0
        weights[n, m] += 1

    # Tudo pronto! Vamos escrever o arquivo gml.

    with open('ufc.gml', 'w') as file:

        # Primeira linha, que abre os colchetes da rede.
        file.write('graph [\n')

        # Segunda linha, que indica se a rede é dirigida (1) ou não (0).
        file.write('  directed 1\n')

        # Colchetes de cada nó. Você sempre precisa colocar um id (inteiro
        # ou string) e depois pode colocar os atributos adicionais que
        # quiser, contanto que sejam inteiros, floats ou strings. Se forem
        # strings, não esqueça as aspas duplas (isso vale para o id também).
        # Não esqueça também da indentação. Ela não é necessária mas ajuda
        # a deixar mais legível.
        #
        # O módulo unidecode converte todo caractere não-ASCII para o
        # caractere ASCII mais próximo. Isso é necessário porque a
        # especificação do formato gml exige que ele seja ASCII.
        for n in names.keys():
            file.write('  node [\n')
            file.write('    id {}\n'.format(n))
            file.write('    name "{}"\n'.format(unidecode(names[n])))
            file.write('  ]\n')

        # Colchetes de cada aresta. Você sempre precisa colocar um source
        # e um target (ids de nós) e depois pode colocar os atributos
        # adicionais que quiser, contanto que sejam inteiros, floats ou
        # strings. Se forem strings, não esqueça as aspas duplas (isso
        # vale para o source e o target também). Não esqueça também da
        # indentação. Ela não é necessária mas ajuda a deixar mais legível.
        for (n, m) in weights.keys():
            file.write('  edge [\n')
            file.write('    source {}\n'.format(n))
            file.write('    target {}\n'.format(m))
            file.write('    weight {}\n'.format(weights[n, m]))
            file.write('  ]\n')

        # Última linha, que fecha os colchetes da rede.
        file.write(']\n')


if __name__ == '__main__':
    main()
