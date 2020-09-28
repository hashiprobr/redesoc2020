# https://spotipy.readthedocs.io/
#
# Objetivo deste código: nós são artistas e arestas são baseadas
# na API de "related artists". Como não há tempo de baixar todos
# os artistas do Spotify inteiro, partimos de uma "raiz" inicial
# e fazemos uma "bola de neve" a partir dessa raiz com recursão.
# Ou seja, pegamos a raiz (0 níveis), os vizinhos da raiz (1 nível),
# os vizinhos dos vizinhos da raiz (2 níveis) e assim em diante.


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from unidecode import unidecode


# Para obter as duas informações abaixo, crie um app no dashboard
# https://developer.spotify.com/dashboard/applications
CLIENT_ID = '???'
CLIENT_SECRET = '???'

# Nó inicial da "bola de neve". Para obter, basta procurar a
# página do artista no Spotify e copiar o id a partir da URL.
ROOT = '5M52tdBnJaKSvOpJGz8mfZ' # Black Sabbath

# Níveis da "bola de neve".
LEVELS = 2


# Função recursiva que faz uma "bola de neve" a partir de um
# nó inicial n. O parâmetro levels determina quantos níveis
# de "bola de neve" queremos a partir de n.
#
# Essa função atualiza o dicionário names, que associa ids
# de artistas a nomes, e o dicionário neighbors, que associa
# ids de artistas a listas de outros ids de artistas de
# acordo com o "related artists" do Spotify.
#
# O objeto sp representa a API do Spotify. Veja a função
# main para mais detalhes sobre como construir esse objeto.
def snowball(sp, names, neighbors, n, levels):

    # Se ainda não sabemos o nome de n, usamos a API para
    # descobrir. Para entender o formato de entrada e saída
    # de cada endpoint da API, é necessário ver a documentação.
    if n not in names.keys():
        artist = sp.artist(n)
        names[n] = artist['name']

    # Como o processo é longo, vamos colocar alguns prints.
    # e indentar de acordo com o nível da recursão, como
    # vocês viram em Desafios.
    print((LEVELS - levels) * '  ' + names[n])

    # Base da recursão: se levels for zero, interrompemos o
    # processo da "bola de neve".
    if levels == 0:
        return

    # Se ainda não sabemos os related artists de n, usamos a
    # API para descobrir. Para entender o formato de entrada
    # e saída de cada endpoint da API, é necessário ver a
    # documentação.
    if n not in neighbors.keys():
        related = sp.artist_related_artists(n)
        neighbors[n] = [artist['id'] for artist in related['artists']]

    # Passo da recursão: continuamos a "bola de neve" para
    # cada um dos related artists, mas com levels reduzido.
    for m in neighbors[n]:
        snowball(sp, names, neighbors, m, levels - 1)


def main():
    # Constrói o objeto que representa a API.
    auth_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Inicializa names e neighbors como dicionários vazios.
    # Se você ainda lembra de Desafios, isso é essencialmente
    # uma memoização: guardamos as respostas já calculadas
    # para evitar o desperdício de chamadas de API. É muito
    # importante fazer isso por causa de rate limits.
    names = {}
    neighbors = {}

    # Inicia a "bola de neve" a partir da raiz. Quando ela
    # terminar, names e neighbors vão estar preenchidos.
    snowball(sp, names, neighbors, ROOT, LEVELS)

    # Tudo pronto! Vamos escrever o arquivo gml.

    with open('spotify.gml', 'w') as file:
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
            file.write('    id "{}"\n'.format(n))
            file.write('    name "{}"\n'.format(unidecode(names[n])))
            file.write('  ]\n')

        # Colchetes de cada aresta. Você sempre precisa colocar um source
        # e um target (ids de nós) e depois pode colocar os atributos
        # adicionais que quiser, contanto que sejam inteiros, floats ou
        # strings. Se forem strings, não esqueça as aspas duplas (isso
        # vale para o source e o target também). Não esqueça também da
        # indentação. Ela não é necessária mas ajuda a deixar mais legível.
        for n in neighbors.keys():
            for m in neighbors[n]:
                file.write('  edge [\n')
                file.write('    source "{}"\n'.format(n))
                file.write('    target "{}"\n'.format(m))
                file.write('  ]\n')

        # Última linha, que fecha os colchetes da rede.
        file.write(']\n')


if __name__ == '__main__':
    main()
