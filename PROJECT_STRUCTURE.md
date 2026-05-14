# Project Structure

```
ulti-Agents-Appointment-Booking/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI/CD pipeline
│       └── deploy.yml                # Deployment workflow
├── src/
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   ├── config.py                     # Configuration management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                   # Base agent class
│   │   ├── coordinator.py            # Coordinator/Supervisor agent
│   │   ├── nlp_agent.py              # Natural language processing agent
│   │   ├── conflict_detector.py      # Conflict detection agent
│   │   ├── scheduler_optimizer.py    # Scheduling optimization agent
│   │   ├── notification_agent.py     # Notification agent
│   │   ├── preference_manager.py     # User preference manager agent
│   │   └── calendar/
│   │       ├── __init__.py
│   │       ├── base_calendar.py      # Base calendar agent
│   │       ├── google_agent.py       # Google Calendar agent
│   │       ├── outlook_agent.py      # Outlook agent
│   │       └── ios_agent.py          # iOS Calendar (CalDAV) agent
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── booking_workflow.py       # LangGraph booking workflow
│   │   ├── sync_workflow.py          # Calendar sync workflow
│   │   └── state.py                  # Workflow state definitions
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                   # API dependencies
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── appointments.py       # Appointment endpoints
│   │   │   ├── calendars.py          # Calendar management endpoints
│   │   │   ├── preferences.py        # User preferences endpoints
│   │   │   └── webhooks.py           # Webhook handlers
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py               # Auth middleware
│   │       ├── rate_limit.py         # Rate limiting
│   │       └── error_handler.py      # Error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                   # User model
│   │   ├── calendar.py               # Calendar model
│   │   ├── appointment.py            # Appointment model
│   │   ├── preference.py             # User preference model
│   │   └── participant.py            # Participant model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                   # User Pydantic schemas
│   │   ├── calendar.py               # Calendar schemas
│   │   ├── appointment.py            # Appointment schemas
│   │   ├── preference.py             # Preference schemas
│   │   └── auth.py                   # Auth schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Authentication service
│   │   ├── calendar_service.py       # Calendar operations service
│   │   ├── appointment_service.py    # Appointment service
│   │   ├── notification_service.py   # Notification service
│   │   ├── sync_service.py           # Calendar sync service
│   │   └── preference_service.py     # Preference service
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── google_calendar.py        # Google Calendar API client
│   │   ├── microsoft_graph.py        # Microsoft Graph API client
│   │   ├── caldav_client.py          # CalDAV client for iOS
│   │   ├── sendgrid_client.py        # SendGrid email client
│   │   └── twilio_client.py          # Twilio SMS client
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py                # Database session management
│   │   ├── base.py                   # Base model class
│   │   └── migrations/               # Alembic migrations
│   │       └── versions/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── datetime_utils.py         # Date/time utilities
│   │   ├── encryption.py             # Token encryption utilities
│   │   ├── validators.py             # Input validators
│   │   └── logger.py                 # Logging configuration
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py             # Celery configuration
│   │   ├── sync_tasks.py             # Calendar sync tasks
│   │   └── notification_tasks.py     # Notification tasks
│   └── prompts/
│       ├── __init__.py
│       ├── nlp_prompts.py            # NLP agent prompts
│       ├── scheduler_prompts.py      # Scheduler prompts
│       └── conflict_prompts.py       # Conflict resolution prompts
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_agents/
│   │   │   ├── test_nlp_agent.py
│   │   │   ├── test_conflict_detector.py
│   │   │   ├── test_scheduler_optimizer.py
│   │   │   └── test_calendar_agents.py
│   │   ├── test_services/
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_appointment_service.py
│   │   │   └── test_calendar_service.py
│   │   └── test_utils/
│   │       ├── test_datetime_utils.py
│   │       └── test_validators.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_booking_workflow.py
│   │   ├── test_calendar_sync.py
│   │   └── test_api_endpoints.py
│   └── fixtures/
│       ├── __init__.py
│       ├── calendar_fixtures.py
│       └── appointment_fixtures.py
├── scripts/
│   ├── setup_db.py                   # Database setup script
│   ├── seed_data.py                  # Seed test data
│   └── run_migrations.py             # Migration runner
├── docker/
│   ├── Dockerfile                    # Main application Dockerfile
│   ├── Dockerfile.worker             # Celery worker Dockerfile
│   └── docker-compose.yml            # Docker Compose configuration
├── docs/
│   ├── api/
│   │   └── openapi.json              # OpenAPI specification
│   ├── guides/
│   │   ├── getting_started.md
│   │   ├── calendar_setup.md
│   │   └── agent_customization.md
│   └── examples/
│       ├── booking_examples.md
│       └── api_examples.md
├── .env.example                      # Example environment variables
├── .gitignore
├── requirements.txt                  # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── pyproject.toml                    # Python project configuration
├── alembic.ini                       # Alembic configuration
├── pytest.ini                        # Pytest configuration
├── README.md
├── ARCHITECTURE.md
├── PROJECT_STRUCTURE.md
├── LICENSE
└── CHANGELOG.md                      # Version history
```

