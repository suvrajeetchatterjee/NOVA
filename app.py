import streamlit as st
from openai import OpenAI
import os
import json
import uuid

# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="NOVA",
    layout="wide"
)

# =========================
# GROQ CLIENT
# =========================

client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)
# =========================
# CHAT STORAGE
# =========================

CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

# =========================
# FUNCTIONS
# =========================

def get_chat_path(chat_id):
    return os.path.join(CHAT_DIR, f"{chat_id}.json")

def load_chat(chat_id):

    path = get_chat_path(chat_id)

    if os.path.exists(path):

        with open(path, "r") as file:
            return json.load(file)

    return {
        "title": "New Chat",
        "messages": []
    }

def save_chat(chat_id, data):

    path = get_chat_path(chat_id)

    with open(path, "w") as file:
        json.dump(data, file)

def get_all_chats():

    chats = []

    for file in os.listdir(CHAT_DIR):

        if file.endswith(".json"):

            chat_id = file.replace(".json", "")

            data = load_chat(chat_id)

            chats.append({
                "id": chat_id,
                "title": data.get("title", "New Chat")
            })

    return chats

# =========================
# SESSION STATE
# =========================

if "current_chat" not in st.session_state:

    new_chat_id = str(uuid.uuid4())

    st.session_state.current_chat = new_chat_id

    save_chat(new_chat_id, {
        "title": "New Chat",
        "messages": []
    })

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.title(" NOVA")

    if st.button("➕ New Chat"):

        new_chat_id = str(uuid.uuid4())

        save_chat(new_chat_id, {
            "title": "New Chat",
            "messages": []
        })

        st.session_state.current_chat = new_chat_id

        st.rerun()

    st.divider()

    chats = get_all_chats()

    for chat in chats:

        col1, col2 = st.columns([4, 1])

        # OPEN CHAT

        with col1:

            if st.button(chat["title"], key=chat["id"]):

                st.session_state.current_chat = chat["id"]

                st.rerun()

        # DELETE CHAT

        with col2:

            if st.button("✕", key=f"delete_{chat['id']}"):

                os.remove(get_chat_path(chat["id"]))

                if st.session_state.current_chat == chat["id"]:

                    new_chat_id = str(uuid.uuid4())

                    save_chat(new_chat_id, {
                        "title": "New Chat",
                        "messages": []
                    })

                    st.session_state.current_chat = new_chat_id

                st.rerun()

# =========================
# LOAD CURRENT CHAT
# =========================

chat_data = load_chat(st.session_state.current_chat)

messages = chat_data["messages"]

# =========================
# MAIN UI
# =========================

st.title("NOVA")
st.caption("Your AI assistant")

# DISPLAY MESSAGES

for message in messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

# =========================
# USER INPUT
# =========================

prompt = st.chat_input("Message NOVA...")

if prompt:

    # SAVE USER MESSAGE

    messages.append({
        "role": "user",
        "content": prompt
    })

    # SHOW USER MESSAGE

    with st.chat_message("user"):
        st.write(prompt)

    # AI RESPONSE

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )

            reply = response.choices[0].message.content

            st.write(reply)

    # SAVE AI RESPONSE

    messages.append({
        "role": "assistant",
        "content": reply
    })

    # AUTO TITLE

    if chat_data["title"] == "New Chat":

        short_title = prompt[:30]

        chat_data["title"] = short_title

    # SAVE CHAT

    chat_data["messages"] = messages

    save_chat(st.session_state.current_chat, chat_data)

    st.rerun()