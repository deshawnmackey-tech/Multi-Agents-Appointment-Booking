# Setup Process and Procedures Guide

This guide defines the standard process for setting up, validating, and maintaining the Multi-Agents Appointment Booking project in a consistent way.

## 1. Purpose

Use this guide to ensure:

- Faster onboarding for new developers
- Consistent local environments
- Repeatable test results
- Fewer setup-time failures
- Predictable CI behavior across SQLite and PostgreSQL

## 2. Scope

This process applies to:

- New local development setup
- Environment verification
- Daily start/stop procedures
- Test execution for both database profiles
- Pull request readiness checks

## 3. Standard Setup Process (New Machine)

### Fast Path (Recommended)

From repository root:

```bash
./scripts/bootstrap_dev.sh
```

Useful options:

```bash
./scripts/bootstrap_dev.sh --run-app
./scripts/bootstrap_dev.sh --no-tests
./scripts/bootstrap_dev.sh --postgres
```

### Step 1: Clone and enter the project

```bash
git clone <repository-url>
cd Multi-Agents-Appointment-Booking
```

### Step 2: Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 4: Create environment file

```bash
cp .env.example .env
```

Minimum values required to start locally:

```env
DATABASE_URL=sqlite:///./local_dev.db
OPENAI_API_KEY=sk-your-key
SECRET_KEY=replace-with-random-secret
JWT_SECRET_KEY=replace-with-another-random-secret
```

### Step 5: Start the API

Use module invocation for maximum compatibility:

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Verify service health

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/docs
```

Expected:

- Health endpoint returns HTTP 200 with status "healthy"
- Docs endpoint returns HTTP 200

## 4. Local Runtime Profiles

### Profile A: Fast local development (default)

- Database: SQLite
- Purpose: quick startup, API/docs checks, fast iteration
- Recommended DATABASE_URL:
  - sqlite:///./local_dev.db

### Profile B: Postgres integration validation

- Database: PostgreSQL
- Purpose: behavior parity with production-like database
- Example DATABASE_URL:
  - postgresql://user:password@localhost:5432/appointment_booking

If using Postgres profile:

```bash
alembic upgrade head
python scripts/check_db_health.py
```

## 5. Test Procedures

### Default test run (SQLite-backed integration tests)

```bash
python -m pytest
```

### PostgreSQL integration profile test run

```bash
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/appointment_booking_test
python -m pytest
```

### Live NLP tests (optional, opt-in)

Live NLP tests are skipped unless explicitly enabled.

```bash
export RUN_LIVE_NLP_TESTS=1
export OPENAI_API_KEY=sk-your-real-key
python -m pytest test_nlp_live.py
```

## 6. CI Procedure

CI workflow file:

- .github/workflows/ci.yml

CI runs a matrix with:

- sqlite
- postgres

Each CI run:

1. Installs runtime and dev dependencies
2. Sets required runtime secrets for app import
3. Runs full test suite

## 7. Daily Start Procedure

Use this at the start of each development session.

```bash
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Then confirm:

```bash
curl http://localhost:8000/health
```

## 8. Daily Stop Procedure

```bash
pkill -f "uvicorn|python -m uvicorn"
```

## 9. Pull Request Readiness Procedure

Before opening a PR:

1. Run tests locally:
   - python -m pytest
2. Confirm app boots and docs are reachable:
   - /health returns 200
   - /api/docs returns 200
3. Ensure no credentials are committed:
   - .env stays local
4. Review changed files for unintended artifacts:
   - local_dev.db, test.db should not be committed

## 10. Troubleshooting Procedures

### Issue: uvicorn command not found

Use:

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Issue: tests fail due to database type mismatch

- Ensure latest code is pulled (portable GUID support is included)
- Re-run with:

```bash
python -m pytest
```

### Issue: live NLP tests fail with API key errors

- Set a valid OPENAI_API_KEY
- Run only when intentionally testing external API calls
- Keep RUN_LIVE_NLP_TESTS unset for normal CI/local runs

### Issue: app starts but business endpoints return not implemented

This is expected for unfinished route handlers. Verify platform health via:

- /health
- /api/docs

## 11. Security Procedures

- Never commit .env
- Rotate secrets periodically
- Use strong random values for SECRET_KEY and JWT_SECRET_KEY
- Use SSL-enabled database URLs in production

## 12. Definition of Done for Setup

A setup is complete when all are true:

- App starts successfully with python -m uvicorn
- /health responds with HTTP 200
- /api/docs is reachable
- python -m pytest passes locally
- CI matrix passes for sqlite and postgres
