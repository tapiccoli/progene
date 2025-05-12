import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import traceback
import re

# Configurar a API da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carregar os dados da planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("dadosprogene.xlsx")
    df['Prova'] = df['Prova'].replace({"F.O.": "Freio de Ouro", "MORF": "Morfologia"})
    return df

# Carregar dataframe
df = carregar_dados()

# Título da aplicação
st.title("🤖 Consulta Bot - Genética Crioula (Inteligência Livre)")

# Exemplos de perguntas
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
        # Limpar marcações de bloco de código e a keyword python
        codigo_bruto = resposta.choices[0].message.content
        # Remover backticks e tags de linguagem
        codigo_limpo = re.sub(r"```[a-zA-Z]*", "", codigo_bruto)
        lines = codigo_limpo.splitlines()
        filtered = [l for l in lines if l.strip() and not l.strip().lower().startswith('python') and not l.strip().startswith('```')]
        return "\n".join(filtered)
    except Exception as e:
        return f"# ERRO: {e}"

# Função para executar o código gerado
def executar_codigo(codigo, dados):
    try:
        local_vars = {"df": dados.copy()}
        exec(codigo, {}, local_vars)
        for var_name, var_value in local_vars.items():
            if isinstance(var_value, (pd.Series, pd.DataFrame)):
                return var_value.to_markdown()
        return "Código executado, mas nenhum DataFrame ou Series foi retornado."
    except Exception:
        return "Erro na execução do código:\n" + traceback.format_exc()

# Fluxo principal
if pergunta:
    with st.spinner("Gerando análise baseada em IA..."):
        codigo = gerar_codigo_analise(pergunta)
        resultado = executar_codigo(codigo, df)
        st.markdown("### Resultado da Análise:")
        st.markdown(f"<div style=\"user-select: none; -webkit-user-select: none; -moz-user-select: none;\">{resultado}</div>", unsafe_allow_html=True)
