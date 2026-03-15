# ============================================
# 🤖 FREE AI CHATBOT
# Built with Hugging Face + Streamlit
# ============================================

import os
import streamlit as st
from huggingface_hub import InferenceClient

# --- SETUP ---
# Get the token from Streamlit secrets (safe & secure)
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Connect to the free AI model
client = InferenceClient(token=HF_TOKEN)

# The free AI model we are using
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

# --- PAGE SETTINGS ---
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --- TITLE ---
st.title("🤖 My Free AI Chatbot")
st.caption("Powered by Hugging Face & Streamlit — 100% Free!")

# --- CHAT HISTORY ---
# This saves the conversation so the AI remembers context
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful, friendly assistant. Answer questions clearly and simply."
        }
    ]

# --- DISPLAY PAST MESSAGES ---
for msg in st.session_state.messages:
    if msg["role"] != "system":  # Don't show the system message to user
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- USER INPUT BOX ---
user_input = st.chat_input("Ask me anything... 💬")

if user_input:

    # Show user message on screen
    with st.chat_message("user"):
        st.write(user_input)

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # --- GET AI RESPONSE ---
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            try:
               response = client.text_generation(
    model=MODEL,
    prompt=f"<s>[INST] {user_input} [/INST]",
    max_new_tokens=500,
    temperature=0.7
)
reply = response
                reply = response.choices[0].message.content

            except Exception as e:
                reply = f"❌ Error: {str(e)}. Please check your Hugging Face token."

        st.write(reply)

    # Save AI reply to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")

    # Button to clear chat history
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": "You are a helpful, friendly assistant. Answer questions clearly and simply."
            }
        ]
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("- Ask any question you like")
    st.markdown("- The AI remembers your conversation")
    st.markdown("- Click 'Clear Chat' to start fresh")
    st.markdown("---")
    st.markdown("Built with ❤️ using:")
    st.markdown("- 🤗 Hugging Face")
    st.markdown("- 🎈 Streamlit")


