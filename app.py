import os
import streamlit as st
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

def search_web(query):
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    data = {"q": query, "num": 3}
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, json=data)
        results = response.json().get("organic", [])
        if not results:
            return "No search results found."
        summary = ""
        for r in results[:3]:
            summary += f"- {r.get('title', '')}: {r.get('snippet', '')}\n"
        return summary
    except:
        return "Search failed."

def ask_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"model": "llama-3.3-70b-versatile", "messages": messages}
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    res = response.json()
    if "choices" in res:
        return res["choices"][0]["message"]["content"]
    return f"Error: {res}"

st.set_page_config(page_title="Aria - Sales Agent", page_icon="🤖")
st.title("🤖 Aria — Your Sales Agent")
st.caption("Powered by Groq + Web Search — 100% Free!")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """You are Aria, a friendly and professional sales assistant.
Your job is to:
- Greet clients warmly by name if you know it
- Understand what the client needs
- Recommend the right product or service confidently
- Handle objections politely
- Always end with a clear call to action like 'Shall I place the order for you?'
If you need current product info, prices or news, use the search results provided.
Keep replies short, friendly and focused on helping the client buy."""
        }
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

user_input = st.chat_input("Ask Aria anything... 💬")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    # Auto search if user asks about price, product or news
    search_keywords = ["price", "cost", "latest", "best", "compare", "review", "buy", "cheap", "deal"]
    should_search = any(word in user_input.lower() for word in search_keywords)

    search_context = ""
    if should_search:
        with st.spinner("🔍 Searching the web..."):
            search_context = search_web(user_input)

    messages_to_send = st.session_state.messages.copy()
    if search_context:
        messages_to_send.append({
            "role": "user",
            "content": f"Web search results for context:\n{search_context}\n\nClient question: {user_input}"
        })
    else:
        messages_to_send.append({"role": "user", "content": user_input})

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Aria is thinking... 🤔"):
            reply = ask_groq(messages_to_send)
        st.write(reply)
        if search_context:
            with st.expander("🔍 Web sources used"):
                st.caption(search_context)

    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": """You are Aria, a friendly and professional sales assistant.
Your job is to:
- Greet clients warmly
- Understand what the client needs
- Recommend products confidently
- Handle objections politely
- Always end with a clear call to action.
Keep replies short, friendly and focused on helping the client buy."""
            }
        ]
        st.rerun()
    st.markdown("---")
    st.markdown("**Aria can:**")
    st.markdown("- Answer sales questions")
    st.markdown("- Search web for live prices")
    st.markdown("- Remember your conversation")
    st.markdown("---")
    st.markdown("Built with ⚡ Groq + 🔍 Serper")
