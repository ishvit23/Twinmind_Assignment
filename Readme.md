# 🧠 Second Brain AI Companion

A fully multi-modal Retrieval-Augmented Generation (RAG) system powered by FastAPI, Streamlit, PostgreSQL + pgvector, FAISS, and Google Gemini AI (Vision + Audio + Text).

Users can upload documents, images, audio, URLs, or text, and the system automatically extracts text, embeds it, stores it, indexes it, and uses it for semantic search + RAG answering.

---

## ✨ Features

- **User Authentication (JWT)** - Secure login and registration system
- **Multi-Modal Ingestion** - Support for documents, images, audio, URLs, and text
- **Image OCR via Gemini Vision** - Extract text from images automatically
- **Audio Transcription via Gemini** - Convert audio files to searchable text
- **Semantic Search with FAISS** - Fast and accurate vector similarity search
- **RAG Chatbot using Gemini** - Context-aware question answering with sources
- **Streamlit Frontend** - Intuitive and responsive user interface
- **Modular Backend Architecture** - Clean, maintainable, and extensible codebase

---

## 📁 Project Structure

```
ASSIGNMENT_TWINMIND/
│
├── TWINMIND-backend/
│   ├── app/
│   │   ├── auth/                 # Authentication logic
│   │   ├── database/             # Database configuration
│   │   ├── models/               # Data models
│   │   ├── routes/               # API endpoints
│   │   ├── services/
│   │   │   ├── ingestion/        # Data ingestion processors
│   │   │   ├── llm/              # LLM integration
│   │   │   ├── embedding/        # Text embedding service
│   │   │   └── faiss/            # FAISS vector indexing
│   │   └── main.py               # FastAPI application entry point
│   ├── uploads/                  # Uploaded files storage
│   ├── requirements.txt
│   └── .env
│
├── TWINMIND-frontend/
│   └── streamlit_app.py          # Streamlit UI application
│
└── README.md
```

---

## 🚀 Backend Setup

```bash
cd TWINMIND-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

---

## 🎨 Frontend Setup

```bash
cd TWINMIND-frontend
pip install streamlit requests
streamlit run streamlit_app.py
```

The frontend interface will be available at `http://localhost:8501`

---

## ⚙️ Environment Variables

Create a `.env` file in the `TWINMIND-backend` directory with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/second_brain
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

---

## 🔄 Workflow

1. **Login / Signup** - Create an account or authenticate
2. **Ingest Data** - Upload documents, images, audio, URLs, or paste text
3. **Chunk + Embed** - System automatically processes and embeds content
4. **FAISS Index** - Creates searchable vector index
5. **RAG Chat with Sources** - Ask questions and get answers with citations

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Backend REST API framework |
| **Streamlit** | Frontend web application |
| **PostgreSQL + pgvector** | Database with vector storage |
| **FAISS** | Efficient similarity search |
| **SentenceTransformers** | Text embedding generation |
| **Gemini LLM + Vision + Audio** | Multi-modal AI processing |

---

## ❓ FAQ

**Q: Can I use GPT-4 instead of Gemini?**  
A: Yes — replace the LLM service in `app/services/llm/` with your preferred provider.

**Q: How to add a new modality?**  
A: Create a new processor in `app/services/ingestion/` following the existing pattern.

**Q: Does this support local LLMs?**  
A: Yes, you can integrate local models by modifying the LLM service layer.

**Q: How is data security handled?**  
A: User authentication via JWT tokens and per-user data isolation in the database.

---

## 📝 License

This project is open-source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using AI-powered technologies**
