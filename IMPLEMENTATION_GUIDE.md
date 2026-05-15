# Implementation Guide

This guide provides detailed implementation steps for building the Multi-Agent Appointment Booking System.

## Phase 1: Foundation Setup (Week 1-2)

### Step 1.1: Initialize Project Structure

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create directory structure
mkdir -p src/{agents/calendar,workflows,api/routes,api/middleware,models,schemas,services,integrations,database/migrations/versions,utils,tasks,prompts}
mkdir -p tests/{unit/test_agents,unit/test_services,unit/test_utils,integration,fixtures}
mkdir -p scripts docker docs/{api,guides,examples}

# Create __init__.py files
find src tests -type d -exec touch {}/__init__.py \;
```

### Step 1.2: Install Core Dependencies

Create `requirements.txt`:
```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# Caching & Queue
redis==5.0.1
celery==5.3.6

# LangChain & LangGraph
langchain==0.1.4
langgraph==0.0.20
langchain-openai==0.0.5
langchain-community==0.0.16

# Calendar APIs
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.116.0
msal==1.26.0
caldav==1.3.9

# Notifications
sendgrid==6.11.0
twilio==8.11.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.2

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
```

Create `requirements-dev.txt`:
```txt
# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Code Quality
black==24.1.1
flake8==7.0.0
mypy==1.8.0
isort==5.13.2

# Development
ipython==8.20.0
```

Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 1.3: Configuration Management

Create `src/config.py`:
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    app_name: str = "Multi-Agents-Appointment-Booking"
    app_env: str = "development"
    debug: bool = True
    secret_key: str
    
    # Database
    database_url: str
    database_pool_size: int = 20
    
    # Redis
    redis_url: str
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    
    # Google Calendar
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # Microsoft Graph
    microsoft_client_id: str
    microsoft_client_secret: str
    microsoft_redirect_uri: str
    
    # SendGrid
    sendgrid_api_key: str
    sendgrid_from_email: str
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### Step 1.4: Database Setup

Create `src/database/session.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=0
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Initialize Alembic:
```bash
alembic init src/database/migrations
```

### Step 1.5: Basic FastAPI Application

Create `src/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.api.routes import auth, appointments, calendars, preferences, webhooks

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(calendars.router, prefix="/calendars", tags=["Calendars"])
app.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
async def root():
    return {"message": "Multi-Agent Appointment Booking System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Phase 2: Database Models (Week 2)

### Step 2.1: User Model

Create `src/models/user.py`:
```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calendars = relationship("Calendar", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
```

### Step 2.2: Calendar Model

Create `src/models/calendar.py`:
```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from src.database.session import Base

class CalendarProvider(str, enum.Enum):
    GOOGLE = "google"
    OUTLOOK = "outlook"
    IOS = "ios"

class Calendar(Base):
    __tablename__ = "calendars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(CalendarProvider), nullable=False)
    calendar_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)  # Encrypted
    refresh_token = Column(String)  # Encrypted
    is_primary = Column(Boolean, default=False)
    sync_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="calendars")
    events = relationship("CalendarEvent", back_populates="calendar", cascade="all, delete-orphan")
```

### Step 2.3: Appointment Model

Create `src/models/appointment.py`:
```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from src.database.session import Base

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String, default="UTC")
    location = Column(String)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    created_by_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    calendar_events = relationship("CalendarEvent", back_populates="appointment", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="appointment", cascade="all, delete-orphan")
```

## Phase 3: Agent Implementation (Week 3-6)

### Step 3.1: Base Agent Class

Create `src/agents/base.py`:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools: list[BaseTool] = []
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    def add_tool(self, tool: BaseTool):
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
    
    def get_tools(self) -> list[BaseTool]:
        """Get all tools available to this agent"""
        return self.tools
```

### Step 3.2: NLP Agent

Create `src/agents/nlp_agent.py`:
```python
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.agents.base import BaseAgent
from src.config import get_settings

class NLPAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NLP Agent",
            description="Parses natural language booking requests into structured data"
        )
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key
        )
        self.prompt = self._create_prompt()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at parsing natural language appointment booking requests.
            Extract the following information:
            - title: Meeting title
            - date: Date of the meeting
            - time: Time of the meeting
            - duration: Duration in minutes
            - participants: List of participant emails
            - location: Meeting location (if specified)
            - description: Additional details
            
            Return the information in JSON format."""),
            ("user", "{input}")
        ])
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_input = input_data.get("text", "")
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"input": user_input})
        return {"parsed_data": response.content}
```

