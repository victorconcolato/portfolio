import streamlit as st

st.markdown("# Chat Financeiro com IA")

# Histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

# Caixa com scroll
chat_box = st.container()

with chat_box:
    st.markdown("""
        <div style="
            height: 400px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #444;
            border-radius: 10px;
            background-color: #111;
        " id="chat-history">
    """, unsafe_allow_html=True)

    # Renderiza mensagens
    for msg in st.session_state.historico:
        if msg["autor"] == "usuario":
            st.markdown(f"""
                <div style="text-align: right; margin: 5px;">
                    <span style="
                        background-color: #0052cc;
                        padding: 8px 12px;
                        border-radius: 12px;
                        color: white;
                        display: inline-block;
                    ">{msg['texto']}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="text-align: left; margin: 5px;">
                    <span style="
                        background-color: #333;
                        padding: 8px 12px;
                        border-radius: 12px;
                        color: white;
                        display: inline-block;
                    ">{msg['texto']}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Input fixo
pergunta = st.text_input("Digite sua pergunta")

if st.button("Enviar"):
    if pergunta.strip():
        st.session_state.historico.append({"autor": "usuario", "texto": pergunta})

        # Resposta fake por enquanto
        resposta = "Aqui entraria a resposta da IA..."
        st.session_state.historico.append({"autor": "ia", "texto": resposta})

        st.rerun()
        