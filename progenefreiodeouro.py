import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# =============================
#  App: progenefreiodeouro
#  Descrição: Chatbot de análise
#  de resultados do Freio de Ouro
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

st.sidebar.title("🔍 Exemplos de Perguntas")
st.sidebar.markdown("- Qual a família materna mais frequente no Freio de Ouro?")
st.sidebar.markdown("- Quantos domingueiros possuem linhas maternas repetidas?")
st.sidebar.markdown("- Qual o pai com mais filhos finalistas?")
st.sidebar.markdown("- Qual a nota média na coluna 'Final' por categoria?")

pergunta = st.text_input("Digite sua pergunta sobre o Freio de Ouro:")


def responder_pergunta(pergunta: str, dados: pd.DataFrame) -> str:
    pergunta_l = pergunta.lower()

    # 1) Família materna mais frequente
    if "família materna" in pergunta_l and ("mais frequente" in pergunta_l or "mais repetida" in pergunta_l):
        fam = dados['Familia Materna'].value_counts().head(5)
        linhas = [f"- {n} ({c} ocorrências)" for n, c in fam.items()]
        return "Famílias maternas mais frequentes:\n" + "\n".join(linhas)

    # 2) Domingueiros com linhas maternas repetidas
    if "domingueiro" in pergunta_l and "linhas" in pergunta_l and "materna" in pergunta_l:
        dom = dados[dados['CATEGORIA'].str.contains('DOMINGUEIRO', case=False, na=False)]
        cont = dom['Familia Materna'].value_counts()
        repet = cont[cont > 1]
        return f"Domingueiros analisados: {len(dom)}\nLinhas maternas que se repetem: {len(repet)}"

    # 3) Pai com mais filhos finalistas
    if "pai" in pergunta_l and ("mais filhos" in pergunta_l or "mais descendentes" in pergunta_l):
        if 'PAI' in dados.columns:
            pai = dados['PAI'].value_counts().idxmax()
            total = dados['PAI'].value_counts().max()
            return f"Pai com mais filhos finalistas: {pai} ({total} filhos)"
        return "A coluna 'PAI' não existe na planilha."

    # 4) Nota média na coluna Final por categoria
    if "nota média" in pergunta_l and "final" in pergunta_l:
        if 'Final' in dados.columns:
            media_cat = dados.groupby('CATEGORIA')['Final'].mean().round(2)
            return "Nota média da coluna 'Final' por categoria:\n" + media_cat.to_string()
        return "A coluna 'Final' não existe na planilha."

    return "Desculpe, não consegui entender a pergunta. Tente reformular ou peça um dos exemplos no menu lateral."


if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta, df)
    st.markdown("### Resposta:")
    st.markdown(f"<div style=\"user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