### Step 3.3: LangGraph Workflow

Create `src/workflows/booking_workflow.py`:
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.agents.coordinator import CoordinatorAgent
from src.agents.nlp_agent import NLPAgent
from src.agents.conflict_detector import ConflictDetectorAgent
from src.agents.scheduler_optimizer import SchedulerOptimizerAgent

class BookingState(TypedDict):
    user_input: str
    parsed_data: dict
    conflicts: list
    optimal_slot: dict
    booking_result: dict
    error: str | None

def create_booking_workflow():
    workflow = StateGraph(BookingState)
    
    # Initialize agents
    nlp_agent = NLPAgent()
    conflict_agent = ConflictDetectorAgent()
    scheduler_agent = SchedulerOptimizerAgent()
    
    # Define nodes
    async def parse_input(state: BookingState):
        result = await nlp_agent.execute({"text": state["user_input"]})
        return {"parsed_data": result["parsed_data"]}
    
    async def check_conflicts(state: BookingState):
        result = await conflict_agent.execute({"booking_data": state["parsed_data"]})
        return {"conflicts": result["conflicts"]}
    
    async def find_optimal_slot(state: BookingState):
        result = await scheduler_agent.execute({
            "booking_data": state["parsed_data"],
            "conflicts": state["conflicts"]
        })
        return {"optimal_slot": result["optimal_slot"]}
    
    # Add nodes
    workflow.add_node("parse", parse_input)
    workflow.add_node("check_conflicts", check_conflicts)
    workflow.add_node("optimize", find_optimal_slot)
    
    # Add edges
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "check_conflicts")
    workflow.add_edge("check_conflicts", "optimize")
    workflow.add_edge("optimize", END)
    
    return workflow.compile()
```

## Phase 4: API Implementation (Week 7-8)

### Step 4.1: Authentication Endpoints

Create `src/api/routes/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.schemas.auth import Token, UserCreate, UserResponse
from src.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(form_data.username, form_data.password)
```

### Step 4.2: Appointment Endpoints

Create `src/api/routes/appointments.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database.session import get_db
from src.schemas.appointment import AppointmentCreate, AppointmentResponse
from src.services.appointment_service import AppointmentService
from src.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AppointmentService(db)
    return await service.create_appointment(current_user.id, appointment_data)

@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AppointmentService(db)
    return await service.get_user_appointments(current_user.id)
```

## Phase 5: Testing (Week 9-10)

### Step 5.1: Unit Tests

Create `tests/unit/test_agents/test_nlp_agent.py`:
```python
import pytest
from src.agents.nlp_agent import NLPAgent

@pytest.mark.asyncio
async def test_nlp_agent_parse_simple_request():
    agent = NLPAgent()
    result = await agent.execute({
        "text": "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour"
    })
    assert "parsed_data" in result
    # Add more assertions based on expected output
```

### Step 5.2: Integration Tests

Create `tests/integration/test_booking_workflow.py`:
```python
import pytest
from src.workflows.booking_workflow import create_booking_workflow

@pytest.mark.asyncio
async def test_complete_booking_workflow():
    workflow = create_booking_workflow()
    initial_state = {
        "user_input": "Book a meeting with team@example.com next Monday at 10am"
    }
    result = await workflow.ainvoke(initial_state)
    assert result["booking_result"] is not None
```

## Phase 6: Deployment (Week 11-12)

### Step 6.1: Docker Setup

Create `docker/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY alembic.ini .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker/docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appointment_booking
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appointment_booking
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile.worker
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

### Step 6.2: CI/CD Pipeline

Create `.github/workflows/ci.yml`:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=src tests/
      - name: Lint
        run: |
          black --check src/
          flake8 src/
```

## Next Steps

1. Review this implementation guide
2. Confirm the approach and make any necessary adjustments
3. Switch to Code mode to begin implementation
4. Follow the phases sequentially, testing each component before moving forward

## Key Considerations

- **Security**: All tokens encrypted at rest, OAuth 2.0 for calendar access
- **Scalability**: Stateless design, horizontal scaling capability
- **Reliability**: Retry logic, error handling, comprehensive logging
- **Testing**: Unit tests for agents, integration tests for workflows
- **Documentation**: API docs with OpenAPI, code comments, user guides