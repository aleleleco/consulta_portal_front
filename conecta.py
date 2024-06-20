from flask import Flask, render_template, request, url_for
import json
import requests
from datetime import datetime

app = Flask(__name__)

configProperites = ''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/consultaCadastros')
def consultaCadastros():
    return render_template('consultaCadastros.html')

@app.route('/consultaUsuario')
def consultaUsuario():
    return render_template('consultaUsuario.html')

@app.route('/buscaDadosUsuario', methods=['POST'])
def buscaDadosUsuario():
    usuario = request.form['usuario']
    configProperites = buscaConfig()

    url = 'https://homodfe.deloitte.com.br/webservice/api/adm?action=infoUsuario'
    url += f'&login={usuario}'

    response = bucasDados(url, configProperites)

    # checa status de retorno
    if str(response.status_code) == "200":
        return render_template('buscaDadosUsuario.html', usuario=json.loads(response.text))
    else:
        return render_template('erroConsulta.html', erro=response)

@app.route('/erroConsulta')
def erroConsulta():
    return render_template('erroConsulta.html')

def bucasDados(url_consulta, config):  # texto >> consulta_municipio
    print(f'Busca dados')
    headers = {"Authorization": f"Bearer {config['acesso']['chave']}"}
    print(f'url de consulta {url_consulta}')
    print(f'header {headers}')
    response = requests.get(url_consulta, headers=headers)
    return response


def buscaConfig():
    file = 'config.json'
    with open(file, "r") as arquivo:
        config = json.load(arquivo)

    tokenGerado = config['acesso']

    if tokenGerado['chave'] == '':
        print('Necessário nova chave...')
        token = geraChave(config)
        tokenGerado['chave']=token['accessToken']
        now = datetime.now()
        tokenGerado['data_expires']=now.strftime("%d-%m-%Y")
        tokenGerado['usuario']=config['user']
    now = datetime.now()  # current date and time
    if tokenGerado['data_expires'] == now.strftime("%d-%m-%Y"):
        print('Chave atual com validade ativa...')
    else:
        print('Necessário nova chave...')
        token = geraChave(config)
        tokenGerado['chave'] = token['accessToken']
        tokenGerado['data_expires'] = now.strftime("%d-%m-%Y")
        tokenGerado['usuario'] = config['user']

        # grava dados no config para atualizar
        config['acesso'] = tokenGerado
        with open('config.json', 'w') as file:
            json.dump(config, file)
            print('config atualizado com chave')

    return config

def geraChave(config):
    url = config["url_login"]
    payload = {"nomeUsuario": config["user"], "chave": config["token"]}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    token = json.loads(r.text)
    return token

app.run(debug=True)