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
# SAFE JSON PARSER (prevents crash on HTML / 502 pages)
# ==========================================================
def safe_request(res):
    if res is None:
        return None, "No response"

    try:
        data = res.json()
        return data, None
    except Exception:
        return None, res.text[:1000]


# ==========================================================
# MAIN APP
# ==========================================================
def show_app():
    st.title("🧠 Second Brain AI Companion")
    st.header("Ingest Data")

    modality = st.selectbox(
        "Choose modality to ingest:",
        ["Document", "Audio", "Image", "Web URL", "Plain Text"]
    )

    user_id = "demo_user"
    headers = {}

    # =====================================================
    # 📄 DOCUMENT INGESTION
    # =====================================================
    if modality == "Document":
        uploaded_file = st.file_uploader(
            "Upload Document (.pdf, .md, .txt)",
            type=["pdf", "md", "txt"]
        )

        if st.button("Ingest Document") and uploaded_file:
            files = {"file": uploaded_file}

            res = requests.post(
                f"{BACKEND_URL}/api/ingest/upload",
                files=files,
                params={"user_id": user_id},
                headers=headers
            )

            data, err = safe_request(res)
            if data:
                st.success(f"Document Ingested: {data.get('filename', '')}")
            else:
                st.error(f"❌ Backend Error {res.status_code}")
                st.code(err)

    # =====================================================
    # 🎵 AUDIO INGESTION
    # =====================================================
    elif modality == "Audio":
        uploaded_audio = st.file_uploader(
            "Upload Audio (.mp3, .m4a)",
            type=["mp3", "m4a"]
        )

        if st.button("Ingest Audio") and uploaded_audio:
            files = {"file": uploaded_audio}

            res = requests.post(
                f"{BACKEND_URL}/api/ingest/audio",
                files=files,
                params={"user_id": user_id},
                headers=headers
            )

            data, err = safe_request(res)
            if data:
                st.success(f"Audio Ingested: {data.get('filename', '')}")
            else:
                st.error(f"❌ Backend Error {res.status_code}")
                st.code(err)

    # =====================================================
    # 🖼️ IMAGE INGESTION
    # =====================================================
    elif modality == "Image":
        uploaded_image = st.file_uploader(
            "Upload Image (.png, .jpg, .jpeg)",
            type=["png", "jpg", "jpeg"]
        )

        if st.button("Ingest Image") and uploaded_image:
            files = {"file": uploaded_image}

            res = requests.post(
                f"{BACKEND_URL}/api/ingest/image",
                files=files,
                params={"user_id": user_id},
                headers=headers
            )

            data, err = safe_request(res)
            if data:
                st.success(f"Image Ingested: {data.get('filename', '')}")
            else:
                st.error(f"❌ Backend Error {res.status_code}")
                st.code(err)

    # =====================================================
    # 🌍 WEB URL INGESTION
    # =====================================================
    elif modality == "Web URL":
        url = st.text_input("Enter Web URL")

        if st.button("Ingest Web Content") and url:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/web",
                json={"url": url, "user_id": user_id},
                headers=headers
            )

            data, err = safe_request(res)
            if data:
                st.success(f"Web Content Ingested: {url}")
            else:
                st.error(f"❌ Backend Error {res.status_code}")
                st.code(err)

    # =====================================================
    # ✏️ PLAIN TEXT INGESTION
    # =====================================================
    elif modality == "Plain Text":
        text = st.text_area("Enter Text")

        if st.button("Ingest Text") and text:
            res = requests.post(
                f"{BACKEND_URL}/api/ingest/text",
                json={"text": text, "title": "Manual Text", "user_id": user_id},
                headers=headers
            )

            data, err = safe_request(res)
            if data:
                st.success("Text Ingested Successfully")
            else:
                st.error(f"❌ Backend Error {res.status_code}")
                st.code(err)

    # =====================================================
    # 💬 CHAT / RAG
    # =====================================================
    st.markdown("---")
    st.header("💬 Chat with Your Second Brain")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.text_input(
        "Ask your AI companion:",
        key="chat_input",
        placeholder="Tell me about Ishvit Khajuria."
    )

    if st.button("Send", key="send_btn") and query:
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{BACKEND_URL}/api/rag",
                json={"query": query, "user_id": user_id, "top_k": 5},
                headers=headers
            )

            data, err = safe_request(res)
            if not data:
                st.error(f"❌ Backend Error {res.status_code}")
                st.code(err)
            else:
                st.session_state.chat_history.append({
                    "user": query,
                    "ai": data.get("answer", "No answer found."),
                    "sources": data.get("sources", [])
                })

    # =====================================================
    # CHAT HISTORY DISPLAY
    # =====================================================
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**AI:** {chat['ai']}")

        if chat["sources"]:
            with st.expander("Sources / Context"):
                for idx, src in enumerate(chat["sources"], 1):
                    st.markdown(f"{idx}. {src}")

    st.markdown("---")
    st.caption("Built for Second Brain AI Companion — Multi-modal ingestion + RAG + Gemini.")


show_app()
