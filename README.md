# RAG365 Enterprise

RAG365 is an enterprise-grade Retrieval-Augmented Generation (RAG) platform designed for trustworthy, scalable, and secure AI-driven knowledge retrieval. It transforms a monolithic RAG system into a modular microservices architecture using the **Strangler Fig migration strategy**.

## 🚀 Key Features

- **Trustworthy AI**: Precise citations with page numbers and text snippets to eliminate hallucinations.
- **Hybrid Search**: Fuses Vector Similarity (S3 Vectors) with Keyword Search (BM25) using Reciprocal Rank Fusion (RRF).
- **Enterprise Security**: Role-Based Access Control (RBAC), tenant isolation, and comprehensive audit logging.
- **Real-time Ingestion**: Asynchronous document processing pipeline with sub-2-minute indexing latency.
- **Advanced Document Understanding**: Extraction of text, tables (markdown), and image captions from complex PDFs.
- **Agentic Reasoning**: Multi-step reasoning using LangGraph-based agents for complex queries.
- **Multi-language Support**: Auto-detection and translation for 10+ languages.
- **Observability**: Distributed tracing, SLO monitoring, and per-tenant cost attribution.

## 🛠 Tech Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), SQLAlchemy
- **AI/LLM**: AWS Bedrock (Claude 3, Llama 3)
- **Database**: PostgreSQL (Relational + BM25), S3 Vectors (Isolated Retrieval)
- **Infrastructure**: AWS (SQS, Lambda, S3, ECS Fargate, API Gateway, Redis)
- **Observability**: OpenTelemetry, CloudWatch

## 📂 Project Structure

```text
.
├── backend/                # Monolithic FastAPI Backend (being extracted)
├── frontend/
│   └── rag-admin-frontend/ # Next.js Admin Dashboard
├── services/
│   ├── auth-service/       # Identity & RBAC (Microservice)
│   ├── chat-service/       # Conversation Management (Microservice)
│   ├── indexing-service/   # Document Processing & Indexing (Microservice)
│   ├── rag_engine/         # Core RAG Orchestration & Retrieval
│   └── ...                 # Other extracted microservices
├── infrastructure/         # Deployment scripts, Docker, and K8s configs
├── common/                 # Shared schemas, utils, and configurations
└── database/               # Shared database models and CRUD operations
```

## 🚥 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- AWS CLI configured with Bedrock/S3/SQS access

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file (see `.env.example`).
5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend/rag-admin-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 🏗 Roadmap

- [x] **Phase 1**: Core RAG with citations and basic indexing.
- [ ] **Phase 2**: RBAC, Monitoring, and Cost Tracking.
- [ ] **Phase 3**: Hybrid Search (BM25 + Vector) and Cross-Encoder Re-ranking.
- [ ] **Phase 4**: Multi-source connectors (SharePoint, Confluence, GDrive).
- [ ] **Phase 5**: Agentic RAG with LangGraph orchestration.

## 📜 License

This project is proprietary. All rights reserved.
