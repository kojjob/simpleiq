# SimpleIQ - Databricks for SMEs 🚀

<div align="center">
  <h3>Transform your data into insights with natural language queries</h3>
  <p>Enterprise-grade analytics made simple for small and medium businesses</p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![React](https://img.shields.io/badge/React-18.2+-61dafb.svg?style=flat&logo=react&logoColor=white)](https://reactjs.org)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178c6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 🎯 What is SimpleIQ?

SimpleIQ democratizes data intelligence by bringing Databricks-level capabilities to SMEs without requiring technical expertise. While Databricks serves enterprises with data teams, SimpleIQ empowers small businesses with the same powerful analytics through a **no-code, conversational interface**.

### 🔥 Key Features

- **🗣️ Natural Language Queries**: Ask questions in plain English, get insights instantly
- **⚡ 5-Minute Setup**: Connect your data and start analyzing immediately
- **📊 Drag-and-Drop Dashboards**: Build beautiful dashboards without code
- **🤖 AI-Powered Insights**: Automated predictions and anomaly detection
- **🔗 50+ Data Connectors**: Google Sheets, CSV, REST APIs, and more
- **💰 SME Pricing**: $49/month vs. $50,000+/year for enterprise solutions

## 🏗️ Technology Stack

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL (transactional) + ClickHouse (analytics)
- **AI/ML**: Llama 3.3 for NLP, LangChain for orchestration
- **Package Manager**: UV for lightning-fast dependency management
- **Queue**: Celery + Redis for background jobs

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for instant HMR
- **UI Library**: Ant Design + Tailwind CSS
- **State Management**: TanStack Query + Zustand
- **Charts**: Chart.js + Recharts

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- UV package manager (will be installed automatically)

### Backend Setup

```bash
cd backend
./setup.sh                    # Installs UV and dependencies
source .venv/bin/activate     # Activate virtual environment
cp .env.example .env          # Configure environment
uvicorn app.main:app --reload # Start server
```

API documentation available at: http://localhost:8000/api/v1/docs

### Frontend Setup

```bash
cd frontend
npm install                   # Install dependencies
npm run dev                   # Start development server
```

Application available at: http://localhost:5173

### Full Stack with Docker

```bash
cd backend
docker-compose up            # Starts all services
```

Services:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173 (run separately)
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- ClickHouse: localhost:8123
- Flower (Celery monitor): localhost:5555

## 📚 Project Structure

```
simpleiq/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models & schemas
│   │   ├── services/       # Business logic
│   │   └── ml/             # AI/ML operations
│   ├── tests/              # Test suite
│   └── docker-compose.yml  # Development environment
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API clients
│   │   └── stores/        # State management
│   └── package.json
│
└── docs/                   # Documentation
    ├── PRD.md             # Product Requirements
    ├── TECHNICAL_ARCHITECTURE.md
    └── USER_STORIES.md
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                       # Run all tests
pytest --cov=app            # With coverage
mypy app/                   # Type checking
ruff check app/             # Linting
```

### Frontend Tests
```bash
cd frontend
npm run test                # Run tests
npm run test:coverage       # With coverage
npm run type-check          # TypeScript checking
npm run lint                # ESLint
```

## 🚢 Deployment

### Development
```bash
git checkout develop
git pull origin develop
# Make changes
git add .
git commit -m "feat: your feature"
git push origin develop
```

### Production
Production deployment uses GitHub Actions for CI/CD:
1. Merge to `main` branch
2. Automated tests run
3. Docker images built
4. Deployed to AWS/GCP

## 📖 Documentation

- [Product Requirements Document](docs/PRD.md)
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [User Stories](docs/USER_STORIES.md)
- [API Documentation](http://localhost:8000/api/v1/docs) (when running)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📊 Roadmap

### Q1 2024 - MVP Launch
- ✅ Core infrastructure setup
- ✅ Authentication & user management
- 🔄 Data connectivity (Google Sheets, CSV)
- 🔄 Natural language query engine
- 🔄 Basic dashboard builder

### Q2 2024 - Intelligence Layer
- ⏳ AI predictions and forecasting
- ⏳ Advanced data connectors
- ⏳ Team collaboration features
- ⏳ Mobile applications

### Q3 2024 - Enterprise Features
- ⏳ White-label options
- ⏳ Advanced security features
- ⏳ API access for developers
- ⏳ Industry-specific solutions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Databricks' vision of democratizing data analytics
- Built with amazing open-source technologies
- Special thanks to the FastAPI and React communities

## 📞 Contact

- **Website**: [simpleiq.io](https://simpleiq.io)
- **Email**: team@simpleiq.io
- **Twitter**: [@SimpleIQData](https://twitter.com/SimpleIQData)
- **LinkedIn**: [SimpleIQ](https://linkedin.com/company/simpleiq)

---

<div align="center">
  <p>Built with ❤️ for SMEs worldwide</p>
  <p><strong>Making Databricks-level analytics accessible to every business</strong></p>
</div>