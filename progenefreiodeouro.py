import streamlit as st
import pandas as pd
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Carregar a chave da API do Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Carregar o modelo de embeddings (manter em cache)
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

embedding_model = load_embedding_model()

@st.cache_data
def load_data():
    df = pd.read_excel("dadosfreiodeourodomingueiro.xlsx")
    return df

df = load_data()

# Gerar embeddings para todas as colunas (manter em cache)
@st.cache_data
def generate_all_column_embeddings(df, model):
    all_column_embeddings = {}
    for col in df.columns:
        unique_values = df[col].astype(str).unique()
        embeddings = model.encode(unique_values)
        all_column_embeddings[col] = {value: emb for value, emb in zip(unique_values, embeddings)}
    return all_column_embeddings

all_column_embeddings = generate_all_column_embeddings(df, embedding_model)

st.title("Progen Freio de Ouro")
st.subheader("Pergunte sobre os dados dos animais:")

pergunta = st.text_input("Sua pergunta:")
resposta_area = st.empty()

if st.button("Obter Resposta"):
    if pergunta:
        resposta_area.markdown("Processando...")

        try:
            pergunta_embedding = embedding_model.encode([pergunta])[0]
            relevant_context = []

            for col, value_embeddings in all_column_embeddings.items():
                for value, emb in value_embeddings.items():
                    similarity = cosine_similarity([pergunta_embedding], [emb])[0][0]
                    if similarity > 0.7: # Ajuste o limiar conforme necessário
                        relevant_rows = df[df[col].astype(str) == value]
                        for index, row in relevant_rows.iterrows():
                            relevant_context.append(row.to_dict())

            # Remover duplicatas do contexto relevante
            unique_context = [dict(t) for t in set(tuple(d.items()) for d in relevant_context)]

            context_string = ""
            for item in unique_context:
                context_string += f"{item}\n"

            prompt = f"Você é um assistente que responde perguntas sobre dados de animais. Use as seguintes informações para responder à pergunta:\n\n{context_string}\n\nPergunta: {pergunta}\nResposta:"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente útil para responder perguntas sobre dados de animais."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500 # Aumentei um pouco mais o max_tokens
            )
            resposta_ia = response.choices[0].message.content
            resposta_area.markdown(resposta_ia)

        except Exception as e:
            resposta_area.error(f"Ocorreu um erro: {e}")
    else:
        resposta_area.warning("Por favor, digite sua pergunta.")
