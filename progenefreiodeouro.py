import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# =============================
#  App: progenefreiodeouro
#  Descrição: Chatbot de análise
#  de resultados do Freio de Ouro com IA
# =============================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_data
def carregar_dados():
    df = pd.read_excel("dadosfreiodeourodomingueiro.xlsx")
    if 'Prova' in df.columns:
        df['Prova'] = df['Prova'].replace({"F.O.": "Freio de Ouro"})
    return df

df = carregar_dados()

st.title("progenefreiodeouro")

st.sidebar.markdown("Esses são apenas exemplos para orientar o tipo de pergunta que você pode fazer:")
st.sidebar.markdown("- Quantos domingueiros possuem linhas maternas repetidas?")
st.sidebar.markdown("- Qual o pai com mais filhos finalistas?")
st.sidebar.markdown("- Qual a nota média na coluna 'Final' por categoria?")

pergunta = st.text_input("Faça uma pergunta livre sobre os dados do Freio de Ouro:")


def responder_pergunta(pergunta: str) -> str:
    try:
        upload = client.files.create(
            file=open("dadosfreiodeourodomingueiro.xlsx", "rb"),
            purpose="assistants"
        )

        resposta = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um analista especialista em provas de Freio de Ouro. "
                        "Use o conteúdo da planilha enviada (com file_id) para responder à pergunta de forma precisa."
                    )
                },
                {"role": "user", "content": pergunta}
            ],
            tools=[{"type": "file_search"}],
            tool_choice="auto",
            file_ids=[upload.id]
        )

        return resposta.choices[0].message.content

    except Exception as e:
        return f"Erro ao consultar IA com arquivo: {e}"


if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta)
    st.markdown("### Resposta:")
    st.markdown(f"<div style=\"user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
