# 🧠 Second Brain AI Companion

A multi-modal Retrieval-Augmented Generation (RAG) application powered by FastAPI (backend) and Streamlit (frontend).  
Supports document, audio, image, web, and text ingestion, semantic search, and Gemini-powered answers with user authentication.

---

## 🚀 Features

- **User Authentication:** Register and login with secure JWT tokens.
- **Multi-Modal Ingestion:** Upload and process documents (PDF, TXT, MD), audio files (MP3, M4A), images (PNG, JPG, JPEG), web URLs, and plain text.
- **Semantic Search:** Uses FAISS and embeddings for fast, relevant retrieval.
- **RAG Chatbot:** Ask questions and get context-aware answers from your personal knowledge base.
- **Gemini LLM Integration:** Answers are generated using Google Gemini (or your configured LLM).
- **Clean UI:** Streamlit frontend with a guided flow (login → register → app).
- **Extensible:** Modular backend for easy addition of new modalities or models.

---

## 🗂️ Project Structure

```
ASSIGNMENT_TWINMIND/
│
├── TWINMIND-backend/
│   ├── app/
│   │   ├── auth/              # Authentication logic
│   │   ├── database/          # DB connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # FastAPI routes
│   │   ├── services/          # Embedding, FAISS, ingestion, LLM
│   │   ├── utils/             # Chunking and helpers
│   │   └── main.py            # FastAPI entrypoint
│   ├── migrations/            # Alembic migrations
│   ├── requirements.txt
│   └── .env                   # Environment variables (not committed)
│
├── TWINMIND-frontend/
│   └── streamlit_app.py       # Streamlit UI
│
├── .gitignore
└── README.md
```

---

## ⚡ Quickstart

### 1. Clone the Repository

```sh
git clone https://github.com/<your-username>/<your-repo-name>.git
cd ASSIGNMENT_TWINMIND
```

### 2. Backend Setup

```sh
cd TWINMIND-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Set up your .env file (see below)
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```sh
cd ../TWINMIND-frontend
pip install streamlit requests
streamlit run streamlit_app.py
```

---

## 🔑 Environment Variables (`.env` Example)

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/twinmind_db
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## 📝 Usage Flow

1. **Login:** Start at the login page.
2. **Register:** If login fails, register a new account.
3. **App:** After login, access ingestion and chat features.
4. **Ingest Data:** Upload documents, audio, images, web URLs, or text.
5. **Chat:** Ask questions and get answers based on your ingested data.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, FAISS, Google Gemini API
- **Frontend:** Streamlit
- **Database:** PostgreSQL (with pgvector for embeddings)
- **Audio:** OpenAI Whisper for transcription
- **Image:** Tesseract OCR for text extraction

---

## 📦 Extending the App

- Add new ingestion processors in `app/services/ingestion/`.
- Swap LLMs in `app/services/llm/`.
- Add new routes in `app/routes/`.

---

## 🧪 Testing

- Backend: Use pytest for unit/integration tests.
- Frontend: Manual testing via Streamlit UI.

---

## 🗄️ Data Privacy

- Uploaded files are stored locally in `uploads/` and `temp_audio/` (excluded from git).
- User authentication uses JWT tokens.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📚 License

MIT License

---

## 💡 Credits

Developed for the TwinMind Assignment by Ishvit Khajuria and contributors.

---

## ❓ FAQ

**Q: How do I reset my password?**  
A: Currently, password reset is not implemented.

**Q: Can I use another LLM?**  
A: Yes! Swap out Gemini for any LLM in `app/services/llm/`.

**Q: How do I add a new data modality?**  
A: Add a new processor in `app/services/ingestion/` and update the frontend.

---

## 🏁 Ready to build your Second Brain!