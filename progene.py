import streamlit as st
import pandas as pd
from openai import OpenAI
import os

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
st.title("🤖 Consulta Bot - Genética Crioula")

# Mostra algumas perguntas prontas
st.sidebar.title("🔍 Exemplos de Perguntas")
st.sidebar.markdown("- Quantos domingueiros possuem linhas repetidas?")
st.sidebar.markdown("- Qual a linha materna mais frequente no Freio de Ouro?")
st.sidebar.markdown("- Quais animais da Morfologia têm linhas maternas que se repetem?")
st.sidebar.markdown("- Qual o pai com maior número de filhos nos domingueiros do Freio de Ouro nos últimos 10 anos?")

# Entrada de pergunta
pergunta = st.text_input("Digite sua pergunta sobre os dados:")

# Função para gerar resposta com base na pergunta
def responder_pergunta(pergunta, dados):
    prompt_system = """
    Você é um assistente de análise genética da raça Crioula. Você tem acesso a uma planilha contendo informações sobre provas como o Freio de Ouro e Morfologia.

    A tabela possui as seguintes colunas:
    - 'Nome Animal': nome do cavalo
    - 'Prova': nome da prova (Freio de Ouro, Morfologia)
    - 'CATEGORIA': categoria do animal (ex: DOMINGUEIRO, FINALISTA)
    - 'C': colocação final do animal na prova
    - 'A': ano da prova
    - 'SEXO': sexo do animal
    - 'Familia Materna': nome da linhagem base materna do cavalo
    - Além disso, há colunas com notas de desempenho em provas como: 'Morfologia', 'Andadura', 'Figura', 'VSP/ESB', 'Mangueira I', 'Campo I', 'Mangueira II', 'Bayard', 'Campo II', e 'Final'.

    Ao responder, siga estas diretrizes:
    - Use os dados diretamente da tabela.
    - Dê respostas com números exatos: totais, porcentagens, listas ordenadas.
    - Se a pergunta envolver "repetidas", use frequência de nomes na coluna 'Familia Materna'.
    - Seja direto, evite rodeios.
    - Se possível, inclua rankings ou percentuais de destaque.

    Exemplo:
    Pergunta: Quais famílias maternas se repetem na Morfologia?
    Resposta: As famílias mais frequentes na Morfologia são: Família X (8 vezes), Família Y (6 vezes)...
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": pergunta}
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
