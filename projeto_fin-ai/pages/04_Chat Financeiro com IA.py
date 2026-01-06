import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

#Carregando o env que tem na pasta que está meu arquivo
load_dotenv()
#Utilizando minha key da OpenAI que está dentro do meu .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
#Chamando de cliente a minha chamada à OpenaAI
client = OpenAI(api_key=OPENAI_API_KEY)


#Funções Auxiliares

def atualiza_container():
    # Garantimos que o container 'caixa' seja limpo
    caixa.empty()
    
    # Dentro do container caixa, FAÇA:
    with caixa:
        # Para cada item dentro do histórico, FAÇA:
        for item in historico:
            if item['role'] == 'user':
                st.write(f"**Usuário:** {item['content']}")
            elif item['role'] == 'assistant':
                st.write(f"**Assistente:** {item['content']}")

def ajuste_data_brasil(data):
    if "/" in data:
        lista_data = data.split("/")
    elif '-' in data:
        lista_data = data.split("-")
    else:
        ValueError('Formato de data inválido')
    dia_data = lista_data[0]
    mes_data = lista_data[1]
    ano_data = lista_data[2]

    if len(dia_data)<2:
        dia_data = '0'+dia_data
    if len(mes_data)<2:
        mes_data = '0'+mes_data
    if len(ano_data)<4 and int(ano_data)>30:
        ano_data = '19'+ano_data
    elif len(ano_data)<4 and int(ano_data)<30:
        ano_data='20'+ano_data

    return ano_data+'-'+mes_data+'-'+dia_data

def acrescentar_datas(data):
    data_nova = ajuste_data_brasil(data)
    formato_data = datetime.strptime(data_nova,"%Y-%m-%d")
    nova_data = formato_data + timedelta(days=1)
    return nova_data.strftime('%Y-%m-%d')

#--------------------------------------------

#Funções para IA:

def buscar_preco_atual(ticker):
    t = yf.Ticker(ticker)
    info = t.fast_info
    preco = info.get('lastPrice') or info.get("last_price")

    return {
        "ticker":ticker,
        "preco": preco,
        "moeda": info.get('currency','USD')}

#--------------------------------------------

def buscar_preco_historico_unico(ticker, data):
    t = yf.Ticker(ticker)
    
    data_inicio_formatada = ajuste_data_brasil(data)
    data_fim_formatada = acrescentar_datas(data_inicio_formatada)
    preco_historico = t.history(start=data_inicio_formatada, end=data_fim_formatada)
    
    if preco_historico.empty:
        return 'Na data informada, não há registro de valores.'
    else:
        return preco_historico['Close']
    
#--------------------------------------------
def variacao_percentual_ticker(ticker,inicio, fim):

    t=yf.Ticker(ticker)
    data_inicio_formatado = ajuste_data_brasil(inicio)
    data_fim_formatado = ajuste_data_brasil(fim)

    df_ticker = t.history(start = data_inicio_formatado, end = data_fim_formatado)
    
    if df_ticker.empty:
        return 'Não há dados para o período informado'
    else:
        variacao_inicial =df_ticker['Close'].iloc[0] 
        variacao_final=df_ticker['Close'].iloc[-1]
        return f'{((variacao_final-variacao_inicial)/variacao_inicial)*100:.2f} %'


#Criando uma variavel chamada Tools. Nela, constará todas as minhas funções

tools = [
    {
        "type": "function",
        "name": "buscar_preco_atual",
        "description": "Busca e retorna o preço atual de um determinado ticker da bolsa de valores",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Uma espécie de sigla que é vinculada a uma empresa cadastrada na bolsa de valores",
                },
            },
            "required": ["ticker"],
        },
    },
]
#Criando a memória da IA
if 'lista_mensagens' not in st.session_state:
    st.session_state['lista_mensagens']=list()
lista_mensagens = st.session_state['lista_mensagens']
#-------------------------------------------------Início do código-----------------------------------------------------
#Título
st.markdown("# Chat Financeiro com IA")

caixa = st.container(border=True,height=300)

#Criação de uma sessão que gravará todos os dados da conversa.
if 'historico' not in st.session_state:
    st.session_state['historico']=list()
#Chamando minha session_state de historico
historico = st.session_state['historico']

#Cria o conteiner onde estará toda a conversa
atualiza_container()

#Primeiro, o usuário irá enviar uma pergunta
input_usuario = st.chat_input('Faça sua pergunta: ') 

#Se apertar o botão 'enviar' e o conteúdo do input não estiver vazio, FAÇA:
if input_usuario:
    #Entra para o histórico. O histórico é o conteudo que será exibido para o usuário.
    historico.append({'role':'user', 'content': input_usuario})
    #Variavel contendo o conteudo do usuario
    lista_mensagens.append({'role':'user', 'content': input_usuario})

    with caixa:
        caixa.empty()

        # Adiciona o placeholder para a resposta do assistente (que virá em seguida)
        st.write(f"**Assistente:** ")
        assistant_placeholder = st.empty() # Placeholder para a resposta da IA

    
    
    #Defina qual será a resposta da API
    response = client.responses.create(model="gpt-5-nano-2025-08-07",   #Este é o modelo que irá usar
                tools=tools, #Aqui estão as funções que poderá usar
                input=lista_mensagens) #Aqui está o histórico da conversa em um formato que você consegue entender.
    
    #Construção da resposta caso seja usada por Tools
    #Vou iterar em cima da resposta da IA
    function_call = False
    resposta_final=""


        #Aqui, estou pegando a classe que eu quero, ou seja, a classe que usa Function_call
    if any((item.type == 'function_call' for item in response.output)):
        function_call = True

        for item in response.output:
            if item.type=='function_call':
                lista_mensagens.append({
                    'type':'function_call',
                    'call_id':item.call_id,
                    'name':item.name,
                    'arguments':item.arguments})
            #Aqui, estou verificando qual é a função que a IA achou necessária usar.
                if item.name == 'buscar_preco_atual':
                #Caso a ia tenha identificado a funçao, aqui, eu farei o chamamento da função, normalmente
                    ticket_acao = json.loads(item.arguments)['ticker']
                
                    #Essa variável foi criada pois, no append logo abaixo, é necessário que tenha somente resultados, NUNCA utiilização de funções
                    buscar_preco = buscar_preco_atual(ticket_acao)
                    #Adicionando à memória da IA a chamada da funçao
                    lista_mensagens.append({
                        "type": "function_call_output", #IA, aqui está o resultado da função que você pediu
                        "call_id": item.call_id, #Liga o chamamento desta IA à resposta anterior dela(aquele response.output)
                        "output": json.dumps(buscar_preco)})
                    #Este append existe para fazer uma segunda solicitação à IA. Assim, ela vai ter um pedido no histórico dela
                    lista_mensagens.append({
                        "role": "assistant",
                        "content": "Use o resultado da função acima para responder ao usuário com uma mensagem formatada, bonita e completa, porém curta."})
            
    
        response2 = client.responses.create(model="gpt-5-nano-2025-08-07", input=lista_mensagens)
        
        for item in response2.output:
            if item.type =='message':
                resposta_final = item.content[0].text
                break
            
    #Caso a IA não use Função
    else:
        for item in response.output:
            if item.type == 'message':
                resposta_final = item.content[0].text
                break
    #Caso tenha conteudo em resposta_final, acrescente:
    if resposta_final:
        historico.append({'role':'assistant', 'content':resposta_final})
        lista_mensagens.append({'role':'assistant', 'content':resposta_final})
        
        #Atualização da caixa
        caixa.empty()
        atualiza_container()