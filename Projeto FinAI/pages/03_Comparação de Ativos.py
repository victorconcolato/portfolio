import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime as dt

st.markdown("# Comparação de Ativos")

ativo = st.text_input("Informe os tickers (ex: 'PETR4.SA   AAPL   TSLA')")
ativos = ativo.upper().strip()
st.caption("-> COM espaço, SEM virgulas.")
st.caption("-> Mínimo de tickers: 02 | Máximo Recomendado: 10")
lista_ativos = ativos.strip().split()
periodos = {'5 Dias':'5d','1 Mês':'1mo','3 Meses':'3mo','6 Meses':'6mo','1 Ano':'1y','2 Anos':'2y','5 Anos':'5y','10 Anos':'10y','Ano Anterior':'ytd','Máximo':'max'}

periodo = st.selectbox(f"Selecione o Período desejado", periodos.keys())

enviar = st.button('Enviar')
#Se apertar em enviar, FAÇA:
if enviar:
    if ativos:
        #Crie uma lista_erros
        lista_erros=list()    
        #Para cada item dentro da lista de ativos, FAÇA:
        for item in lista_ativos:
            #Tente:
            try:
                #Verifica se consegue achar cada item da lista e abrir um value conforme a key()
                currency = yf.Ticker(item).fast_info['currency']
            except:
                #Caso dê erro, acrescente na lista_erros. 
                lista_erros.append(item)
        #Se a lista_erros tiver conteúdo, FAÇA:        
        if lista_erros:
            #Informe os itens da lista erro numa mensagem
            st.error(f"Não consta no sistema: {', '.join(lista_erros)}")
            #Pare de rodar o streamlit
            st.stop()
        #Caso a lista de erros esteja vazia, FAÇA:
        else:
            #Crie um DF com todos os ativos informados pelo usuário
            df_hist_ativos = yf.Tickers(ativos).history(period=periodos[periodo])
            #Crie uma variavel contendo todos os valores de fechamento dos ativos
            df_fechamento = df_hist_ativos['Close']
            df_fechamento_origin=df_fechamento.copy()
            #Para cada coluna o DF, contnida nas colunas 0,1,2,3..., FAÇA:
            
            # O que eu quero é pegar o primeiro valor de cada coluna e dividir por 100
            # Para achar o primeiro valor de cada coluna
            
            #Primeiro, identifico quantas colunas tem, independente do numero de ações que o usuario digitou
            nome_colunas = list(df_fechamento.columns)
            qntd_colunas = len(nome_colunas)
            #Agora, eu vou buscar o primeiro item de CADA coluna
            #Contador =0
            
            #Para cada coluna dentro do dataframe, faça:
            for coluna in df_fechamento:
                c=0
                #Enquanto a primeira linha da coluna selecionada for NaN, FAÇA:
                while pd.isnull(df_fechamento[coluna].iloc[c]):
                    #Acrescente mais 1 no contador
                    c+=1
                #Quando sair do looping, modifique a coluna multiplicando o resultado por cada item da coluna:
                fator =(100/(df_fechamento[coluna].iloc[c]))
                df_fechamento[coluna] = df_fechamento[coluna]*fator
            
            #Gráfico de comparação
            st.subheader('Comparação entre os ativos')
            st.caption(f"{' | '.join(lista_ativos)}")
            fig = px.line(df_fechamento)
            st.plotly_chart(fig)

            #Calculo de retornos
            #Pega o ultimo valor de cada fechamento e subtrai 1.
            dict_retorno=dict()
            for coluna in df_fechamento.columns:
                retorno = float(df_fechamento[coluna].iloc[-1] - 100)
                dict_retorno[coluna]=f'{retorno:.1f}%'
            df_retorno = pd.DataFrame.from_dict(dict_retorno,orient='index',columns=['Retorno'])
            df_retorno.index.name='Tickers'
            
            st.subheader('Retornos')
            col1, col2 = st.columns(2)
            col1.dataframe(df_retorno)
            col2.line_chart(df_retorno)

            st.subheader('Resultados')
            fig1 = px.line(df_fechamento_origin)
            
            col1, col2 = st.columns(2)
            col1.dataframe(df_fechamento_origin)
            
            col2.plotly_chart(fig1)
    else:
        st.warning('Informe algum Ticker')
