import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Configurar a API da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carregar os dados da planilha
@st.cache_data
def carregar_dados():
    return pd.read_excel("dadosprogene.xlsx")

df = carregar_dados()

# Título da aplicação
st.title("🤖 Consulta Bot - Genética Crioula")

# Mostra algumas perguntas prontas
st.sidebar.title("🔍 Exemplos de Perguntas")
st.sidebar.markdown("- Quantos domingueiros possuem linhas repetidas?")
st.sidebar.markdown("- Qual a linha materna mais frequente no Freio de Ouro?")
st.sidebar.markdown("- Quais animais da MORF têm linhas que se repetem?")

# Entrada de pergunta
pergunta = st.text_input("Digite sua pergunta sobre os dados:")

# Função para gerar resposta com base na pergunta
def responder_pergunta(pergunta, dados):
    prompt = f"""
    Você é um especialista em dados da raça crioula. Com base na seguinte tabela de dados (resumo do conteúdo):

    {dados.head(10).to_string(index=False)}

    Responda com base na pergunta: {pergunta}
    Seja claro e use dados reais da tabela.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em dados de cavalos Crioulos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar IA: {e}"

# Executar quando o usuário digitar algo
if pergunta:
    with st.spinner("Consultando base de dados e IA..."):
        resposta = responder_pergunta(pergunta, df)
        st.markdown("### Resposta:")
        st.markdown(f"<div style='user-select: none; -webkit-user-select: none; -moz-user-select: none;'>{resposta}</div>", unsafe_allow_html=True)
