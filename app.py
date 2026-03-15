import os
import streamlit as st
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN", "")
client = InferenceClient(token=HF_TOKEN)
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")
st.title("🤖 My Free AI Chatbot")
st.caption("Powered by Hugging Face & Streamlit — 100% Free!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask me anything... 💬")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            try:
                prompt = ""
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        prompt += f"<s>[INST] {msg['content']} [/INST]"
                    else:
                        prompt += f" {msg['content']} </s>"

                reply = client.text_generation(
                    prompt,
                    model=MODEL,
                    max_new_tokens=500,
                    temperature=0.7
                )
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("Built with 🤗 Hugging Face & 🎈 Streamlit")
