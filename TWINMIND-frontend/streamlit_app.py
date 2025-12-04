import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Second Brain AI Companion",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = os.getenv("BACKEND_URL", "https://twinmind-assignment-4.onrender.com")

# ---------------------------------------------
# SAFE JSON PARSER
# ---------------------------------------------
def safe_request(res):
    if res is None:
        return None, "No response"

    try:
        return res.json(), None
    except Exception:
        return None, res.text[:1000]


# ---------------------------------------------
# AUTH HELPERS
# ---------------------------------------------
def login_user(username, password):
    res = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    return safe_request(res)


def register_user(username, password):
    res = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"username": username, "password": password}
    )
    return safe_request(res)


# ---------------------------------------------
# LOGIN PAGE
# ---------------------------------------------
def login_page():
    st.title("🔐 Login to Second Brain")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data, err = login_user(username, password)

        if data and data.get("status") == "success":
            st.success("Logged in successfully!")

            # Store session
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.token = data.get("token", "")
            st.session_state.user_id = username  # USED BY RAG & INGEST ENDPOINTS

            st.rerun()
        else:
            st.error(err or data.get("message", "Login failed"))


    st.write("---")
    if st.button("Create an Account"):
        st.session_state.page = "signup"
        st.rerun()


# ---------------------------------------------
# SIGNUP PAGE
# ---------------------------------------------
def signup_page():
    st.title("📝 Create Your Second Brain Account")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")

    if st.button("Sign Up"):
        data, err = register_user(username, password)

        if data and data.get("status") == "success":
            st.success("Account created! Please login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(err or data.get("message", "Registration failed"))

    st.write("---")
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ---------------------------------------------
# MAIN APPLICATION (YOUR ORIGINAL APP)
# ---------------------------------------------
def show_app():
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.title("🧠 Second Brain AI Companion")
    st.header("Ingest Data")

    modality = st.selectbox(
        "Choose modality to ingest:",
        ["Document", "Audio", "Image", "Web URL", "Plain Text"]
    )

    user_id = st.session_state.username   # IMPORTANT
    headers = {}

    # -------------------- DOCUMENT --------------------
    if modality == "Document":
        uploaded_file = st.file_uploader(
            "Upload Document (.pdf, .md, .txt)",
            type=["pdf", "md", "txt"]
        )

        if st.button("Ingest Document") and uploaded_file:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/upload",
                files={"file": uploaded_file},
                params={"user_id": user_id},
            )
            data, err = safe_request(res)
            if data:
                st.success(f"Document Ingested: {data.get('filename', '')}")
            else:
                st.error(f"Error: {err}")

    # -------------------- AUDIO --------------------
    elif modality == "Audio":
        uploaded_audio = st.file_uploader("Upload Audio (.mp3, .m4a)", type=["mp3", "m4a"])
        if st.button("Ingest Audio") and uploaded_audio:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/audio",
                files={"file": uploaded_audio},
                params={"user_id": user_id},
            )
            data, err = safe_request(res)
            if data:
                st.success(f"Audio Ingested: {data.get('filename', '')}")
            else:
                st.error(f"Error: {err}")

    # -------------------- IMAGE --------------------
    elif modality == "Image":
        uploaded_image = st.file_uploader("Upload Image (.png, .jpg, .jpeg)",
                                          type=["png", "jpg", "jpeg"])
        if st.button("Ingest Image") and uploaded_image:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/image",
                files={"file": uploaded_image},
                params={"user_id": user_id},
            )
            data, err = safe_request(res)
            if data:
                st.success(f"Image Ingested: {data.get('filename', '')}")
            else:
                st.error(f"Error: {err}")

    # -------------------- WEB URL --------------------
    elif modality == "Web URL":
        url = st.text_input("Enter Web URL")
        if st.button("Ingest Web Content") and url:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/web",
                json={"url": url, "user_id": user_id},
            )
            data, err = safe_request(res)
            if data:
                st.success(f"Web Content Ingested: {url}")
            else:
                st.error(f"Error: {err}")

    # -------------------- TEXT --------------------
    elif modality == "Plain Text":
        text = st.text_area("Enter Text")
        if st.button("Ingest Text") and text:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/text",
                json={"text": text, "title": "Manual Text", "user_id": user_id},
            )
            data, err = safe_request(res)
            if data:
                st.success("Text Ingested Successfully")
            else:
                st.error(f"Error: {err}")

    # -------------------- CHAT / RAG --------------------
    st.write("---")
    st.header("💬 Chat with Your Second Brain")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.text_input("Ask your AI companion:", key="chat_input")

    if st.button("Send") and query:
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{BACKEND_URL}/api/rag",
                json={"query": query, "user_id": user_id, "top_k": 5},
            )
            data, err = safe_request(res)
            if data:
                st.session_state.chat_history.append({
                    "user": query,
                    "ai": data.get("answer", "No answer found."),
                    "sources": data.get("sources", [])
                })
            else:
                st.error(err)

    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**AI:** {chat['ai']}")
        if chat["sources"]:
            with st.expander("Sources / Context"):
                for idx, src in enumerate(chat["sources"], 1):
                    st.markdown(f"{idx}. {src}")


# ---------------------------------------------
# ROUTING LOGIC
# ---------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
else:
    show_app()
