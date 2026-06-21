# CREA2 Platform - Architecture Documentation

## Executive Summary

This document describes the architecture of the CREA2 Fair Division Platform, a complete rebuild of the legacy ASP.NET Core application using modern Python and React technologies.

### Technology Stack

**Backend:**
- FastAPI (Python 3.12+)
- PostgreSQL (database)
- SQLAlchemy / SQLModel (ORM)
- Redis (caching & message broker)
- Celery (async task queue)
- OR-Tools (optimization engine)
- JWT (authentication)

**Frontend:**
- React 18
- TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Query (data fetching)
- Zustand (state management)
- React Router (routing)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (frontend serving)
- PostgreSQL (persistent data)
- Redis (cache & broker)

---

## System Overview

The CREA2 platform enables users to solve fair division problems through an intuitive web interface backed by powerful optimization algorithms.

### Core Domain

**Dispute**: Central entity representing a fair division problem
- Owner: User who created the dispute
- Agents: Participants in the division
- Goods: Items to be divided
- Status: Workflow state (Setting Up → Bidding → Finalizing → Finalized/Rejected)
- Resolution Method: Bids (monetary) or Ratings (1-5 stars)

**Agent**: Participant in a dispute
- Linked to a User account (or invited by email)
- Share of entitlement (custom percentage or equal split)
- Validation status (tracks agreement through workflow)

**Good**: Item to be divided
- Name and estimated value
- Divisible or indivisible
- Associated utilities from each agent

**AgentUtility**: Polymorphic entity representing agent preferences
- **Bid**: Monetary bid value within bounds of estimated value
- **Rate**: Star rating (1-5) converted to utility via formula

**RestrictedAssignment**: Constraint on agent-good pairs
- Limits maximum share an agent can receive of a specific good

---

## Architecture Diagram

```
┌─────────────────┐
│   React SPA     │
│  (TypeScript)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI        │
│  (Python)       │
├─────────────────┤
│ • Auth Routes   │
│ • Dispute CRUD  │
│ • Solution API  │
└────┬────────┬───┘
     │        │
     ▼        ▼
┌─────────┐  ┌──────────┐
│PostgreSQL│  │  Redis   │
│         │  │ (Cache)  │
└─────────┘  └────┬─────┘
                  │
                  ▼
            ┌──────────┐
            │  Celery  │
            │  Worker  │
            └──────────┘
```

