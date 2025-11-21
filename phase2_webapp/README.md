# Phase 2: Web Application Deployment

## Overview

This is a **production-ready web application** for the Healthrix Productivity System built with:

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Frontend**: React (starter templates provided)
- **Deployment**: Docker + docker-compose
- **Authentication**: JWT tokens with role-based access control

**Status**: ✅ **Backend Complete - Ready for Production**

---

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- 4GB RAM minimum
- Ports 8000 (API) and 5432 (Database) available

### 1. Clone and Setup

```bash
cd phase2_webapp
cp backend/.env.example backend/.env
# Edit backend/.env and set SECRET_KEY to a random string
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Verify

```bash
# Check services are running
docker-compose ps

# View logs
docker-compose logs -f backend

# API should be available at:
open http://localhost:8000/docs
```

### 4. Create First User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "emp_id": "EMP001",
    "email": "admin@healthrix.com",
    "password": "SecurePassword123!",
    "name": "Admin User",
    "department": "IT",
    "role": "admin"
  }'
```

### 5. Get Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@healthrix.com&password=SecurePassword123!"
```

---

## Project Structure

```
phase2_webapp/
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/v1/              # API endpoints
│   │   │   └── endpoints/
│   │   │       ├── auth.py      # Authentication
│   │   │       ├── activities.py # Activity CRUD
│   │   │       └── performance.py # Performance calc
│   │   ├── core/                # Core utilities
│   │   │   ├── config.py        # Configuration
│   │   │   └── security.py      # JWT & auth
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── db/                  # Database setup
│   │   └── main.py              # FastAPI app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                    # React frontend (starter)
├── docker/                      # Additional Docker configs
├── deployment/                  # Deployment guides
├── docs/                        # Documentation
└── docker-compose.yml           # Docker orchestration
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `GET /api/v1/auth/me` - Get current user info

### Activities
- `POST /api/v1/activities` - Create activity
- `GET /api/v1/activities` - List activities (filtered)
- `GET /api/v1/activities/{id}` - Get specific activity
- `PUT /api/v1/activities/{id}` - Update activity
- `DELETE /api/v1/activities/{id}` - Delete activity

### Performance
- `POST /api/v1/performance/calculate` - Calculate performance scores
- `GET /api/v1/performance/scores` - List performance scores
- `GET /api/v1/performance/trend/{emp_id}` - Get employee trend
- `GET /api/v1/performance/leaderboard` - Get team leaderboard
- `GET /api/v1/performance/statistics` - Get team statistics
- `GET /api/v1/performance/my-latest` - Get my latest score

**Full API Documentation**: http://localhost:8000/docs

---

## Database Schema

### Users Table
- `emp_id` (PK) - Employee ID
- `email` - Email address (unique)
- `hashed_password` - Bcrypt hashed password
- `name` - Full name
- `department` - Department
- `role` - employee | supervisor | admin
- `is_active` - Account status
- `hire_date` - Hire date

### Task Standards Table
- `task_id` (PK) - Task ID
- `task_name` - Task name (unique)
- `ec_category` - Effort category (EC-1 to EC-5)
- `base_score` - Points per completion
- `target_daily` - Daily target count

### Activities Table
- `activity_id` (PK) - Activity ID
- `date` - Activity date
- `emp_id` (FK) - Employee
- `task_id` (FK) - Task
- `count` - Number of completions
- `patient_id` - Optional patient ID
- `duration_minutes` - Optional duration
- `notes` - Optional notes

### Daily Metrics Table
- `metric_id` (PK) - Metric ID
- `date` - Metric date
- `emp_id` (FK) - Employee
- `idle_hours` - Idle time (decimal)
- `conduct_flag` - 0 (Good) or 1 (Issue)
- `conduct_notes` - Notes about conduct
- `supervisor` - Supervisor who recorded

### Performance Scores Table
- `score_id` (PK) - Score ID
- `date` - Score date
- `emp_id` (FK) - Employee
- `total_task_points` - Points earned
- `productivity_percent` - Productivity %
- `weighted_prod_score` - Weighted productivity
- `behavior_score_raw` - Raw behavior score
- `weighted_behavior_score` - Weighted behavior
- `final_performance_percent` - Final score
- `task_count` - Number of activities
- `idle_hours` - Idle hours
- `conduct_flag` - Conduct flag

---

