# KnowledgeAI — RAG Knowledge Assistant

A full-stack **Retrieval-Augmented Generation** application that lets you upload PDFs or YouTube videos and ask intelligent questions about them with cited answers.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │  Dashboard  │  │    Chat    │  │  Toast / Layout / UI   │ │
│  │  Upload PDF │  │ Ask Qs    │  │  Components            │ │
│  │  Add YouTube│  │ Citations │  │                        │ │
│  └─────┬──────┘  └─────┬──────┘  └────────────────────────┘ │
│        │               │           Axios API Service        │
└────────┼───────────────┼────────────────────────────────────┘
         │  HTTP / REST  │
┌────────┼───────────────┼────────────────────────────────────┐
│        ▼               ▼        Backend (FastAPI)           │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Upload   │  │   Chat/Ask   │  │    Middleware           │ │
│  │  Routes   │  │   Route      │  │  (CORS, Error Handler) │ │
│  └─────┬─────┘  └──────┬──────┘  └────────────────────────┘ │
│        ▼               ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Modules                             │   │
│  │  PDF Processor · YouTube Processor · Chunker          │   │
│  │  Embedder (Gemini) · Vector Store (Qdrant)            │   │
│  │  RAG Pipeline (Gemini 1.5 Flash)                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
   ┌──────────┐                  ┌──────────────┐
   │  Qdrant  │                  │  Google       │
   │  Cloud   │                  │  Gemini API   │
   └──────────┘                  └──────────────┘
```

## Prerequisites

| Tool      | Version | Purpose               |
| --------- | ------- | --------------------- |
| Python    | 3.11+   | Backend runtime       |
| Node.js   | 20+     | Frontend tooling      |
| npm       | 9+      | Package manager       |
| Docker    | 24+     | Container deployment  |
| Git       | 2.40+   | Version control       |

**External Services:**
- [Google AI Studio](https://aistudio.google.com/) — Gemini API key
- [Qdrant Cloud](https://cloud.qdrant.io/) — vector database cluster

## Local Setup

### 1. Clone and navigate

```bash
git clone https://github.com/your-username/ContextAwareKnowledgeAssistant.git
cd ContextAwareKnowledgeAssistant
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app

Navigate to **http://localhost:5173** — upload a PDF or YouTube video, then ask questions in the Chat tab.

## Environment Variables

| Variable          | Required | Description                      | Where to get it                    |
| ----------------- | -------- | -------------------------------- | ---------------------------------- |
| `GEMINI_API_KEY`  | Yes      | Google Gemini API key            | [Google AI Studio](https://aistudio.google.com/) |
| `QDRANT_URL`      | Yes      | Qdrant Cloud cluster URL         | [Qdrant Cloud](https://cloud.qdrant.io/) |
| `QDRANT_API_KEY`  | Yes      | Qdrant Cloud API key             | Qdrant Cloud dashboard → API Keys |
| `COLLECTION_NAME` | No       | Qdrant collection name           | Default: `knowledge_base`         |
| `CORS_ORIGIN`     | No       | Allowed CORS origin              | Default: `http://localhost:5173`   |
| `VITE_API_URL`    | No       | Backend API URL (frontend)       | Default: `/api` (proxied by Vite)  |

## API Endpoints

| Method   | Endpoint                        | Description                    |
| -------- | ------------------------------- | ------------------------------ |
| `POST`   | `/api/upload/pdf`               | Upload a PDF document          |
| `POST`   | `/api/upload/youtube`           | Import a YouTube transcript    |
| `GET`    | `/api/upload/sources`           | List all ingested sources      |
| `DELETE` | `/api/upload/source/{name}`     | Delete a source and its chunks |
| `POST`   | `/api/chat/ask`                 | Ask a question (RAG pipeline)  |
| `GET`    | `/health`                       | Health check                   |

## Docker Deployment

```bash
# Start both services
docker compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Production Deployment

### Backend → Render

1. Push your repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New Web Service**
3. Connect the repo, set **Root Directory** to `backend`
4. Render will auto-detect `render.yaml`
5. Add environment variables in the Render dashboard

### Frontend → Vercel

1. Go to [Vercel](https://vercel.com/) → **New Project**
2. Import the repo, set **Root Directory** to `frontend`
3. Set **Build Command**: `npm run build`
4. Set **Output Directory**: `dist`
5. Add env variable: `VITE_API_URL=https://your-backend.onrender.com/api`
6. `vercel.json` handles SPA rewrites automatically

> **Important:** Update `CORS_ORIGIN` in your Render backend to match your Vercel frontend URL.

## Tech Stack

| Layer     | Technology                                   |
| --------- | -------------------------------------------- |
| Frontend  | React 19, TypeScript, Vite 6, Tailwind CSS 4 |
| Backend   | FastAPI, Python 3.11, Pydantic v2            |
| AI/LLM    | Google Gemini 1.5 Flash                      |
| Embeddings| Google Gemini Embedding                      |
| Vector DB | Qdrant Cloud                                 |
| Deploy    | Vercel (frontend) + Render (backend)         |

## Team

Built by **Sibtain** — [GitHub](https://github.com/sibtainwrites)

## License

This project is licensed under the [MIT License](LICENSE).
