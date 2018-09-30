# /index.py

'''
IMPORTANTE. ESTA DEMO NÃO POSSUI AUTENTICAÇÃO DE USUÁRIO, PORTANTO
ESTAMOS ASSUMINDO UM UNICO USUÁRIO 0 (ZERO) DA BASE DE USUÁRIOS FAKES.
POR ISSO, POR EXEMPLO, QUE EU SALVO A ÚLTIMA RECOMENDAÇÃO EM UM ARQUIVO SIMPLES. CLARO
QUE NA VERSÃO FINAL DEVE-SE USAR UM BANCO DE DADOS.
'''

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pandas as pd
import numpy as np

from surprise.dump import load

app = Flask(__name__)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        return response.query_result.fulfillment_text

def fetch_recommendations(n_lojas=3, n_ofertas=2):
    model=load('recomendacao_lojas')[1]
    lojas = pd.read_csv('lojas.csv')
    lojas['id'] = lojas.index
    ofertas_manuais = pd.read_csv('ofertas_manuais.csv')
    lojas_ids = lojas['id'].values
    ratings = []
    for i in range(0, len(lojas_ids)):
        prediction = model.predict(uid=0,iid=lojas_ids[i])
        ratings.append(prediction.est)
    lojas_escolhidas = lojas.sample(n_lojas, weights=np.array(ratings), axis=0)
    ofertas_totais = None
    for i in range(0, lojas_escolhidas.shape[0]):
        ofertas = ofertas_manuais[ofertas_manuais['lojas'] == lojas_escolhidas.iloc[[i]]['id'].values[0]]
        if ofertas.shape[0] != 0:
            if ofertas.shape[0] >= n_ofertas:
                ofertas = ofertas.sample(n_ofertas, weights='priority', axis=0)
            if ofertas_totais is None:
                ofertas_totais = ofertas
            else:
                ofertas_totais = pd.concat([ofertas_totais.reset_index(drop=True), ofertas], axis=0)
        else:
            #IMPLEMENTAR O CASO DE NÃO TER OFERTAS MANUAIS
            pass
    return lojas_escolhidas.join(ofertas_totais.set_index('lojas'), lsuffix='_lojas', rsuffix='_ofertas', on='id')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_message', methods=['POST'])
def get_message():
    data = request.get_json(silent=True)
    intent = data['queryResult']['intent']['displayName']
    if intent == 'promocoes - sem preferencia':
        #Caso o usuario simplesmente queira saber as promocoes mais indicadas
        recommendations = fetch_recommendations()
        recommendations.to_csv('ultima_recomendacao.csv', index=False)
        html_text = data['queryResult']['fulfillmentText'] + '<br><br>  '
        for i in range(0, len(recommendations)):
            loja = recommendations.iloc[[i]]['LOJA'].values[0]
            url = recommendations.iloc[[i]]['url'].values[0]
            imagem = recommendations.iloc[[i]]['imagem'].values[0]
            preco = recommendations.iloc[[i]]['preco'].values[0]
            titulo = recommendations.iloc[[i]]['titulo'].values[0]
            html_text += '<br>' + titulo + '<br><img src="https://evsarteblog.files.wordpress.com/2018/08/ursal.jpg?w=863" style="width:64px !important;height:64px !important;"/><br>R$ ' + str(round(preco,2)) + '<br>Para mais ofertas, acesse a página da loja <a href="' + url + '">aqui!</a><br>'
        
        reply = {
            "fulfillmentText": html_text,
        }
    elif intent == 'promocoes - sem preferencia - gostou':
        #Caso o usuario goste da ultima recomendacao, vamos guardar o like
        recommendations = pd.read_csv('ultima_recomendacao.csv')
        ratings = pd.read_csv('ratings.csv')
        for i in range(0, len(recommendations)):
            loja_id = recommendations.iloc[[i]]['id'].values[0]
            ratings = ratings.append(pd.DataFrame([[loja_id,0,0.5]], columns=['loja_id', 'user_id', 'like']))
        ratings.to_csv('ratings.csv', index=False)
    else:
        reply = {
            "fulfillmentText": data['queryResult']['fulfillmentText'],
        }
    return jsonify(reply)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    print(latitude)
    print(longitude)
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }

    return jsonify(response_text)

# run Flask app
if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), port='5000', debug=False, host='0.0.0.0')