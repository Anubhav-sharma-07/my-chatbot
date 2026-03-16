import os
import streamlit as st
import requests
import json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
MEMORY_FILE = "client_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

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
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=data
    )
    res = response.json()
    if "choices" in res:
        return res["choices"][0]["message"]["content"]
    return f"Error: {res}"

st.set_page_config(page_title="Aria - Sales Agent", page_icon="🤖")
st.title("🤖 Aria — Your Sales Agent")
st.caption("Powered by Groq + Web Search + Memory — 100% Free!")

# Load client memory
memory = load_memory()
client_names = list(memory.keys())

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.subheader("👥 Known Clients")
    if client_names:
        for name in client_names:
            info = memory[name]
            st.markdown(f"**{name}**")
            for k, v in info.items():
                st.caption(f"  {k}: {v}")
    else:
        st.caption("No clients remembered yet.")
    st.markdown("---")
    st.markdown("**Aria can:**")
    st.markdown("- Answer sales questions")
    st.markdown("- Search web for live prices")
    st.markdown("- Remember every client")
    st.markdown("---")
    st.markdown("Built with ⚡ Groq + 🔍 Serper + 🧠 Memory")

# Build system prompt with memory context
memory_context = ""
if memory:
    memory_context = f"\n\nKnown clients from memory:\n{json.dumps(memory, indent=2)}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""You are Aria, a friendly and professional sales assistant.
Your job is to:
- Greet clients warmly by name if you know them
- Understand what the client needs
- Recommend the right product confidently
- Handle objections politely
- Always end with a clear call to action like 'Shall I place the order for you?'
- When a client tells you their name, budget, or preferences, remember it.
- If you learn something important about a client (name, budget, interests), 
  reply normally AND add this exact line at the end of your response:
  REMEMBER: name=John, budget=500, interest=laptops
  (only include fields you actually learned)
Keep replies short, friendly and focused on helping the client buy.{memory_context}"""
        }
    ]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

user_input = st.chat_input("Talk to Aria... 💬")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

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
            "content": f"Web search results:\n{search_context}\n\nClient: {user_input}"
        })
    else:
        messages_to_send.append({"role": "user", "content": user_input})

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Aria is thinking... 🤔"):
            reply = ask_groq(messages_to_send)

        # Extract and save memory if Aria learned something
        if "REMEMBER:" in reply:
            parts = reply.split("REMEMBER:")
            clean_reply = parts[0].strip()
            memory_line = parts[1].strip()
            client_info = {}
            client_name = "unknown"
            for item in memory_line.split(","):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k == "name":
                        client_name = v
                    else:
                        client_info[k] = v
            if client_name != "unknown":
                memory = load_memory()
                if client_name not in memory:
                    memory[client_name] = {}
                memory[client_name].update(client_info)
                save_memory(memory)
            reply = clean_reply

        st.write(reply)
        if search_context:
            with st.expander("🔍 Web sources used"):
                st.caption(search_context)

    st.session_state.messages.append({"role": "assistant", "content": reply})
