import streamlit as st

st.markdown("# Chat Financeiro com IA")

# Histórico de mensagens (pode ser uma lista simples)
if "historico" not in st.session_state:
    st.session_state.historico = []

# Container onde as mensagens aparecem
chat_container = st.container()

# Container do input
input_container = st.container()

# Exibir mensagens anteriores
with chat_container:
    for msg in st.session_state.historico:
        if msg["autor"] == "usuario":
            st.markdown(f"**Você:** {msg['texto']}")
        else:
            st.markdown(f"**IA:** {msg['texto']}")

# Campo de entrada + botão
with input_container:
    pergunta = st.text_input("Digite sua pergunta")
    if st.button("Enviar"):
        if pergunta.strip():
            # Salva a pergunta no histórico
            st.session_state.historico.append({"autor": "usuario", "texto": pergunta})

            # Aqui você chamaria a OpenAI e geraria a resposta
            resposta = "Aqui entraria a resposta da IA..."

            # Salva a resposta no histórico
            st.session_state.historico.append({"autor": "ia", "texto": resposta})

            # Força o Streamlit a redesenhar a página
            st.rerun()