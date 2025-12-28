import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

st.markdown('# Consulta de Ativos')

acao = st.text_input('Informe o ticker do ativo (ex: PETR4.SA, AAPL, TSLA)')
periodos = {'1 Dia':'1d','5 Dias':'5d','1 Mês':'1mo','3 Meses':'3mo','6 Meses':'6mo','1 Ano':'1y','2 Anos':'2y','5 Anos':'5y','10 Anos':'10y','Ano Anterior':'ytd','Máximo':'max'}

periodo = st.selectbox('Selecione o período',periodos)

if st.button('Consultar'):
    if acao:
        df_ticket = yf.Ticker(f"{acao}").history(period=f"{periodos[periodo]}")
        if df_ticket.empty:
            st.warning('Empresa Não Encontrada')
            st.stop()
        else:
            ticket = yf.Ticker(f"{acao}")    
            info_ticker = ticket.get_info()
            st.write(f"Você pesquisou: {acao.upper()} - {info_ticker.get('shortName')}")
            st.divider()
            #Informações Básicas
            st.text(f"Nome da Empresa: {info_ticker.get('shortName')}")
            st.text(f"Endereço: {info_ticker.get('address1')}")
            st.text(f"Cidade: {info_ticker.get('city')}")
            st.text(f"País: {info_ticker.get('country')}")
            st.text(f"Site: {info_ticker.get('website')}")
            st.text(f"Setor: {info_ticker.get('sector')}")
            st.text(f"Total de Funcionários: {info_ticker.get('fullTimeEmployees')}")
            
            officers = info_ticker.get('companyOfficers')
            if officers and len(officers)>0 and officers[0].get('name'):
                st.text(f"CEO: {officers[0]['name']}")
            st.divider()
            #valor atual
            fast = ticket.get_fast_info()
            if fast and fast.get('lastPrice'):
                st.markdown("### Valor Atual ")
                valor_atual = fast.get('lastPrice')
                valor_atual_str = f"{valor_atual:.2f}"
                st.markdown(f"#### USD {valor_atual:.2f}")
                st.divider()

            fig=go.Figure() #Cria um gráfico na memória
            fig.add_trace( #Adiciona camadas ao gráfico
                go.Candlestick( #Informa para o plotly que este é um gráfico de velas
                                x=df_ticket.index,
                                open=df_ticket['Open'],
                                high=df_ticket['High'],
                                low=df_ticket['Low'],
                                close=df_ticket['Close']))

            fig.update_layout(
                            title=f'Gráfico de Candles - {acao.upper()}',
                            xaxis_title="Data",
                            yaxis_title="Preço",
                            xaxis_rangeslider_visible=False, #Remove o slider feio que aparece embaixo do gráfico Candles por padrão
                            template="plotly_dark")

            df_ticket["MME9"] = df_ticket["Close"].ewm(span=9, adjust=False).mean()
            fig.add_trace(go.Scatter(
                                x=df_ticket.index,
                                y=df_ticket["MME9"],
                                line=dict(color="yellow", width=1.5),
                                name="MME 9"))
            df_ticket["MME21"] = df_ticket["Close"].ewm(span=21, adjust=False).mean()
            fig.add_trace(go.Scatter(
                                x=df_ticket.index,
                                y=df_ticket["MME21"],
                                line=dict(color="orange", width=1.5),
                                name="MME 21"))
            df_ticket["MME200"] = df_ticket["Close"].ewm(span=200, adjust=False).mean()
            fig.add_trace(go.Scatter(
                                x=df_ticket.index,
                                y=df_ticket["MME200"],
                                line=dict(color="cyan", width=1.5),
                                name="MME 200"))
                            
                            
                    

            st.plotly_chart(fig)


            #Valor por período
            st.markdown(f"### Variação  |  {periodo}")
            if len(df_ticket)>1:
                prim_close_df=df_ticket['Close'][0]
            else:
                prim_close_df=df_ticket['Close'][-1]
            df_ticket['Variação'] = ((df_ticket['Close']-prim_close_df)/prim_close_df)*100
            
            st.subheader('Variação(%)')
            st.line_chart(df_ticket['Variação'])
            st.subheader('Volume')
            st.line_chart(df_ticket['Volume'])
            st.subheader('Preço')
            st.line_chart(df_ticket['Close'],)

            st.markdown("### Métricas Essenciais")
            col1,col2,col3,col4 = st.columns(4)
            #Variação do Período
            col1.metric('Variação no período',value=f"{df_ticket['Variação'][-1]:.2f}%",delta=f"{df_ticket['Variação'][-1]:.2f}%",border=True,width=210)
            #Variação do Dia
            delta_variacao_dia = f"{((df_ticket['Close'][-1]-df_ticket['Close'][-2])/df_ticket['Close'][-2])*100:.2f}"
            col2.metric('Variação do dia',value=valor_atual_str,delta=f"{delta_variacao_dia}%",border=True,width=210)
            #Maior Alta do Período
            col3.metric('Maior Alta do Período',value=f"{df_ticket['Variação'].max():.2f}%",delta=f"{df_ticket['Variação'].max():.2f}%",border=True,width=210)

            #Maior Queda do Período
            col4.metric('Maior Queda do Período',value=f"{df_ticket['Variação'].min():.2f}%",delta=f"{df_ticket['Variação'].min():.2f}%",border=True,width=210)
            
            st.markdown("### Métricas Complementares")
            col1,col2,col3,col4=st.columns(4)

            #Tendência(Alta/Baixa)
            if df_ticket['Variação'][-1]>0:
                col1.metric('Tendência: Alta',value=f"{df_ticket['Variação'][-1]:.2f}%",border=True,width=210)
            else:
                col1.metric('Tendência: Baixa',value=f"{df_ticket['Variação'][-1]:.2f}%",border=True,width=210)

            #Volatilidade
            df_ticket['Retorno Diário'] = df_ticket['Close'].pct_change()*100
            volatilidade = f"{df_ticket['Retorno Diário'].std():.2f}%"
            col2.metric("Volatilidade",value=volatilidade,border=True,width=210)
                
            #Máxima do Período
            maxima_dia=df_ticket['Close'].max()
            col3.metric('Máxima do Período',value=f"{maxima_dia:.2f}",border=True,width=210)
            
            #Mínima do Período
            minima_dia=df_ticket['Close'].min()
            col4.metric('Mínima do Período',value=f"{minima_dia:.2f}",border=True,width=210)
        
    else:
        st.warning('Informe um valor')
        