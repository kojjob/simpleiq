# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SimpleIQ is a cloud-native analytics and AI platform designed to democratize data intelligence for small and medium-sized enterprises (SMEs). The platform enables non-technical business users to connect their data sources, ask questions in natural language, and receive AI-powered insights without requiring data science expertise.

### Key Features
- Natural language query interface powered by Llama 3.3
- No-code data connectivity (50+ connectors)
- Drag-and-drop dashboard builder
- Automated insights and predictions
- Real-time collaboration and sharing
- Enterprise-grade security and compliance

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit + RTK Query
- **UI Components**: Ant Design + Tailwind CSS
- **Build Tool**: Vite
- **Testing**: Jest + React Testing Library + Cypress

### Backend
- **Core Services**: Node.js (TypeScript) with NestJS
- **AI/ML Services**: Python with FastAPI
- **API**: REST + GraphQL (Apollo Server)
- **Database**: PostgreSQL 15+ with TimescaleDB, ClickHouse for analytics
- **Cache**: Redis
- **Message Queue**: Apache Kafka
- **Authentication**: Auth0 / Supabase Auth

### Infrastructure
- **Cloud**: AWS (primary), GCP (secondary)
- **Container**: Docker + Kubernetes (EKS)
- **CI/CD**: GitHub Actions + ArgoCD
- **Monitoring**: Prometheus + Grafana, ELK Stack
- **IaC**: Terraform + Pulumi

## Development Setup

```bash
# Prerequisites
- Node.js 18+
- Python 3.11+
- Docker Desktop
- PostgreSQL 15+
- Redis

# Clone and install
git clone https://github.com/simpleiq/simpleiq.git
cd simpleiq
npm install

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Database setup
npm run db:migrate
npm run db:seed

# Start development servers
npm run dev:api      # Start API server (port 3000)
npm run dev:web      # Start web app (port 5173)
npm run dev:ai       # Start AI service (port 8000)

# Or start all services with Docker
docker-compose up
```

## Common Commands

```bash
# Development
npm run dev           # Start all services in dev mode
npm run dev:api       # Start API server only
npm run dev:web       # Start web application only
npm run dev:ai        # Start AI service only

# Testing
npm run test          # Run unit tests
npm run test:e2e      # Run end-to-end tests
npm run test:coverage # Generate coverage report
npm run test:watch    # Run tests in watch mode

# Code Quality
npm run lint          # Run ESLint
npm run lint:fix      # Fix linting issues
npm run format        # Format code with Prettier
npm run typecheck     # Run TypeScript type checking

# Building
npm run build         # Build all packages
npm run build:api     # Build API server
npm run build:web     # Build web application
npm run build:docker  # Build Docker images

# Database
npm run db:migrate    # Run database migrations
npm run db:rollback   # Rollback last migration
npm run db:seed       # Seed database with test data
npm run db:reset      # Reset database

# Deployment
npm run deploy:staging    # Deploy to staging
npm run deploy:production # Deploy to production (requires approval)
```

## Project Structure

```
simpleiq/
├── packages/
│   ├── api/                 # Backend API services (NestJS)
│   │   ├── src/
│   │   │   ├── modules/     # Feature modules
│   │   │   ├── common/      # Shared utilities
│   │   │   └── main.ts      # Application entry
│   │   └── test/
│   ├── web/                 # React web application
│   │   ├── src/
│   │   │   ├── components/  # Reusable components
│   │   │   ├── pages/       # Page components
│   │   │   ├── features/    # Feature modules
│   │   │   ├── hooks/       # Custom hooks
│   │   │   └── App.tsx      # Application root
│   │   └── test/
│   ├── mobile/              # React Native mobile app
│   ├── shared/              # Shared types and utilities
│   └── ai/                  # Python AI/ML services
│       ├── models/          # ML models
│       ├── services/        # AI services
│       └── api/             # FastAPI endpoints
├── infrastructure/
│   ├── terraform/           # Infrastructure as Code
│   ├── kubernetes/          # K8s manifests
│   └── docker/              # Dockerfiles
├── docs/
│   ├── PROJECT_OVERVIEW.md
│   ├── USER_PERSONAS.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── PRODUCT_ROADMAP.md
│   └── GTM_STRATEGY.md
└── scripts/                 # Utility scripts
```

## Architecture Overview

SimpleIQ follows a microservices architecture with clear separation of concerns:

1. **API Gateway**: Kong gateway handles routing, rate limiting, and authentication
2. **Core Services**: NestJS services handle business logic, user management, billing
3. **AI Services**: Python services handle NLP, predictions, and ML operations
4. **Data Services**: Handle data ingestion, processing, and querying
5. **Message Bus**: Kafka enables async communication between services
6. **Data Layer**: PostgreSQL for transactional data, ClickHouse for analytics

### Key Design Patterns
- **API-First**: All functionality exposed via REST/GraphQL APIs
- **Event-Driven**: Services communicate via events for loose coupling
- **Multi-Tenancy**: Complete data isolation between organizations
- **CQRS**: Separate read and write models for performance
- **Repository Pattern**: Abstracted data access layer

## Development Guidelines

### Code Style
- Use TypeScript for all Node.js code
- Follow ESLint and Prettier configurations
- Write tests for all new features (minimum 80% coverage)
- Use conventional commits for git messages
- Document all public APIs with JSDoc/OpenAPI

### Git Workflow
1. Create feature branch from `develop`
2. Make changes with atomic commits
3. Write/update tests
4. Create PR with description
5. Pass CI checks and code review
6. Merge to `develop`
7. Deploy to staging automatically
8. Production deployment on release

### Testing Strategy
- **Unit Tests**: All business logic and utilities
- **Integration Tests**: API endpoints and service interactions
- **E2E Tests**: Critical user flows
- **Performance Tests**: Load testing for APIs
- **Security Tests**: Vulnerability scanning

### Security Practices
- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper authentication and authorization
- Sanitize all user inputs
- Keep dependencies updated
- Follow OWASP guidelines

## Important Context

### Target Users
SimpleIQ is designed for non-technical SME users who need analytics without complexity. Key personas include:
- E-commerce entrepreneurs
- Operations managers
- Marketing directors
- Small business owners

### MVP Features (Current Focus)
1. Data connectivity (Google Sheets, CSV, REST API)
2. Natural language queries
3. Basic dashboard builder (5 chart types)
4. User authentication
5. Simple sharing

### Technical Decisions
- **Why Microservices**: Scalability and independent deployment
- **Why TypeScript**: Type safety and better developer experience
- **Why PostgreSQL + ClickHouse**: OLTP + OLAP optimization
- **Why Kubernetes**: Container orchestration and auto-scaling
- **Why Llama 3.3**: Cost-effective AI with privacy control

### Performance Targets
- API response time: <200ms (p50), <1s (p99)
- Dashboard load time: <2s
- Query execution: <5s
- AI response time: <3s
- Uptime SLA: 99.9%

## Getting Help

- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Internal**: Slack channel #simpleiq-dev

## Notes

- Always run tests before pushing code
- Update documentation when adding features
- Consider performance implications of changes
- Think about multi-tenant data isolation
- Prioritize user experience over technical complexity