# CREA OSS Platform

**Open-Source Chatbot + RAG + Game-Theory Dispute Resolution Platform**

A modern, production-ready platform combining conversational AI with fair division algorithms for dispute resolution. Built entirely on open-source technologies.

## 🌟 Features

### Core Capabilities

- **💬 Conversational AI**
  - Multi-backend LLM support (HuggingFace, TGI, vLLM, llama.cpp)
  - Streaming responses
  - Context-aware conversations with Redis-backed history
  - Fine-tuning data collection and export

- **📚 RAG (Retrieval-Augmented Generation)**
  - Document ingestion and chunking
  - Open-source embeddings (sentence-transformers)
  - Qdrant vector database integration
  - Semantic search with configurable relevance thresholds

- **⚖️ Game-Theory Algorithms**
  - **Max-Min Fairness**: Maximize minimum agent utility
  - **Nash Social Welfare**: Maximize product of weighted utilities
  - Support for entitlements, restrictions, and budgets
  - Real-time dispute resolution with explanations

- **⚡ Performance & Scalability**
  - Semantic caching (Redis)
  - Background task processing (Celery)
  - Async database operations (SQLAlchemy + asyncpg)
  - Docker-based deployment

- **🎯 Model Management**
  - Swap between base and fine-tuned models
  - Multi-tenant model configurations
  - Support for local and remote inference

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                       │
├─────────────────┬──────────────┬─────────────┬──────────────┤
│   ChatService   │  RAGService  │ LLMService  │ OptimizerSvc │
├─────────────────┴──────────────┴─────────────┴──────────────┤
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌───────────┐ │
│  │  Redis   │  │  Qdrant    │  │   LLM    │  │Algorithm  │ │
│  │  Cache   │  │  Vector DB │  │ Backends │  │  Solvers  │ │
│  └──────────┘  └────────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
              ┌──────────────────────────┐
              │    PostgreSQL Database    │
              └──────────────────────────┘
```

### Components

1. **Backend** (FastAPI)
   - RESTful API endpoints
   - Async request handling
   - Pydantic validation
   - Structured logging

2. **LLM Layer**
   - Modular backend abstraction
   - Support for multiple open-source models
   - Configurable generation parameters

3. **RAG Pipeline**
   - Document chunking and embedding
   - Vector similarity search
   - Context injection into prompts

4. **Game-Theory Solvers**
   - SciPy-based optimization
   - Constraint handling
   - Fair allocation computation

5. **Caching & Workers**
   - Semantic prompt caching
   - Background document processing
   - Training data export

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- 8GB+ RAM recommended

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd crea-oss-platform
```

2. **Configure environment**

```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose**

```bash
cd ../infra
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)
- FastAPI backend (port 8000)
- Celery worker

4. **Initialize database** (first time only)

```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the API**

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant UI: http://localhost:6333/dashboard

## 📖 Usage

### Chat API

Send a message to the chatbot:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is max-min fairness allocation?",
    "session_id": "user-123",
    "use_rag": true
  }'
```

### Create a Dispute

```bash
curl -X POST "http://localhost:8000/api/v1/disputes/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Inheritance Dispute",
    "resolution_method": "ratings",
    "agents": [
      {"email": "alice@example.com", "name": "Alice", "share_of_entitlement": 0.5},
      {"email": "bob@example.com", "name": "Bob", "share_of_entitlement": 0.5}
    ],
    "goods": [
      {"name": "House", "estimated_value": 300000, "indivisible": true},
      {"name": "Savings", "estimated_value": 50000, "indivisible": false}
    ]
  }'
```

### Solve a Dispute

```bash
curl -X POST "http://localhost:8000/api/v1/disputes/1/solve" \
  -H "Content-Type: application/json" \
  -d '{"method": "maxmin"}'
```

### Upload Documents for RAG

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@legal_document.txt" \
  -F "title=Legal Precedent Document" \
  -F "category=laws"
```

## 🎓 Model Configuration

### Using Different LLM Backends

#### 1. HuggingFace Local (Default)

```python
# In .env
DEFAULT_LLM_BACKEND=hf_local
DEFAULT_MODEL_ID=mistralai/Mistral-7B-Instruct-v0.2
HF_DEVICE=cuda  # or cpu
```

#### 2. Text Generation Inference (TGI)

```bash
# Start TGI server
docker run -p 8080:80 \
  -v $PWD/models:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id mistralai/Mistral-7B-Instruct-v0.2
