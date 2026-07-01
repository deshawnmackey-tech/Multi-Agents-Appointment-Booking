# Multi-Agents-Appointment-Booking

Multi-Agent Appointment Booking System with Google Calendar, Outlook, and iOS Calendar Integration

## 🚀 Quick Start

### One-Command Bootstrap (Recommended)

```bash
./scripts/bootstrap_dev.sh
```

Optional flags:

```bash
./scripts/bootstrap_dev.sh --run-app
./scripts/bootstrap_dev.sh --no-tests
./scripts/bootstrap_dev.sh --postgres
```

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Git

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ulti-Agents-Appointment-Booking
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

5. **Update `.env` with your credentials**
   
   **IMPORTANT:** Replace the following placeholders:
   
   ```env
   # Database - Replace 'user' and 'password' with your PostgreSQL credentials
   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/appointment_booking
   
   # Add your API keys
   OPENAI_API_KEY=your-actual-openai-api-key
   SECRET_KEY=generate-a-secure-random-key
   JWT_SECRET_KEY=generate-another-secure-random-key
   ```

6. **Create the database**
   ```bash
   createdb appointment_booking
   ```

7. **Verify database connection**
   ```bash
   python scripts/check_db_health.py
   ```

8. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

9. **Start the application**
   ```bash
   python -m uvicorn src.main:app --reload
   ```

## 🗄️ Database Configuration

### Connection Pool Settings

The application uses SQLAlchemy connection pooling for optimal database performance. Configure these settings in your `.env` file:

| Variable | Description | Default | Production Recommended |
|----------|-------------|---------|------------------------|
| `DATABASE_URL` | PostgreSQL connection string | - | Use SSL, strong password |
| `DATABASE_POOL_SIZE` | Number of persistent connections | 20 | 50-100 (based on load) |
| `DATABASE_POOL_MAX_OVERFLOW` | Extra connections when pool exhausted | 10 | 20 |
| `DATABASE_POOL_TIMEOUT` | Timeout for getting connection (seconds) | 30 | 30 |
| `DATABASE_POOL_RECYCLE` | Recycle connections after N seconds | 3600 | 3600 |
| `DATABASE_ECHO_POOL` | Log pool checkouts/checkins | false | false |

### Environment-Specific Configurations

**Development:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/appointment_booking_dev
DATABASE_POOL_SIZE=10
```

**Production:**
```env
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/appointment_booking?sslmode=require
DATABASE_POOL_SIZE=50
DATABASE_POOL_MAX_OVERFLOW=20
```

**Testing:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/appointment_booking_test
DATABASE_POOL_SIZE=5
```

### Database Health Check

Run the health check script to verify your database configuration:

```bash
python scripts/check_db_health.py
```

Expected output:
```
============================================================
DATABASE HEALTH CHECK
============================================================

✓ Database connection successful

Database Information:
  URL: postgresql://user:****@localhost:5432/appointment_booking
  Version: PostgreSQL 14.x

Connection Pool Status:
  Pool size: 0
  Checked out: 0
  Overflow: 0
  Max overflow: 10

Pool Configuration:
  Pool size: 20
  Max overflow: 10
  Timeout: 30s
  Recycle: 3600s
  Pre-ping: Enabled

✓ Query execution successful

============================================================
HEALTH CHECK PASSED
============================================================
```

## 🔐 Security Best Practices

### Environment Files

- ✅ `.env` is in `.gitignore` (never commit credentials)
- ✅ Use `.env.example` as a template
- ✅ Use strong, unique passwords for production
- ✅ Rotate credentials regularly
- ✅ Use SSL/TLS for database connections in production

### Generating Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Production Checklist

- [ ] Replace all placeholder credentials in `.env`
- [ ] Use SSL for database connections (`?sslmode=require`)
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Use strong, unique passwords
- [ ] Enable database connection encryption
- [ ] Configure proper firewall rules
- [ ] Set up monitoring and alerting
- [ ] Regular security audits

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_agents/
```

### Test Database Setup

The test suite uses a separate database to avoid affecting development data.
By default, tests run on local SQLite (`sqlite:///./test.db`).

To run integration tests against PostgreSQL instead, set `TEST_DATABASE_URL`:

```bash
# Example PostgreSQL profile
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/appointment_booking_test
python -m pytest
```

## 📚 Additional Documentation

- [Architecture](ARCHITECTURE.md) - System architecture and design
- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Development guidelines
- [Project Structure](PROJECT_STRUCTURE.md) - Directory organization
- [Setup Process and Procedures](SETUP_PROCESS_PROCEDURES.md) - Standardized onboarding and operational workflow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Database Connection Issues

1. **Verify PostgreSQL is running:**
   ```bash
   pg_isready
   ```

2. **Check credentials:**
   ```bash
   psql -U your_username -d appointment_booking
   ```

3. **Run health check:**
   ```bash
   python scripts/check_db_health.py
   ```

4. **Check logs:**
   - Enable `DATABASE_ECHO_POOL=true` in `.env` for detailed pool logging
   - Check PostgreSQL logs: `/var/log/postgresql/`

### Common Issues

**Issue:** `FATAL: password authentication failed`
- **Solution:** Verify username and password in `DATABASE_URL`

**Issue:** `FATAL: database "appointment_booking" does not exist`
- **Solution:** Run `createdb appointment_booking`

**Issue:** `Connection pool exhausted`
- **Solution:** Increase `DATABASE_POOL_SIZE` or `DATABASE_POOL_MAX_OVERFLOW`

**Issue:** `Timeout waiting for connection`
- **Solution:** Increase `DATABASE_POOL_TIMEOUT` or check database performance

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section above
