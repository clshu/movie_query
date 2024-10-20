import os
from dotenv import load_dotenv

import streamlit as st
from src.movie_insights import set_up_components, run_movie_insights

# Load API KEY from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

st.title("Movie Query App")


user_hint = (
    "Ask me a question about movies! For example, you can ask questions like:\n"
    "- What are movies directed by Christopher Nolan?\n"
    "- What are movies with Brat Pitt?\n"
)
st.write(user_hint)

# Initialize components
# Data loading and model setup

collection, openai_ef, llm = set_up_components(OPENAI_API_KEY)


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your movie question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        print(prompt)

    with st.chat_message("assistant"):

        query = prompt
        response = run_movie_insights(collection, openai_ef, llm, query)
        st.write(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response})
