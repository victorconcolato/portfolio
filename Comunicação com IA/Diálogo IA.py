from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import streamlit as st
import json

#CHAMANDO A API DA OPENAI
load_dotenv() # Carrega as variáveis do arquivo .env

openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("A chave da API não foi encontrada no arquivo .env.")
    
client = OpenAI(api_key=openai_api_key)

#---------------------------------------------------------------------
#Função para obter temperatura de algum local

def obter_temperatura_atual(local, unidade='celsius'):
    if 'são paulo' in local.lower():
        return json.dumps(
            {'local': 'São Paulo','temperatura':'32','unidade':unidade})
    if 'porto alegre' in local.lower():
        return json.dumps({'local': 'porto alegre','temperatura':'28','unidade':unidade}) 

#Criação de uma Tools(lista de dicionários)
tools = [
    {
    'type':'function', #Tipo da ferramenta
    'function':{#Aviso que é uma função
        'name':'obter_temperatura_atual', #Qual o nome da função, importante ter a ver com o objetivo
        'description':'Serve para informar a temperatura do local, conforme a pergunta realizada.', #Descrição melhor
        'parameters': { #Quais são os parâmetros que serão passados?
            'type':'object',#Tipo do parâmetro
            'properties':{#Aqui você vai colocar o nome dos parâmetros. No caso, local e unidade
                'local':{
                    'type':'string',#Tipo do parâmetro
                    'description':'O nome da cidade. Ex: São Paulo', #Descrição do parâmetro
                },
                'unidade':{#Aqui você vai colocar o nome dos parâmetros. No caso, local e unidade
                    'type':'string',#Tipo do parâmetro
                    'enum':['celsius','fahrenheit']#Aqui diz: Só pode ser celsius ou fahrenheit(Por causa do enam)
                },
            },
            'required':['local'],#Qual eu preciso, obrigatoriamente, informar.
}
}
}
]

funcoes_disponiveis ={'obter_temperatura_atual':obter_temperatura_atual}


# #EXEMPLO DE UMA CHAMADA PARA A OPENAI COM STREAM FUNCIONANDO:
# mensagens=list()
# pergunta = 'Qual a temperatura de São Paulo?'
# mensagens.append({'role':'user','content':f'{pergunta}'})
# resposta = client.chat.completions.create(
# messages=mensagens,
# model='gpt-4o-mini-2024-07-18',
# max_tokens=30,
# temperature=0,
# stream=True,
# tools=tools,#Modelo, as suas ferramentas são as que eu decidi lá em cima, caso queira usá-las.
# tool_choice='auto'#Decida automaticamente.
# )

# # print(resposta.choices[0].message.tool_calls) #content)
# for pedaco in resposta:
#     if pedaco.choices[0].delta.content != None:
#         print(pedaco.choices[0].delta.content, end="", flush=True)


# ------------------------------------------------------------------------





#Criação de uma função:
#lista chamada mensagens para incluir os arquivos json da conversa.
mensagens = [
    {
        "role": "system",
        "content": (
            "Você possui uma função fictícia chamada obter_temperatura_atual. "
            "Ela não usa dados reais e serve apenas para simular temperaturas. "
            "Sempre que o usuário perguntar sobre clima, temperatura, calor, frio "
            "ou condições meteorológicas de uma cidade, você DEVE chamar essa função "
            "em vez de responder diretamente."
        )
    }
]