---

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Settings & configuration
│   │   └── security.py         # Auth & JWT utils
│   ├── db/
│   │   ├── base.py             # Import all models
│   │   └── session.py          # DB session management
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── dispute.py
│   │   ├── agent.py
│   │   ├── good.py
│   │   ├── agent_utility.py
│   │   ├── restricted_assignment.py
│   │   └── conversation.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── dispute.py
│   │   ├── agent.py
│   │   ├── good.py
│   │   └── solution.py
│   ├── api/routes/             # API endpoints
│   │   ├── auth.py             # Login, register, verify email
│   │   └── disputes.py         # Dispute CRUD & workflows
│   ├── services/               # Business logic
│   │   ├── optimizer.py        # OR-Tools fair division solver
│   │   ├── email_service.py    # Email sending (Mailjet)
│   │   └── blockchain_service.py # Optional blockchain anchoring
│   └── workers/
│       └── tasks.py            # Celery async tasks
├── alembic/                    # Database migrations
├── tests/                      # Pytest tests
├── requirements.txt
├── Dockerfile
└── .env.example
```

### API Endpoints

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Create new user account | No |
| POST | `/login` | Login and get JWT tokens | No |
| POST | `/refresh` | Refresh access token | No |
| POST | `/verify-email` | Verify email with token | No |
| POST | `/request-password-reset` | Request password reset | No |
| POST | `/reset-password` | Reset password with token | No |

#### Disputes (`/api/v1/disputes`)

| Method | Endpoint | Description | Auth Required | Authorization |
|--------|----------|-------------|---------------|---------------|
| POST | `/` | Create dispute | Yes | Any user |
| GET | `/` | List user's disputes | Yes | Owner or Agent |
| GET | `/{id}` | Get dispute details | Yes | Owner or Agent |
| PUT | `/{id}` | Update dispute | Yes | Owner only |
| DELETE | `/{id}` | Delete dispute | Yes | Owner only |
| POST | `/{id}/validate` | Validate setup phase | Yes | Agent |
| POST | `/{id}/solve` | Run optimization | Yes | Owner |
| POST | `/{id}/finalize` | Accept solution | Yes | Agent |
| POST | `/{id}/reject` | Reject solution | Yes | Agent |

### Database Schema

**PostgreSQL Tables:**

- `users` - User accounts with hashed passwords
- `roles` - User roles (admin, manager)
- `user_roles` - Many-to-many user-role association
- `disputes` - Fair division problems
- `agents` - Dispute participants
- `goods` - Items to divide
- `agent_utilities` - Polymorphic table (TPT pattern)
- `bids` - Bid-based utilities (inherits agent_utilities)
- `rates` - Rating-based utilities (inherits agent_utilities)
- `restricted_assignments` - Constraints
- `conversations` - LLM chat sessions

**Key Constraints:**

- Unique agent email per dispute
- Unique good name per dispute
- Unique bid/rate per agent-good-dispute combination
- Cascade delete for dispute removal

### Optimization Service

The `OptimizationService` uses Google OR-Tools to solve the fair division problem:

**Algorithm:**
1. Load dispute with all agents, goods, utilities, and constraints
2. Create decision variables `x[i,j]` = allocation of good j to agent i
3. Build objective function: Maximize total utility
4. Add constraints:
   - Each good fully allocated (sum of allocations = 1)
   - Indivisible goods are binary (0 or 1)
   - Budget constraints per agent (based on share of entitlement)
   - Restricted assignment bounds
5. Solve using linear programming (GLOP solver)
6. Extract allocation matrix and compute utilities

**Complexity:** O(n*m) where n=agents, m=goods

**Async Execution:** For disputes with >10 agents or goods, optimization runs as a Celery background task.

---

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── main.tsx                # App entry point
│   ├── App.tsx                 # Route configuration
│   ├── api/                    # API client functions
│   │   ├── auth.ts
│   │   └── disputes.ts
│   ├── lib/                    # Utilities
│   │   ├── auth-store.ts       # Zustand auth state
│   │   └── api-client.ts       # Axios instance with interceptors
│   ├── components/
│   │   ├── layout/             # Layout components
│   │   │   ├── MainLayout.tsx
│   │   │   └── AuthLayout.tsx
│   │   ├── auth/               # Auth-related components
│   │   ├── disputes/           # Dispute-related components
│   │   └── ui/                 # Reusable UI components
│   ├── pages/                  # Page components
│   │   ├── HomePage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── disputes/
│   │   │   ├── DisputeListPage.tsx
│   │   │   ├── DisputeCreatePage.tsx
│   │   │   ├── DisputeDetailPage.tsx
│   │   │   ├── DisputeBidsPage.tsx
│   │   │   └── DisputeSolutionPage.tsx
│   │   └── static/
│   │       ├── HelpPage.tsx
│   │       ├── ResearchPage.tsx
│   │       └── ...
│   ├── hooks/                  # Custom React hooks
│   └── types/                  # TypeScript types
├── public/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── Dockerfile
└── nginx.conf
```

### State Management

**Zustand Store (`auth-store`):**
- User profile
- Access & refresh tokens
- Authentication status
- Login/logout actions

**React Query:**
- Server state caching
- Automatic refetching
- Optimistic updates
- Mutations for CRUD operations

### Routing

**Public Routes:**
- `/` - Home page
- `/login`, `/register` - Authentication
- `/help`, `/research`, `/project`, `/contact`, `/legal-terms`, `/news` - Static content

**Protected Routes:** (require authentication)
- `/dashboard` - User dashboard
- `/disputes` - List disputes
- `/disputes/create` - Create new dispute
- `/disputes/:id` - Dispute details
- `/disputes/:id/bids` - Submit bids/ratings
- `/disputes/:id/solution` - View solution

---

## Security

### Authentication & Authorization

**JWT-Based Auth:**
- Access tokens (7 days expiry)
- Refresh tokens (30 days expiry)
- Tokens stored in Zustand persist middleware (localStorage)
- Axios interceptor automatically adds `Authorization: Bearer <token>` header

**Password Security:**
- Bcrypt hashing with automatic salt
- Minimum 8 characters
- Reset via email token (secure random, single-use)

