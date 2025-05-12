import streamlit as st
import pandas as pd
import openai
import os

# Configurações da página
st.set_page_config(
    page_title="Progenefreiodeouro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Oculta menu do Streamlit e desabilita seleção de texto global
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    body {user-select: none; -webkit-user-select: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Carrega chave da OpenAI
oai_key = st.secrets.get("OPENAI_API_KEY")
if not oai_key:
    st.error("Erro interno: chave da OpenAI não encontrada.")
    st.stop()
openai.api_key = oai_key

# Prompt padrão para o assistente de dados
system_prompt = (
    "Você precisa agir como um analisador de dados experiente, "
    "que busca os dados na planilha 'dadosfreiodeourodomingueiro.xlsx' encontrada no repositório deste aplicativo. "
    "Use os títulos das colunas da tabela como referência nas perguntas e, após isso, exiba a resposta em HTML, de forma que não possa ser copiada."
)

# Função para carregar a planilha padrão de apoio
@st.cache_data
def load_data():
    arquivo = "dadosfreiodeourodomingueiro.xlsx"
    if os.path.exists(arquivo):
        try:
            # Usa engine openpyxl para leitura de xlsx
            return pd.read_excel(arquivo, engine='openpyxl')
        except Exception:
            return None
    return None

# Carrega dados
_df = load_data()
if _df is None:
    st.error("Erro interno ao carregar dados. Verifique se 'dadosfreiodeourodomingueiro.xlsx' está na raiz do app.")
    st.stop()

# Campo de entrada de perguntas
query = st.text_input("Faça sua pergunta sobre os dados:")
if query:
    with st.spinner("Processando..."):
        # Converte a tabela em CSV para o prompt
        table_csv = _df.to_csv(index=False)
        # Prepara sequência de mensagens para o modelo
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Tabela em CSV:\n{table_csv}\n\nPergunta: {query}"}
        ]
        # Chama API de chat do OpenAI corretamente
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            max_tokens=2048
        )
        # Extrai o HTML de resposta
        html_output = response.choices[0].message.content
        # Wrapper para desabilitar cópia
        wrapper = (
            "<div style='user-select: none; -webkit-user-select: none;'>" +
            html_output +
            "</div>"
        )
        # Exibe a resposta protegida
        st.components.v1.html(wrapper, height=600, scrolling=True)
