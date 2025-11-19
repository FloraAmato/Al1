# CREA2 Fair Division Platform

A modern, full-stack web application for solving fair division problems using optimization algorithms.

## Overview

This is a complete rebuild of the legacy ASP.NET Core / C# application, now built with:

- **Backend**: Python 3.12+ with FastAPI
- **Frontend**: React 18 with TypeScript and TailwindCSS
- **Database**: PostgreSQL
- **Cache/Broker**: Redis
- **Task Queue**: Celery
- **Optimization**: OR-Tools

## Features

- 🔐 **Secure Authentication**: JWT-based auth with email verification and password reset
- 👥 **Multi-Agent Disputes**: Create disputes with multiple participants
- 📊 **Two Resolution Methods**: Bid-based (monetary) or Rating-based (stars)
- 🎯 **Fair Allocation**: Advanced optimization algorithms ensure fairness
- 📜 **Blockchain Anchoring**: Optional tamper-proof verification
- 📧 **Email Notifications**: Automatic invitations and updates
- 🚀 **Async Processing**: Background jobs for large optimizations

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd migrated-app
   ```

2. **Configure environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings

   # Frontend (optional)
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Default Credentials

After first run, create a superuser:
```bash
docker-compose exec backend python -m app.db.init_db
```

## Project Structure

```
migrated-app/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── workers/   # Celery tasks
│   ├── alembic/       # Database migrations
│   └── tests/         # Backend tests
├── frontend/          # React frontend
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/
│   │   ├── pages/
│   │   └── lib/       # Utilities
│   └── public/
├── docs/              # Documentation
├── docker-compose.yml
└── README.md
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm run test
```

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Production Build

**Backend:**
```bash
cd backend
docker build -t crea2-backend .
```

**Frontend:**
```bash
cd frontend
npm run build
docker build -t crea2-frontend .
```

### Environment Variables

Key environment variables (see `.env.example`):

**Backend:**
- `SECRET_KEY`: JWT secret (change in production!)
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `MAILJET_API_KEY/SECRET`: Email service
- `BLOCKCHAIN_USERNAME/PASSWORD`: Blockchain anchoring

**Frontend:**
- `VITE_API_URL`: Backend API URL

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

### Key Components

1. **Authentication**: JWT-based with role-based access control
2. **Dispute Management**: Full CRUD with workflow states
3. **Optimization Engine**: OR-Tools for fair division algorithms
4. **Email Service**: Mailjet integration for notifications
5. **Background Jobs**: Celery for async optimization tasks
6. **Blockchain**: Optional anchoring for solution verification

## Migration from Legacy System

To migrate data from the old ASP.NET Core application:

1. Export data from SQL Server
2. Run migration script: `python scripts/migrate_from_legacy.py`
3. Verify data integrity

## License

[Insert License]

## Contributors

[Insert Contributors]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Email: support@crea.eu
- Documentation: http://localhost:3000/help

---

**Built with ❤️ for fair division**
