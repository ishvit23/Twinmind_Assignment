import streamlit as st
import requests

st.set_page_config(page_title="Second Brain AI Companion", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "login"
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

def show_login():
    st.title("Login")
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(
            "http://localhost:8000/api/auth/login",
            json={"username": username, "password": password}
        )
        if res.status_code == 200 and "access_token" in res.json():
            st.session_state.access_token = res.json()["access_token"]
            st.session_state.user_id = username
            st.session_state.page = "app"
            st.rerun()
        else:
            st.error(res.json().get("detail", "Login failed."))
            st.session_state.page = "register"
            st.rerun()

def show_register():
    st.title("Register")
    st.info("Please register to continue.")  # <-- Message only at the top
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        res = requests.post(
            "http://localhost:8000/api/auth/register",
            json={"username": username, "password": password, "email": email}
        )
        if res.status_code == 200:
            st.success("Registration successful! Please login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            error_msg = res.json().get("detail", "Registration failed.")
            st.error(error_msg)
            st.session_state.page = "login"
            st.rerun()

def show_app():
    st.title("🧠 Second Brain AI Companion")
    st.header("Ingest Data")
    modality = st.selectbox(
        "Choose modality to ingest:",
        ["Document", "Audio", "Image", "Web URL", "Plain Text"]
    )
    user_id = st.session_state.user_id
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    if modality == "Document":
        uploaded_file = st.file_uploader("Upload Document (.pdf, .md, .txt)", type=["pdf", "md", "txt"])
        if st.button("Ingest Document") and uploaded_file:
            files = {"file": uploaded_file}
            res = requests.post(
                "http://localhost:8000/api/ingest/document",
                files=files,
                params={"user_id": user_id},
                headers=headers
            )
            st.success(f"Document Ingested: {res.json().get('filename', '')}")

    elif modality == "Audio":
        uploaded_audio = st.file_uploader("Upload Audio (.mp3, .m4a)", type=["mp3", "m4a"])
        if st.button("Ingest Audio") and uploaded_audio:
            files = {"file": uploaded_audio}
            res = requests.post(
                "http://localhost:8000/api/ingest/audio",
                files=files,
                params={"user_id": user_id},
                headers=headers
            )
            st.success(f"Audio Ingested: {res.json().get('filename', '')}")

    elif modality == "Image":
        uploaded_image = st.file_uploader("Upload Image (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
        if st.button("Ingest Image") and uploaded_image:
            files = {"file": uploaded_image}
            res = requests.post(
                "http://localhost:8000/api/ingest/image",
                files=files,
                params={"user_id": user_id},
                headers=headers
            )
            st.success(f"Image Ingested: {res.json().get('filename', '')}")

    elif modality == "Web URL":
        url = st.text_input("Enter Web URL")
        if st.button("Ingest Web Content") and url:
            res = requests.post(
                "http://localhost:8000/api/ingest/web",
                json={"url": url, "user_id": user_id},
                headers=headers
            )
            st.success(f"Web Content Ingested: {url}")

    elif modality == "Plain Text":
        text = st.text_area("Enter Text")
        if st.button("Ingest Text") and text:
            res = requests.post(
                "http://localhost:8000/api/ingest/text",
                json={"text": text, "user_id": user_id},
                headers=headers
            )
            st.success("Text Ingested")

    st.markdown("---")
    st.header("💬 Chat with Your Second Brain")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.text_input(
        "Ask your AI companion:",
        key="chat_input",
        placeholder="(eg .. Tell me about Ishvit Khajuria.)"  # <-- Added placeholder
    )

    if st.button("Send", key="send_btn") and query:
        with st.spinner("Thinking..."):
            response = requests.post(
                "http://localhost:8000/api/rag",
                json={"query": query, "user_id": user_id, "top_k": 5},
                headers=headers
            )
            answer = response.json().get("answer", "No answer found.")
            sources = response.json().get("sources", [])
            st.session_state.chat_history.append({"user": query, "ai": answer, "sources": sources})

    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**AI:** {chat['ai']}")
        if chat["sources"]:
            with st.expander("Sources / Context"):
                for idx, src in enumerate(chat["sources"], 1):
                    st.markdown(f"{idx}. {src}")

    st.markdown("---")
    st.caption("Built for the Second Brain AI Companion assignment. Supports multi-modal ingestion, semantic search, Gemini-powered answers, and user authentication.")

# Routing logic
if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "register":
    show_register()
elif st.session_state.page == "app":
    show_app()