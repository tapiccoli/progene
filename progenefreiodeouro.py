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
        # Fazer upload do arquivo
        file_upload = client.files.create(
            file=open("dadosfreiodeourodomingueiro.xlsx", "rb"),
            purpose="assistants"
        )

        # Criar o assistant com o arquivo já vinculado
        assistant = client.beta.assistants.create(
            name="Freio de Ouro Analyst",
            instructions="Você é um especialista em provas do Freio de Ouro. Use os dados fornecidos para responder perguntas com precisão.",
            model="gpt-4-turbo",
            tools=[{"type": "file_search"}],
            file_ids=[file_upload.id]
            
        )

        

        # Criar um thread
        thread = client.beta.threads.create()

        # Enviar a pergunta
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )

        # Iniciar a execução do assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Aguardar a execução terminar
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                return "A execução da IA falhou."

        # Buscar a resposta
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value
        return resposta

    except Exception as e:
        return f"Erro ao consultar IA com assistant: {e}"


if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta)
    st.markdown("### Resposta:")
    st.markdown(f"<div style=\"user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
