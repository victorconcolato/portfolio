acumulador_resposta_chunks={
    'id_chamada01':{'name':'obter_temperatura_atual', 'arguments':'{\"local\":\"São Paulo\",\"unidade\":\"celsius\"}'},
                            
    'id_chamada02':{'name':'obter_temperatura_atual', 'arguments':'{\"local\":\"São Paulo\",\"unidade\":\"celsius\"}'}
}

for valor in acumulador_resposta_chunks.values():
    print(valor['name'])
    argumentos_str = valor['arguments']
import json 
function_args = json.loads(argumentos_str)