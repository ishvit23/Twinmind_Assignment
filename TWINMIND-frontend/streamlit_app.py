import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Second Brain AI Companion",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = os.getenv("BACKEND_URL", "https://twinmind-assignment-4.onrender.com")

MAX_PASSWORD_LEN = 72   # bcrypt safe limit


# ==========================================================
# SAFE JSON PARSER
# ==========================================================
def safe_request(res):
    if res is None:
        return None, "No response"
    try:
        return res.json(), None
    except:
        return None, res.text[:1000]


# ==========================================================
# AUTH HELPERS
# ==========================================================
def login_user(username, password):
    password = password[:MAX_PASSWORD_LEN]  # truncate for safety

    res = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    return safe_request(res)


def register_user(username, email, password):
    password = password[:MAX_PASSWORD_LEN]  # truncate

    res = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"username": username, "email": email, "password": password}
    )
    return safe_request(res)


def logout_user():
    st.session_state.clear()
    st.rerun()


# ==========================================================
# LOGIN UI
# ==========================================================
def show_login_page():
    st.title("🔐 Login to Second Brain")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data, err = login_user(username, password)

        if data and "access_token" in data:
            st.session_state["token"] = data["access_token"]
            st.session_state["username"] = data["username"]
            st.success("🎉 Login successful!")
            st.rerun()
        else:
            detail = (data.get("detail") if data else None) or err or "Unknown error"
            st.error(f"❌ Login failed: {detail}")


# ==========================================================
# SIGNUP UI
# ==========================================================
def show_signup_page():
    st.title("📝 Create Account")

    username = st.text_input("Username (min 3 chars)")
    email = st.text_input("Email")
    password = st.text_input("Password (max 72 chars)", type="password")

    if st.button("Sign Up"):
        if len(password) > MAX_PASSWORD_LEN:
            st.warning("Password truncated to 72 characters for security.")

        data, err = register_user(username, email, password)

        if data and data.get("status") == "success":
            st.success("🎉 Account created successfully! Please login.")
        else:
            detail = (data.get("detail") if data else None) or err or "Unknown error"
            st.error(f"❌ Signup failed: {detail}")


# ==========================================================
# MAIN PROTECTED APP
# ==========================================================
def show_app():
    token = st.session_state.get("token")
    username = st.session_state.get("username")

    st.sidebar.write(f"👤 Logged in as **{username}**")
    if st.sidebar.button("Logout"):
        logout_user()

    st.title("🧠 Second Brain AI Companion")
    st.header("Ingest Data")

    headers = {"Authorization": f"Bearer {token}"}
    user_id = username

    modality = st.selectbox(
        "Choose modality to ingest:",
        ["Document", "Audio", "Image", "Web URL", "Plain Text"]
    )

    # --- Document ---
    if modality == "Document":
        file = st.file_uploader("Upload Document (.pdf, .md, .txt)", type=["pdf", "md", "txt"])
        if st.button("Ingest Document") and file:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/upload",
                files={"file": file},
                params={"user_id": user_id},
                headers=headers
            )
            data, err = safe_request(res)
            st.success(f"📄 Document Ingested: {data.get('filename')}") if data else st.error(err)

    # --- Audio ---
    elif modality == "Audio":
        file = st.file_uploader("Upload Audio (.mp3, .m4a)", type=["mp3", "m4a"])
        if st.button("Ingest Audio") and file:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/audio",
                files={"file": file},
                params={"user_id": user_id},
                headers=headers
            )
            data, err = safe_request(res)
            st.success("🎧 Audio processed!") if data else st.error(err)

    # --- Image ---
    elif modality == "Image":
        file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if st.button("Ingest Image") and file:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/image",
                files={"file": file},
                params={"user_id": user_id},
                headers=headers
            )
            data, err = safe_request(res)
            st.success("🖼️ Image processed!") if data else st.error(err)

    # --- Web URL ---
    elif modality == "Web URL":
        url = st.text_input("Enter a Web URL")
        if st.button("Ingest Web Content") and url:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/web",
                json={"url": url, "user_id": user_id},
                headers=headers
            )
            data, err = safe_request(res)
            st.success("🌍 Web content ingested!") if data else st.error(err)

    # --- Plain Text ---
    elif modality == "Plain Text":
        text = st.text_area("Enter Text")
        if st.button("Ingest Text") and text:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/text",
                json={"text": text, "title": "Manual Text", "user_id": user_id},
                headers=headers
            )
            data, err = safe_request(res)
            st.success("📝 Text ingested!") if data else st.error(err)

    # ======================================================
    # RAG CHAT SECTION
    # ======================================================
    st.markdown("---")
    st.header("💬 Chat with your AI")

    query = st.text_input("Ask something…")

    if st.button("Send Query"):
        res = requests.post(
            f"{BACKEND_URL}/api/rag",
            json={"query": query, "user_id": user_id, "top_k": 5},
            headers=headers
        )
        data, err = safe_request(res)

        if data:
            st.subheader("🤖 AI Response")
            st.write(data.get("answer"))
        else:
            st.error(err)


# ==========================================================
# NAVIGATION
# ==========================================================
page = st.sidebar.selectbox("Navigation", ["Login", "Sign Up", "App"])

if page == "Login":
    if "token" in st.session_state:
        show_app()
    else:
        show_login_page()

elif page == "Sign Up":
    show_signup_page()

else:
    if "token" not in st.session_state:
        st.error("❌ Please login first!")
    else:
        show_app()
