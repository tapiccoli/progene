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


def responder_pergunta(pergunta: str, dados: pd.DataFrame) -> str:
    snapshot = dados.head(1050).to_string(index=False)
    system_prompt = (
        "Você é um analista especializado em cavalos Crioulos e provas do Freio de Ouro.\n"
        "Abaixo está um exemplo dos dados disponíveis. Responda de forma clara e objetiva:\n"
        + snapshot
    )
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.2
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar IA: {e}"


if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta, df)
    st.markdown("### Resposta:")
    st.markdown(f"<div style=\"user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