**Role-Based Access Control:**
- **Admin**: Full system access
- **Manager**: Can manage all disputes
- **User**: Own disputes and invited disputes

**Resource-Based Authorization:**
- Dispute owners: CRUD operations
- Dispute agents: Read, bid, accept/reject
- Checked at API endpoint level via dependencies

### CORS & HTTPS

- CORS middleware configured for allowed origins
- HTTPS enforced in production (Nginx + Let's Encrypt recommended)
- Secure cookie settings in production

### Input Validation

- Pydantic schemas validate all API inputs
- SQL injection prevented by SQLAlchemy parameterization
- XSS prevented by React's auto-escaping

---

## Deployment

### Docker Compose (Local Development)

```bash
# Clone and setup
git clone <repo>
cd migrated-app

# Start all services
docker-compose up -d

# Access
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

### Production Deployment

**Recommended Stack:**
- Frontend: Nginx + static build on CDN (Vercel, Netlify, Cloudflare)
- Backend: Gunicorn + FastAPI on cloud VPS (DigitalOcean, AWS EC2)
- Database: Managed PostgreSQL (RDS, DigitalOcean Managed DB)
- Redis: Managed Redis (ElastiCache, DigitalOcean)
- Celery: Same VPS as backend or separate worker instances

**Environment Variables:**
- Store in `.env` files (development)
- Use secrets manager in production (AWS Secrets Manager, Vault)

**Database Migrations:**
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

---

## Migration Strategy

### Data Migration from Legacy System

**Phase 1: Schema Mapping**
- Map ASP.NET Identity tables to new `users` and `roles` tables
- Export dispute data from SQL Server
- Transform to PostgreSQL format

**Phase 2: User Migration**
- Export users from old system
- Import with flag for password reset (bcrypt vs old hashing)
- Send password reset emails to all users

**Phase 3: Dispute Migration**
- Export disputes, agents, goods, utilities
- Import with UUID generation
- Verify data integrity

**Script Location:** `scripts/migrate_from_legacy.py`

---

## Performance Considerations

### Optimization
- Use async/await throughout for I/O operations
- Database connection pooling (SQLAlchemy)
- Redis caching for frequently accessed data
- Celery for long-running optimizations

### Scalability
- Horizontal scaling: Run multiple API instances behind load balancer
- Database: Read replicas for queries
- Celery: Add more workers as needed

### Monitoring
- FastAPI automatic OpenAPI docs at `/docs`
- Prometheus metrics endpoint (add `prometheus-fastapi-instrumentator`)
- Logging with structured JSON logs
- Sentry for error tracking (recommended)

---

## Testing Strategy

### Backend Tests
```bash
cd backend
pytest tests/
```

**Test Coverage:**
- Unit tests: Models, services, utilities
- Integration tests: API endpoints
- E2E tests: Full workflows

### Frontend Tests
```bash
cd frontend
npm run test
```

**Test Tools:**
- Vitest for unit tests
- React Testing Library for component tests
- Playwright for E2E tests (recommended)

---

## Future Enhancements

1. **LLM Integration**: AI-powered dispute wizard and solution explanations
2. **Real-time Collaboration**: WebSockets for live updates
3. **Advanced Visualizations**: Interactive charts for allocations
4. **Mobile App**: React Native mobile client
5. **Multi-language Support**: i18n implementation
6. **Audit Logging**: Track all changes for compliance
7. **Advanced Analytics**: Dashboard for dispute statistics

---

## Support & Maintenance

**Documentation:**
- API Docs: Auto-generated at `/docs` (Swagger UI)
- Developer Docs: This file
- User Guide: `/help` page on frontend

**Version Control:**
- Main branch: Production-ready code
- Develop branch: Integration
- Feature branches: `feature/description`

**Deployment:**
- CI/CD: GitHub Actions (recommended)
- Automated testing on PR
- Deploy on merge to main

---

## Appendix

### Environment Variables Reference

See `.env.example` files in backend and frontend directories.

### API Error Codes

- 400: Bad Request (validation error)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

### License

[Insert license information]

### Contributors

[Insert contributor information]

---

**Document Version:** 1.0
**Last Updated:** 2024-01-01
**Maintainer:** CREA2 Development Team