## Key Directories Explained

### `/src/agents/`
Contains all agent implementations. Each agent is a specialized component that handles specific tasks:
- **Coordinator**: Orchestrates other agents using LangGraph
- **NLP Agent**: Parses natural language booking requests
- **Calendar Agents**: Interface with different calendar providers
- **Conflict Detector**: Identifies scheduling conflicts
- **Scheduler Optimizer**: Finds optimal time slots
- **Notification Agent**: Handles email/SMS notifications
- **Preference Manager**: Manages and learns user preferences

### `/src/workflows/`
LangGraph workflow definitions that orchestrate agent interactions:
- **Booking Workflow**: Main appointment booking flow
- **Sync Workflow**: Calendar synchronization flow
- **State**: Shared state definitions for workflows

### `/src/api/`
FastAPI application structure:
- **Routes**: API endpoint definitions
- **Middleware**: Request/response processing
- **Dependencies**: Shared dependencies (auth, database)

### `/src/models/`
SQLAlchemy ORM models representing database tables

### `/src/schemas/`
Pydantic schemas for request/response validation

### `/src/services/`
Business logic layer that coordinates between API, agents, and database

### `/src/integrations/`
Third-party API clients (Google, Microsoft, SendGrid, Twilio)

### `/src/tasks/`
Celery background tasks for async operations

### `/tests/`
Comprehensive test suite:
- **Unit Tests**: Test individual components
- **Integration Tests**: Test workflows and API endpoints
- **Fixtures**: Reusable test data

## Configuration Files

### `requirements.txt`
Main dependencies:
- fastapi
- uvicorn
- sqlalchemy
- alembic
- psycopg2-binary
- redis
- celery
- langchain
- langgraph
- langchain-openai
- google-auth
- google-auth-oauthlib
- google-api-python-client
- msal
- caldav
- sendgrid
- twilio
- pydantic
- pydantic-settings
- python-jose
- passlib
- bcrypt
- python-multipart

### `requirements-dev.txt`
Development dependencies:
- pytest
- pytest-asyncio
- pytest-cov
- black
- flake8
- mypy
- isort
- httpx

### `.env.example`
Environment variables template:
```env
# Application
APP_NAME=ulti-Agents-Appointment-Booking
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/appointment_booking
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Google Calendar
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Microsoft Graph
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/microsoft/callback

# SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Development Workflow

1. **Setup**: Clone repo, create virtual environment, install dependencies
2. **Database**: Run migrations with Alembic
3. **Development**: Run FastAPI with hot reload
4. **Testing**: Run pytest with coverage
5. **Linting**: Use black, flake8, mypy, isort
6. **Docker**: Build and run with docker-compose
7. **Deployment**: CI/CD pipeline via GitHub Actions