def geracao_textos(pergunta):    

    #Coloca a pergunta no histórico
    mensagens.append({'role':'user','content':f'{pergunta}'})
    
    #Coração do código. Ele vai buscar na OpenAI a resposta
    resposta = client.chat.completions.create(
    messages=mensagens,
    model='gpt-4o-mini-2024-07-18',
    max_tokens=100, #Quantidade de Tokens
    temperature=0, #0 = Pouco criativo, 2 = Provavelmente alucina
    stream=True, #Enviando as mensagens separadas por chunks
    tools=tools, #Aqui, o tools é igual ao dicionario criado anteriormente(tools tbm) contendo alguma função 
    tool_choice='auto'#Aqui serve para a IA decidir sozinha se deve usar a função ou não
    )
    resposta_ia = "" #Aqui é uma variavel em string para somar os chunks e incluí-los todos aqui. Precisa ser criado antes do for para que o resultado de cada chunk seja adicionado
    
    #Aqui é só para deixar estilizada a conversa
    print('Assistente: ', end="")

    #Preciso criar um acumulador por causa do stream, se não, ele só vai exibir o primeiro chunk então:
    #Eu vou acumular todos os chunks para depois exibí-los.
    acumulador_resposta_chunks = {}

    #Para cada conteudo na lista resposta, faça:
    for pedaco in resposta:
        #Se tiver conteudo na lista de resposta originada sem o tools, FAÇA:
        if pedaco.choices[0].delta.content: #Esse 'caminho' contém as respostas que não vieram de tools
            texto = pedaco.choices[0].delta.content #Criei uma variavel para ficar mais bonitinho
            print(texto, end="",flush=True) #Mandei printar
            resposta_ia += texto #Acrescentei os chunks à variavel resposta_ia
             
        


        #Se tiver conteudo na lista de resposta originada com o uso do tools, FAÇA:
        if pedaco.choices[0].delta.tool_calls:

            #Crie uma variável para ficar mais legível
            chamada_funcao = pedaco.choices[0].delta.tool_calls
            #Para cara trecho dentro da lista que contém todas as chamadas da função, faça:
            for chamada in chamada_funcao:#Estou iterando pois há 2 identificadore de chamadas no código todo. Poderiam haver infinitos.
                #Aqui, eu to chamando de nome_funcao o nome da função, ou seja: nome_chamada=obter_temperatura_atual
                num_chamada_funcao = chamada.id
                #Se obter_temperatura_atual não estiver dentro do dicionário chamado acumulador_resposta_chunks, FAÇA:
                if num_chamada_funcao not in acumulador_resposta_chunks:
                    #To criando uma chave com os valores dentro do dicionario acumulador_resposta_chunks
                    #o resultado será: {obter_temperatura_atual:{name:'',arguments:''}}
                    #Ou seja, será criado um dicionário com duas chaves, ambas, vazias.
                    acumulador_resposta_chunks[num_chamada_funcao] = {'name':'','arguments' : ''}
                #Se chamada.function.name tiver algum conteúdo, FAÇA:
                if chamada.function.name:
                    #Acrescente na key'name' o conteudo chamada.function.name
                    #Ele está usando += pois, não se esqueça, está havendo uma iteração
                    #Pois o stream manda por chunks, então, precisa juntar tudo.
                    acumulador_resposta_chunks[num_chamada_funcao]['name'] +=chamada.function.name
                #Se chamada.function.arguments tiver algum conteúdo, FAÇA:
                if chamada.function.arguments is not None and chamada.function.arguments.strip() != "":
                    #Acrescente na key 'arguments', o conteudo de chamada.function.arguments
                    #Ele está usando += pois, não se esqueça, está havendo uma iteração
                    #Pois o stream manda por chunks, então, precisa juntar tudo.
                    acumulador_resposta_chunks[num_chamada_funcao]['arguments']+=chamada.function.arguments
                
                #O resultado ficou: ex: acumulador_resposta_chunks={'id_chamada01':{'name':'obter_temperatura_atual', 'arguments':'{\"local\":\"São Paulo\",\"unidade\":\"celsius\"}'}
                # ,
                # 'id_chamada02':{'name':'obter_temperatura_atual', 'arguments':'{\"local\":\"São Paulo\",\"unidade\":\"celsius\"}'}
            #O break é exigido pois só assim o conteudo de resposta poderá ser finalizado
            break

        #Com isso, se o acumulador_resposta_chunks tiver algum conteúdo, FAÇA:    
    if acumulador_resposta_chunks:
        #Para cada id : dicionario em acumulador_resposta_chunks.items(), FAÇA:
        for chave, dicionario_interno in acumulador_resposta_chunks.items():# Aqui precisa ser items() pois a chave será usada posteriormente
            #Aqui é só criar as variaveis.
            
            nome_funcao = dicionario_interno['name'] 
            #arg_funcao_em_str = '{cidade:São Paulo, unidade:celsius}'
            arg_funcao_em_str = dicionario_interno['arguments']

            if arg_funcao_em_str.strip() == "":
                continue  # ainda não terminou de chegar, pula


            #Transforma arg_funcao_em_str, que era uma string, em dicionário.
            arg_funcao_em_dict = json.loads(arg_funcao_em_str)

            #Aqui ele buscou lá no dicionario 'funcoes_disponiveis' o valor relacionado a obter_temperatura_atual.
            #Isso acontece pq a IA só entende texto, então, eu preciso criar uma variavel associada a um dicionario.
            #Neste dicionario, deve conter o texto que a IA vai entender, vinculado a função que ela deverá utilizar.
            funcao_chamada = funcoes_disponiveis[nome_funcao] 
            
            resposta_funcao = funcao_chamada(
            # Estes são os parâmetros que estão sendo relacionados à função. Ex: obter_temperatura_local(local, unidade)
            local=arg_funcao_em_dict.get('local'), #o get é a mesma coisa que dicionario['local']. Mas, o codigo não quebra se o retorno for vazio
            unidade=arg_funcao_em_dict.get('unidade'))#o get é a mesma coisa que dicionario['unidade']. Mas, o codigo não quebra se o retorno for vazio
            
            

            #Aqui vai adicionar a resposta da função à memória da IA
            mensagens.append(
            {"tool_call_id":chave, #Só para dizer qual id do too_call
            'role':'tool',#Assim o modelo já sabe que é uma função e não um usuário
            'name':nome_funcao, #Nome da função
            'content':resposta_funcao}) #Resposta da função
        
        #Aqui, é a criação da variavel contendo a resposta dela junto da resposta da função
        resposta_final = client.chat.completions.create(
            messages=mensagens,
            model="gpt-4o-mini-2024-07-18"
        )
        print("\n" + resposta_final.choices[0].message.content)
        return 
    if not acumulador_resposta_chunks:
        mensagens.append({'role':'assistant', 'content': resposta_ia})


while True:
    pergunta=input('Pergunte o que quiser: ')
    if pergunta =='fim':
        break
    else:
        geracao_textos(pergunta)