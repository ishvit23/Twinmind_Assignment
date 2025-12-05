
Second Brain AI Companion

A fully multi-modal Retrieval-Augmented Generation (RAG) system powered by FastAPI, Streamlit, PostgreSQL + pgvector, FAISS, and Google Gemini AI (Vision + Audio + Text).

Users can upload documents, images, audio, URLs, or text, and the system automatically extracts text, embeds it, stores it, indexes it, and uses it for semantic search + RAG answering.

------------------------------------------------------------

FEATURES

• User Authentication (JWT)  
• Multi-Modal Ingestion  
• Image OCR via Gemini Vision  
• Audio Transcription via Gemini  
• Semantic Search with FAISS  
• RAG Chatbot using Gemini  
• Streamlit Frontend  
• Modular Backend Architecture  

------------------------------------------------------------

PROJECT STRUCTURE

ASSIGNMENT_TWINMIND/
│
├── TWINMIND-backend/
│   ├── app/
│   │   ├── auth/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   ├── llm/
│   │   │   ├── embedding/
│   │   │   └── faiss/
│   │   └── main.py
│   ├── uploads/
│   ├── requirements.txt
│   └── .env
│
├── TWINMIND-frontend/
│   └── streamlit_app.py
│
└── README.md

------------------------------------------------------------

BACKEND SETUP

cd TWINMIND-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

------------------------------------------------------------

FRONTEND SETUP

cd TWINMIND-frontend
pip install streamlit requests
streamlit run streamlit_app.py

------------------------------------------------------------

ENVIRONMENT VARIABLES

DATABASE_URL=
SECRET_KEY=
GEMINI_API_KEY=

------------------------------------------------------------

WORKFLOW

1. Login / Signup  
2. Ingest Data  
3. Chunk + Embed  
4. FAISS Index  
5. RAG Chat with Sources  

------------------------------------------------------------

TECH STACK

• FastAPI  
• Streamlit  
• PostgreSQL + pgvector  
• FAISS  
• SentenceTransformers  
• Gemini LLM + Vision + Audio  

------------------------------------------------------------

FAQ

Q: Can I use GPT-4 instead of Gemini?  
A: Yes — replace the LLM service.

Q: How to add new modal?  
A: Create a processor in app/services/ingestion.

------------------------------------------------------------
