from pprint import pprint
import dotenv
import os
import requests
from requests.auth import HTTPBasicAuth

dotenv.load_dotenv()
cliente_id = os.environ['SPOTIFY_CLIENT_ID']
cliente_secret = os.environ['SPOTIFY_CLIENT_SECRET']

http_auth = HTTPBasicAuth(cliente_id, cliente_secret)

url ='https://accounts.spotify.com/api/token'

body = {
    'grant_type': 'client_credentials'
}

resposta = requests.post(url, data=body, auth=http_auth)

try:
    resposta.raise_for_status()
except requests.HTTPError as e:
    print(f'Erro no request {e}')
    resultado = None
else:
    resultado = resposta.json()

token = resultado['access_token']

id_artista ='1on7ZQ2pvgeQF4vmIA09x5'
url = f'https://api.spotify.com/v1/artists/{id_artista}'
headers = {
    'Authorization': f'Bearer {resultado["access_token"]}'
}

resposta=requests.get(url, headers=headers)

pprint(resposta.json())