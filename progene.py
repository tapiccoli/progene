import streamlit as st
import pandas as pd
import openai
import os

# =============================
#  App: progenefreiodeouro
#  Descrição: Chatbot de análise
#  de resultados do Freio de Ouro
# =============================

# Configurar a API da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar os dados da planilha Freio de Ouro
@st.cache_data
def carregar_dados():
    df = pd.read_excel("dadosfreiodeourodomingueiro.xlsx")
    # Expandir abreviatura
    df['Prova'] = df['Prova'].replace({"F.O.": "Freio de Ouro"})
    return df

df = carregar_dados()

# Interface do Streamlit
st.title("progenefreiodeouro")

st.sidebar.title("🔍 Exemplos de Perguntas")
st.sidebar.markdown("- Qual a família materna mais frequente no Freio de Ouro?")
st.sidebar.markdown("- Quantos domingueiros possuem linhas maternas repetidas?")
st.sidebar.markdown("- Qual o pai com mais filhos finalistas?")
st.sidebar.markdown("- Qual a nota média na coluna 'Final' por categoria?")

# Entrada de pergunta do usuário
pergunta = st.text_input("Digite sua pergunta sobre o Freio de Ouro:")

# Função de resposta usando GPT-3.5-turbo
def responder_pergunta(pergunta: str, dados: pd.DataFrame) -> str:
    """Gera resposta usando a IA com snapshot de dados para contexto."""
    snapshot = dados.head(10).to_string(index=False)
    system_prompt = (
        "Você é um assistente de análise de dados de cavalos Crioulos, especializado nas provas de Freio de Ouro. "
        "A tabela possui colunas como: 'Nome Animal', 'CATEGORIA', 'C', 'A', 'SEXO', 'Familia Materna' e notas das etapas: "
        "'Andadura', 'Figura', 'VSP/ESB', 'Mangueira I', 'Campo I', 'Mangueira II', 'Bayard', 'Campo II', 'Final'. "
        "Use o contexto abaixo para responder de forma objetiva.\n" + snapshot
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar IA: {e}"

# Exibir resposta
if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta, df)
        st.markdown("### Resposta:")
        st.markdown(f"<div style=\"user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
