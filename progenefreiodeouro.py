import streamlit as st
import pandas as pd
import os
import openai

# =============================
#  App: progenefreiodeouro
#  Descrição: Chatbot de análise
#  de resultados do Freio de Ouro
# =============================


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
    snapshot = dados.head(15).to_string(index=False)
    system_prompt = (
        "Você é um analista de dados especializado em cavalos Crioulos. "
        "Com base na pergunta a seguir, use o contexto da planilha abaixo para responder de forma objetiva e clara.
"
        + snapshot
    )
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.2
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao consultar IA: {e}"



if pergunta:
    with st.spinner("Consultando GPT-3.5 para analisar o Freio de Ouro..."):
        resposta = responder_pergunta(pergunta, df)
    st.markdown("### Resposta:")
    st.markdown(f"<div style=\"user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
