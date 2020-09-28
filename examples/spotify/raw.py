# https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow
#
# Objetivo deste código: usar a API do Spotify sem precisar de uma biblioteca pronta.


import requests

from base64 import b64encode


# Para obter as duas informações abaixo, crie um app no dashboard
# https://developer.spotify.com/dashboard/applications
CLIENT_ID = '???'
CLIENT_SECRET = '???'

# Exemplo de id de artists. Para obter, basta procurar a
# página do artista no Spotify e copiar o id a partir da URL.
ROOT = '5M52tdBnJaKSvOpJGz8mfZ' # Black Sabbath


def main():
    # Body do request. Segundo a documentação (ver link da linha 1), deve
    # ter um dicionário com o conteúdo abaixo, especificamente no formato
    # application/x-www-form-urlencoded. Esse é o formato padrão do
    # requests, então é só passar o dicionário como o parâmetro data
    # (ver linha 51) que vai magicamente funcionar.
    data = {
        'grant_type': 'client_credentials',
    }

    # Credenciais para pedir token. Segundo a documentação (ver link da
    # linha 1), deve ser o client ID e o cliente secret separados por
    # um dois pontos (:).
    credentials = '{}:{}'.format(CLIENT_ID, CLIENT_SECRET)

    # Ainda segundo a documentação, as credenciais devem ser codificadas
    # pelo método base64. Há um módulo padrão do Python que faz isso (veja
    # os imports deste código), mas ele recebe e devolve bytes, não strings.
    # É por causa disso que precisamos do encode() e do decode() abaixo.
    credentials64 = b64encode(credentials.encode()).decode()

    # Headers do request. Segundo a documentação (ver link da linha 1),
    # deve ter o conteúdo abaixo. Headers é sempre um dicionário. Diferente
    # do body, você não precisa se preocupar com qual é o formato.
    headers = {
        'Authorization': 'Basic ' + credentials64,
    }

    # Faz o request do access token e pega a resposta em JSON. Não é
    # toda API que dá respostas em JSON! Estamos seguros em fazer isso
    # porque sabemos que isso é verdade em relação à API do Spotify.
    response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    data = response.json()

    # Se o request deu errado, isso pode ser verificado pelo status code.
    if response.status_code != 200:
        print(data)
        return

    # Se o request deu certo, a documentação (ver link da linha 1) diz
    # que o token de acesso está na chave access_token da resposta.
    token = data['access_token']

    # Agora estamos prontos para usar a API! Vamos por exemplo, usar:
    # https://developer.spotify.com/documentation/web-api/reference/artists/get-artist/

    # Headers do request. Segundo a documentação (ver link da linha 1),
    # deve ter o conteúdo abaixo. Headers é sempre um dicionário. Diferente
    # do body, você não precisa se preocupar com qual é o formato.
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    # Faz o request do artists e pega a resposta em JSON. Não é
    # toda API que dá respostas em JSON! Estamos seguros em fazer isso
    # porque sabemos que isso é verdade em relação à API do Spotify.
    response = requests.get('https://api.spotify.com/v1/artists/' + ROOT, headers=headers)
    data = response.json()

    # Vamos ver se deu tudo certo...
    print(data)


if __name__ == '__main__':
    main()