```

```python
# In .env
DEFAULT_LLM_BACKEND=tgi
TGI_URL=http://localhost:8080
```

#### 3. vLLM

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --port 8000
```

```python
# In .env
DEFAULT_LLM_BACKEND=vllm
VLLM_URL=http://localhost:8000
```

### Fine-Tuning Integration

1. **Collect training data**

```bash
# Export conversations with rating >= 4
curl -X POST "http://localhost:8000/api/v1/admin/export-training-data?min_rating=4"
```

2. **Train your model** (external process)

Use the exported JSONL with your preferred fine-tuning framework (e.g., LoRA, QLoRA).

3. **Register the fine-tuned model**

```bash
curl -X POST "http://localhost:8000/api/v1/models/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dispute-finetuned-v1",
    "model_id": "path/to/finetuned-model",
    "backend_type": "hf_local",
    "is_finetuned": true,
    "base_model_id": "mistralai/Mistral-7B-Instruct-v0.2"
  }'
```

4. **Use the fine-tuned model**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -d '{
    "message": "Analyze this dispute...",
    "session_id": "user-123",
    "model_id": "path/to/finetuned-model"
  }'
```

## 🧪 Testing

```bash
cd backend

# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## 📁 Project Structure

```
crea-oss-platform/
├── backend/
│   ├── app/
│   │   ├── algorithms/      # Game-theory solvers
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Config, logging, database
│   │   ├── llm_backends/    # LLM backend implementations
│   │   ├── models/          # SQLAlchemy models
│   │   ├── rag/             # RAG components
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── workers/         # Celery tasks
│   │   └── main.py          # FastAPI app
│   ├── tests/               # Tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── .env.example
├── infra/
│   ├── docker-compose.yml
│   └── Dockerfile.backend
├── docs/                    # Additional documentation
└── README.md
```

## 🔧 Configuration Reference

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_HOST` | Redis host | `localhost` |
| `QDRANT_URL` | Qdrant endpoint | `http://localhost:6333` |
| `DEFAULT_MODEL_ID` | Default LLM model | `mistralai/Mistral-7B-Instruct-v0.2` |
| `EMBEDDING_MODEL` | Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CACHE_ENABLED` | Enable semantic caching | `true` |
| `RAG_TOP_K` | Number of RAG results | `5` |

See `.env.example` for full configuration options.

## 🎯 Algorithms

### Max-Min Fairness

Maximizes the minimum utility across all agents:

```
maximize   t
subject to:
  - For each agent i: Σ(x_ij × u_ij) ≥ t
  - For each good j: Σ(x_ij) ≤ 1
  - Budget: Σ(x_ij × v_j) ≤ B
  - x_ij ≥ 0
```

### Nash Social Welfare

Maximizes the product of agent utilities weighted by entitlements:

```
maximize   Π(U_i ^ w_i)
subject to:
  - For each good j: Σ(x_ij) ≤ 1
  - Budget: Σ(x_ij × v_j) ≤ B
  - x_ij ≥ 0
```

Where:
- `x_ij`: allocation of good j to agent i
- `u_ij`: utility of good j for agent i
- `w_i`: entitlement weight of agent i
- `v_j`: value of good j
- `B`: total budget

## 🛣️ Roadmap

- [ ] Authentication & authorization (JWT)
- [ ] Multi-tenancy support
- [ ] React/TypeScript frontend
- [ ] Streaming chat responses in UI
- [ ] Enhanced document parsing (PDF, DOCX)
- [ ] Graph-based dispute visualization
- [ ] Explanation generation for allocations
- [ ] Integration with external knowledge bases

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📄 License

[Specify your license here]

## 🙏 Acknowledgments

Built with:
- FastAPI
- HuggingFace Transformers
- Qdrant
- SciPy
- SQLAlchemy
- Redis
- Celery

---

**Note**: This is a framework designed for extensibility. All LLM and embedding models are open-source and can be swapped based on your requirements.
