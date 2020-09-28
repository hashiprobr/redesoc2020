# https://www.gharchive.org/
#
# https://data.gharchive.org/2020-09-26-0.json.gz
#
# O dataset representa todos os eventos (pulls, pushs, etc.) que
# aconteceram no GitHub em determinado período.
#
# Objetivo deste código: rede two-mode em que os nós são usuários
# e repositórios e existe aresta A-B se A fez push em B.

import json

from unidecode import unidecode


def main():
    nodes = set()
    edges = set()

    with open('github.json') as file:

        # Poderíamos carregar o arquivo inteiro usando json.load,
        # mas isso provavelmente estouraria a memória. Os criadores
        # do GH Archive sabem disso e formataram o arquivo de modo
        # que cada linha dele é um JSON valido por si só. Então
        # vamos ler o arquivo linha por linha.
        for line in file:
            data = json.loads(line)

            # Vamos ignorar todos os eventos que não são pushs.
            # Para descobrir o que esperar das chaves e valores,
            # é necessário ler a documentação ou ver o JSON na mão.
            if data['type'] == 'PushEvent':

                # Vamos pegar o nome do usuário. Como esse nome é
                # único no GitHub inteiro, serve como identificador.
                n = data['actor']['login']

                # Vamos ignorar todos os pushs feitos por bots.
                if not n.endswith('[bot]'):

                    # Vamos pegar o nome do repositório. Como esse
                    # nome é único no GitHub inteiro, serve como id.
                    m = data['repo']['name']

                    # Como nodes e edges são sets, não precisamos
                    # nos preocupar com repetições. Uma alternativa
                    # seria transformar repetições em pesos.
                    nodes.add(n)
                    nodes.add(m)
                    edges.add((n, m))

    # Tudo pronto! Vamos escrever o arquivo gml.

    with open('github2.gml', 'w') as file:

        # Primeira linha, que abre os colchetes da rede.
        file.write('graph [\n')

        # Segunda linha, que indica se a rede é dirigida (1) ou não (0).
        file.write('  directed 0\n')

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
        for n in nodes:
            file.write('  node [\n')
            file.write('    id "{}"\n'.format(unidecode(n)))
            file.write('  ]\n')

        # Colchetes de cada aresta. Você sempre precisa colocar um source
        # e um target (ids de nós) e depois pode colocar os atributos
        # adicionais que quiser, contanto que sejam inteiros, floats ou
        # strings. Se forem strings, não esqueça as aspas duplas (isso
        # vale para o source e o target também). Não esqueça também da
        # indentação. Ela não é necessária mas ajuda a deixar mais legível.
        #
        # O módulo unidecode converte todo caractere não-ASCII para o
        # caractere ASCII mais próximo. Isso é necessário porque a
        # especificação do formato gml exige que ele seja ASCII.
        for (n, m) in edges:
            file.write('  edge [\n')
            file.write('    source "{}"\n'.format(unidecode(n)))
            file.write('    target "{}"\n'.format(unidecode(m)))
            file.write('  ]\n')

        # Última linha, que fecha os colchetes da rede.
        file.write(']\n')


if __name__ == '__main__':
    main()
