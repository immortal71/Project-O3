#  OncoPurpose - Production Quick Start

**Database-ready deployment with 6,800+ drugs and persistent storage**

---

##  What's New - Production Features

### Priority 1: Deployment 
-  **Dockerfile** - Containerized deployment
-  **docker-compose.yml** - Full stack (MySQL + Backend)
-  **.env configuration** - Environment management
-  **Production settings** - CORS, rate limiting, workers

### Priority 2: Database 
-  **MySQL 8.0 schema** - 8 tables created
-  **SQLAlchemy models** - Full ORM support
-  **Data migration** - Load 6,798 drugs automatically
-  **Generated outputs storage** - Save predictions/images ⭐

### Priority 3: API 
-  **Database endpoints** - `/api/v1/db/*` routes
-  **Rate limiting** - 60 requests/minute
-  **Error handling** - Production-grade middleware
-  **Health checks** - Monitor DB connection

---

##  Quick Start (Choose One)

### Option 1: Docker (Recommended) ⭐

```powershell
# Start everything
docker-compose up -d

# Wait for MySQL
Start-Sleep -Seconds 15

# Migrate data (6,798 drugs → MySQL)
docker-compose exec backend python backend/migrate_data.py

# Access: http://localhost:8000/docs
```

### Option 2: Local Setup

```powershell
# Install dependencies
pip install -r backend\requirements.txt

# Start MySQL (or use Docker)
docker-compose up -d mysql
Start-Sleep -Seconds 15

# Migrate data
python backend\migrate_data.py

# Start server
python backend\server.py
```

---

##  Database Features

### Automatic Setup
- Creates 8 tables on first run
- Indexes for fast queries
- Foreign keys for data integrity

### Tables Created
```sql
drugs              -- 6,798 compounds
hero_cases         -- 15 gold-standard examples
generated_outputs  -- Your predictions/images ⭐
mechanisms         -- 1,436 MOAs (indexed)
targets            -- 2,183 targets (indexed)
drug_mechanisms    -- Relationships
drug_targets       -- Relationships
analytics_cache    -- Performance optimization
```

### NEW: Save Generated Outputs 

```javascript
// Every prediction/image automatically saved!
POST /api/v1/db/output
{
    "output_type": "prediction",  // or "image", "analysis"
    "drug_name": "Metformin",
    "cancer_type": "Breast",
    "confidence_score": 0.87,
    "output_data": { ... }
}

// Retrieve later
GET /api/v1/db/outputs?output_type=prediction&limit=50
```

---

##  API Endpoints

### Two Modes Available

**Mode 1: In-Memory (Fast )**
- `/api/v1/search` - 6,798 drugs in RAM
- Response time: <5ms
- No database required

**Mode 2: Database (Persistent )**
- `/api/v1/db/search` - MySQL queries
- Response time: 10-50ms
- Saves generated outputs

### Frontend Configuration

```javascript
// frontend-config.js
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    USE_DATABASE: true,  // Enable persistent storage
    ENDPOINTS: {
        DB_SAVE_OUTPUT: '/api/v1/db/output',  // NEW
        DB_GET_OUTPUTS: '/api/v1/db/outputs'  // NEW
    }
};

// Auto-save predictions
await saveGeneratedOutput({
    output_type: 'prediction',
    drug_name: 'Aspirin',
    cancer_type: 'Colorectal',
    confidence_score: 0.85
});
```

---

##  Production Configuration

### Environment Variables (.env)

```env
# Required
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/oncopurpose
ENVIRONMENT=production

# Security
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60

# Performance
WORKERS=4
LOG_LEVEL=INFO
```

### Docker Deployment

```powershell
# Build production image
docker build -t oncopurpose:latest .

# Run with custom config
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e WORKERS=4 \
  -e DATABASE_URL=mysql+pymysql://... \
  oncopurpose:latest
```

---

##  Test Your Setup

```powershell
# 1. Health check (includes DB status)
Invoke-WebRequest http://localhost:8000/health | ConvertFrom-Json

# 2. Database stats
Invoke-WebRequest http://localhost:8000/api/v1/db/stats | ConvertFrom-Json

# 3. Search in database
Invoke-WebRequest "http://localhost:8000/api/v1/db/search?q=metformin"

# 4. Save test output
$body = @{
    output_type = "test"
    drug_name = "Aspirin"
    confidence_score = 0.95
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri http://localhost:8000/api/v1/db/output `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

---

##  What's Running

### Services
- **Backend API**: Port 8000
- **MySQL Database**: Port 3306
- **Interactive Docs**: http://localhost:8000/docs

### Data Loaded
-  **In-Memory**: 6,798 drugs (2-3 sec startup)
-  **Database**: 6,798 drugs (30-60 sec migration)
-  **Indexes**: 1,436 MOAs, 2,183 targets

### Performance
- In-memory search: <5ms
- Database search: 10-50ms
- Concurrent requests: 60/minute (rate limited)

---

##  Troubleshooting

### Database connection failed?
```powershell
# Check MySQL status
docker-compose ps

# View logs
docker-compose logs mysql

# Test connection
docker-compose exec mysql mysql -u oncopurpose_user -p
```

### Migration errors?
```powershell
# Clear and remigrate
python backend\migrate_data.py
# Type 'yes' when prompted
```

### Import errors?
```powershell
# Install missing packages
pip install pymysql cryptography python-dotenv slowapi
```

---

##  Production Checklist

-  Change default passwords in `.env`
-  Set specific CORS origins (not "*")
-  Enable rate limiting
-  Use HTTPS in production
-  Set `ENVIRONMENT=production`
-  Increase `WORKERS` for production (4+)
-  Monitor `/health` endpoint
-  Backup MySQL database regularly

---

##  You're Production Ready!

### What You Have Now:

1.  **Dockerized** - One-command deployment
2.  **Database** - MySQL with persistent storage
3.  **Rate Limited** - 60 req/min protection
4.  **Output Storage** - Save all predictions ⭐
5.  **Error Handling** - Production-grade middleware
6.  **Health Monitoring** - Database status checks
7.  **Frontend Ready** - Configuration included
8.  **Documentation** - Complete API docs at `/docs`

### Quick Commands

```powershell
# Start production
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down

# Full reset (removes data!)
docker-compose down -v
```

---

**Built for Founders Fest 2025**   
**6,798 drugs • MySQL Database • Production Ready**
