# Database Migrations

This directory contains Alembic database migrations for the Multi-Agent Appointment Booking System.

## Setup

1. Ensure your database connection is configured in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

2. Initialize the database (if not already done):
   ```bash
   python -c "from src.database.session import init_db; init_db()"
   ```

## Creating Migrations

To create a new migration after modifying models:

```bash
alembic revision --autogenerate -m "Description of changes"
```

## Running Migrations

To upgrade to the latest version:

```bash
alembic upgrade head
```

To downgrade one version:

```bash
alembic downgrade -1
```

To see current version:

```bash
alembic current
```

To see migration history:

```bash
alembic history
```

## Migration Files

Migration files are stored in `versions/` directory with the naming format:
```
YYYYMMDD_HHMM_<revision>_<description>.py
```

## Important Notes

- Always review auto-generated migrations before applying them
- Test migrations in a development environment first
- Keep migrations small and focused on specific changes
- Never modify existing migration files that have been applied to production

## Troubleshooting

If you encounter issues:

1. Check database connection in `.env`
2. Ensure all models are imported in `env.py`
3. Verify Alembic configuration in `alembic.ini`
4. Check migration history: `alembic history`

# Made with Bob