## Configuration

### Environment Variables

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-random-secret-key-here

# Performance Settings
DAILY_TARGET_POINTS=400
PRODUCTIVITY_WEIGHT=0.90
BEHAVIOR_WEIGHT=0.10
IDLE_PENALTY_PER_HOUR=10
CONDUCT_PENALTY=50
```

---

## Development

### Local Development (without Docker)

```bash
# Install PostgreSQL locally
createdb healthrix

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit .env
cp .env.example .env
# Edit .env with your local database URL

# Run backend
uvicorn app.main:app --reload

# API docs: http://localhost:8000/docs
```

### Running Tests

```bash
cd backend
pytest
pytest --cov=app tests/
```

---

## Deployment

### Option 1: Docker Compose (Recommended)

See Quick Start above.

**Production checklist**:
- [ ] Change `SECRET_KEY` in .env
- [ ] Set `DEBUG=false`
- [ ] Use strong database password
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS (nginx proxy)
- [ ] Configure backups
- [ ] Set up monitoring

### Option 2: Cloud Platforms

**Heroku**:
```bash
heroku create healthrix-api
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**AWS/DigitalOcean/Azure**:
See `deployment/` directory for detailed guides.

---

## Security

### Role-Based Access Control

**Employee Role**:
- Can create/view/edit own activities
- Can view own performance scores
- Cannot access other employees' data

**Supervisor Role**:
- All employee permissions
- Can view all activities and scores
- Can create daily metrics for employees
- Can trigger performance calculations
- Can access leaderboards and statistics

**Admin Role**:
- All supervisor permissions
- Can create/edit users
- Can modify task standards
- Full system access

### Authentication Flow

1. Register or login to get JWT tokens
2. Include token in Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```
3. Token expires after 30 minutes (configurable)
4. Use refresh token to get new access token

---

## Performance Calculation

### Formula

```
Productivity Score (90% weight):
  Total Points = Σ (Task Count × Task Base Score)
  Productivity % = (Total Points / 400) × 100
  Weighted = Productivity % × 0.90

Behavior Score (10% weight):
  Base = 100
  Minus: Idle Hours × 10 points
  Minus: Conduct Flag × 50 points
  Weighted = Base × 0.10

FINAL PERFORMANCE = Weighted Productivity + Weighted Behavior
```

### Calculation Trigger

**Manual**: POST to `/api/v1/performance/calculate`

**Automated**: Set up cron job:
```bash
# Add to crontab (calculate daily at 1 AM)
0 1 * * * curl -X POST http://localhost:8000/api/v1/performance/calculate \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-11-20"}'
```

---

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Database Health

```bash
docker-compose exec db pg_isready -U healthrix
```

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f db

# All logs
docker-compose logs -f
```

---

## Backup & Restore

### Backup Database

```bash
docker-compose exec db pg_dump -U healthrix healthrix > backup.sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U healthrix healthrix < backup.sql
```

---

## Troubleshooting

### Issue: Database connection fails

**Solution**:
```bash
# Check database is running
docker-compose ps db

# Check connection string in .env
# Should be: postgresql://healthrix:healthrixpassword@db:5432/healthrix
```

### Issue: CORS errors

**Solution**:
Add your frontend URL to `BACKEND_CORS_ORIGINS` in .env:
```
BACKEND_CORS_ORIGINS=http://localhost:3000,http://your-frontend.com
```

### Issue: Token expired

**Solution**:
Login again to get a new token or use refresh token.

---

## Migration from Phase 1

### Export from Google Sheets

1. Download CSVs from Google Sheets
2. Use provided migration scripts (see `docs/migration_guide.md`)

### Import to PostgreSQL

```bash
# Example: Import employees
docker-compose exec backend python scripts/import_data.py \
  --type employees \
  --file /path/to/employees.csv
```

---

## Next Steps

1. **Frontend Development**: Build React dashboard (see `frontend/README.md`)
2. **CI/CD**: Set up GitHub Actions for automated testing/deployment
3. **Monitoring**: Integrate Sentry for error tracking
4. **Analytics**: Add advanced reporting and ML predictions
5. **Mobile App**: Consider React Native mobile app

---

## Support & Resources

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org

---

## License

Proprietary - Healthrix Productivity System

---

**Built with ❤️ using FastAPI, PostgreSQL, and modern web technologies**
