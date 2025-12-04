import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Second Brain AI Companion",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = os.getenv("BACKEND_URL", "https://twinmind-assignment-4.onrender.com")


# ==========================================================
# SAFE JSON PARSER
# ==========================================================
def safe_request(res):
    try:
        return res.json(), None
    except:
        return None, res.text[:1000]


# ==========================================================
# AUTH HELPERS
# ==========================================================
def login_user(username, password):
    res = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    return safe_request(res)


def register_user(username, email, password):
    res = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"username": username, "email": email, "password": password}
    )
    return safe_request(res)


def logout_user():
    st.session_state.pop("token", None)
    st.session_state.pop("username", None)


# ==========================================================
# LOGIN / SIGNUP UI
# ==========================================================
def show_login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data, err = login_user(username, password)
        if data:
            st.session_state["token"] = data["access_token"]
            st.session_state["username"] = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(f"❌ Login failed: {err}")


def show_signup_page():
    st.title("📝 Create Account")

    username = st.text_input("Username (min 3 chars)")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        data, err = register_user(username, email, password)
        if data:
            st.success("🎉 Account created! Please login.")
        else:
            st.error(f"❌ Signup failed: {err}")


# ==========================================================
# MAIN APPLICATION UI
# ==========================================================
def show_app():
    token = st.session_state.get("token", None)
    username = st.session_state.get("username", None)

    st.sidebar.write(f"👤 Logged in as **{username}**")
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

    st.title("🧠 Second Brain AI Companion")
    st.header("Ingest Data")

    headers = {"Authorization": f"Bearer {token}"}
    user_id = username

    modality = st.selectbox(
        "Choose modality to ingest:",
        ["Document", "Audio", "Image", "Web URL", "Plain Text"]
    )

    # =====================================================
    # DOCUMENT INGESTION
    # =====================================================
    if modality == "Document":
        uploaded_file = st.file_uploader("Upload Document (.pdf, .md, .txt)", type=["pdf", "md", "txt"])
        if st.button("Ingest Document") and uploaded_file:
            files = {"file": uploaded_file}
            res = requests.post(f"{BACKEND_URL}/api/ingest/upload", files=files, params={"user_id": user_id}, headers=headers)
            data, err = safe_request(res)
            if data:
                st.success(f"Document Ingested: {data.get('filename')}")
            else:
                st.error(err)

    # =====================================================
    # AUDIO INGESTION
    # =====================================================
    elif modality == "Audio":
        audio_file = st.file_uploader("Upload Audio (.mp3, .m4a)", type=["mp3", "m4a"])
        if st.button("Ingest Audio") and audio_file:
            files = {"file": audio_file}
            res = requests.post(f"{BACKEND_URL}/api/ingest/audio", files=files, params={"user_id": user_id}, headers=headers)
            data, err = safe_request(res)
            if data:
                st.success(f"Audio processed!")
            else:
                st.error(err)

    # =====================================================
    # IMAGE INGESTION
    # =====================================================
    elif modality == "Image":
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if st.button("Ingest Image") and img_file:
            files = {"file": img_file}
            res = requests.post(f"{BACKEND_URL}/api/ingest/image", files=files, params={"user_id": user_id}, headers=headers)
            data, err = safe_request(res)
            if data:
                st.success("Image processed!")
            else:
                st.error(err)

    # =====================================================
    # WEB URL INGESTION
    # =====================================================
    elif modality == "Web URL":
        url = st.text_input("Enter Web URL")
        if st.button("Ingest Web Content") and url:
            res = requests.post(f"{BACKEND_URL}/api/ingest/web", json={"url": url, "user_id": user_id}, headers=headers)
            data, err = safe_request(res)
            if data:
                st.success("Web content ingested!")
            else:
                st.error(err)

    # =====================================================
    # TEXT INGESTION
    # =====================================================
    elif modality == "Plain Text":
        txt = st.text_area("Enter Text")
        if st.button("Ingest Text") and txt:
            res = requests.post(f"{BACKEND_URL}/api/ingest/text", json={"text": txt, "title": "Manual Text", "user_id": user_id}, headers=headers)
            data, err = safe_request(res)
            if data:
                st.success("Text ingested!")
            else:
                st.error(err)

    st.markdown("---")
    st.header("💬 Chat with RAG")

    query = st.text_input("Ask something…")

    if st.button("Send"):
        res = requests.post(
            f"{BACKEND_URL}/api/rag",
            json={"query": query, "user_id": user_id, "top_k": 5},
            headers=headers
        )
        data, err = safe_request(res)
        if data:
            st.write("**AI:**", data.get("answer"))
        else:
            st.error(err)


# ==========================================================
# ROUTING LOGIC
# ==========================================================
page = st.sidebar.selectbox("Navigation", ["Login", "Sign Up", "App"])

if page == "Login":
    if "token" in st.session_state:
        st.switch_page("App")
    show_login_page()

elif page == "Sign Up":
    show_signup_page()

else:
    if "token" not in st.session_state:
        st.error("Please login first!")
    else:
        show_app()
