import os
import streamlit as st
import requests

st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")
st.title("🤖 My Free AI Chatbot")
st.caption("Powered by Groq & Llama 3 — 100% Free!")

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
            GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "NOT_FOUND")

            if GROQ_API_KEY == "NOT_FOUND":
                reply = "❌ GROQ_API_KEY not found. Please check Streamlit secrets."
            else:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": st.session_state.messages
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                res = response.json()

                if "choices" in res:
                    reply = res["choices"][0]["message"]["content"]
                else:
                    reply = f"❌ API Error: {res}"

        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("Built with ⚡ Groq + 🎈 Streamlit")
