import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import traceback

# Configurar a API da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carregar os dados da planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("dadosprogene.xlsx")
    df['Prova'] = df['Prova'].replace({"F.O.": "Freio de Ouro", "MORF": "Morfologia"})
    return df

df = carregar_dados()

# Título da aplicação
st.title("🤖 Consulta Bot - Genética Crioula (Inteligência Livre)")

# Mostra algumas perguntas prontas
st.sidebar.title("🔍 Exemplos de Perguntas")
st.sidebar.markdown("- Qual o pai com maior número de filhos domingueiros?")
st.sidebar.markdown("- Quais as linhas maternas mais repetidas na Morfologia?")
st.sidebar.markdown("- Quem foi o campeão da Morfologia em 2023?")
st.sidebar.markdown("- Qual a média da nota Final dos machos no Freio de Ouro?")

# Entrada de pergunta
pergunta = st.text_input("Digite sua pergunta sobre os dados:")

# Função para gerar código com base na pergunta

def gerar_codigo_analise(pergunta):
    prompt = f"""
    Você é um analista de dados especializado em cavalos da raça Crioula.
    Com base na pergunta abaixo, escreva um código Python usando pandas
    para analisar um DataFrame chamado df que contém dados da planilha.

    Pergunta: {pergunta}

    Forneça apenas o código. Não inclua explicações, nem tags markdown, nem a palavra 'python'.
    """
    try:
        resposta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um gerador de código pandas que responde apenas com código."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
                codigo_bruto = resposta.choices[0].message.content
        linhas = codigo_bruto.strip().splitlines()
        linhas_filtradas = [l for l in linhas if not l.strip().lower().startswith('python')]
        return "
".join(linhas_filtradas).strip()
    except Exception as e:
        return f"# ERRO: {e}"

# Função para executar o código gerado
def executar_codigo(codigo, dados):
    try:
        local_vars = {"df": dados.copy()}
        exec(codigo, {}, local_vars)
        for var in local_vars:
            if isinstance(local_vars[var], (pd.Series, pd.DataFrame)):
                return local_vars[var].to_markdown()
        return "Código executado, mas nenhum DataFrame ou Series foi retornado."
    except Exception:
        return "Erro na execução do código:\n" + traceback.format_exc()

# Processamento principal
if pergunta:
    with st.spinner("Gerando análise baseada em IA..."):
        codigo = gerar_codigo_analise(pergunta)
        resposta = executar_codigo(codigo, df)
        st.markdown("### Resultado da Análise:")
        st.markdown(f"<div style=\"user-select: none; -webkit-user-select: none; -moz-user-select: none;\">{resposta}</div>", unsafe_allow_html=True)
