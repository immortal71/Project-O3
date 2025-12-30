#  OncoPurpose - Production Deployment Guide

**Complete drug repurposing platform with 6,800+ compounds and MySQL database**

---

##  Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [API Documentation](#api-documentation)
7. [Frontend Integration](#frontend-integration)
8. [Docker Deployment](#docker-deployment)
9. [Production Configuration](#production-configuration)
10. [Troubleshooting](#troubleshooting)

---

##  Quick Start

### Option 1: Docker (Recommended)

```powershell
# Clone and setup
cd Project-O3
docker-compose up -d

# Wait for MySQL to initialize (~15 seconds)
Start-Sleep -Seconds 15

# Migrate data
docker-compose exec backend python backend/migrate_data.py

# Access the application
# API: http://localhost:8000/docs
# Frontend: Open index (1).html in browser
```

### Option 2: Manual Setup

```powershell
# Run automated setup script
.\setup.ps1

# Start the server
python backend\server.py

# Access at http://localhost:8000
```

---

##  System Requirements

### Required
- **Python**: 3.11 or higher
- **MySQL**: 8.0 or higher (or Docker)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space

### Optional
- **Docker Desktop**: For containerized deployment
- **Node.js**: For frontend development tools

---

##  Installation

### 1. Install Python Dependencies

```powershell
pip install -r backend\requirements.txt
```

**Key packages:**
- `fastapi` - Web framework
- `sqlalchemy` - ORM for database
- `pymysql` - MySQL connector
- `slowapi` - Rate limiting
- `uvicorn` - ASGI server

### 2. Install MySQL

#### Option A: Docker (Recommended)
```powershell
docker-compose up -d mysql
```

#### Option B: Manual Installation
Download from [MySQL Official Site](https://dev.mysql.com/downloads/installer/)

---

##  Database Setup

### 1. Configure Environment

Edit `.env` file (created from `.env.template`):

```env
# Database
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=oncopurpose
MYSQL_USER=oncopurpose_user
MYSQL_PASSWORD=oncopurpose_pass
DATABASE_URL=mysql+pymysql://oncopurpose_user:oncopurpose_pass@localhost:3306/oncopurpose

# Environment
ENVIRONMENT=development  # or 'production'

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5500
```

### 2. Initialize Database

The database schema includes:
- **drugs** - 6,798 compounds from Broad Institute Hub
- **hero_cases** - 15 gold-standard repurposing examples
- **generated_outputs** - Store predictions/images
- **mechanisms** - 1,436 mechanisms of action
- **targets** - 2,183 drug targets

### 3. Migrate Data

```powershell
python backend\migrate_data.py
```

**Expected output:**
```
 Migrated 6798 drugs
 Hero Cases: 15
 Mechanisms: 1436
 Targets: 2183
```

**Migration time:** ~30-60 seconds

---

##  Running the Application

### Development Mode

```powershell
# Start server with auto-reload
python backend\server.py
```

**Server will start on:** `http://localhost:8000`

**Features enabled:**
-  Auto-reload on code changes
-  Detailed error messages
-  CORS: Allow all origins
-  Single worker process

### Production Mode

```powershell
# Set environment to production
$env:ENVIRONMENT="production"
$env:WORKERS="4"

python backend\server.py
```

**Features enabled:**
-  4 worker processes
-  Restricted CORS
-  Error masking
-  Rate limiting

---

##  API Documentation

### Endpoint Structure

The API has **two modes**:

#### 1. In-Memory Endpoints (Fast, no DB required)
- `/api/v1/search` - Search drugs
- `/api/v1/drug/{name}` - Drug details
- `/api/v1/hero-cases` - Gold-standard examples
- `/api/v1/stats` - Statistics
- `/api/v1/oncology` - Oncology drugs
- `/api/v1/mechanism/{moa}` - Drugs by mechanism

#### 2. Database Endpoints (Persistent storage)
- `/api/v1/db/search` - Search in database
- `/api/v1/db/drug/{name}` - Drug from database
- `/api/v1/db/hero-cases` - Hero cases from DB
- `/api/v1/db/stats` - Database statistics
- `/api/v1/db/output` - Save generated output **(NEW)**
- `/api/v1/db/outputs` - Get saved outputs **(NEW)**

### Example Requests

#### Search Drugs
```javascript
GET /api/v1/search?q=metformin&limit=20

Response:
{
  "query": "metformin",
  "total_results": 5,
  "drugs": [...],
  "hero_cases": [...]
}
```

#### Save Generated Output
```javascript
POST /api/v1/db/output

Body:
{
  "output_type": "prediction",
  "drug_name": "Aspirin",
  "cancer_type": "Colorectal",
  "confidence_score": 0.85,
  "output_data": {
    "mechanism": "COX-2 inhibition",
    "pathways": ["inflammation", "angiogenesis"]
  }
}

Response:
{
  "id": 123,
  "output_type": "prediction",
  "session_id": "uuid-here",
  "created_at": "2025-12-25T10:30:00"
}
```

#### Get Saved Outputs
```javascript
GET /api/v1/db/outputs?output_type=prediction&limit=50

Response:
[
  {
    "id": 123,
    "output_type": "prediction",
    "drug_name": "Aspirin",
    "cancer_type": "Colorectal",
    "confidence_score": 0.85,
    "created_at": "2025-12-25T10:30:00"
  }
]
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI

---

##  Frontend Integration

### 1. Include Configuration

Add to your HTML files:

```html
<!-- Frontend Configuration -->
<script src="frontend-config.js"></script>

<!-- Dashboard Generator (if using) -->
<script src="dashboard-generator.js"></script>
```

### 2. Use API Functions

```javascript
// Search drugs
const results = await searchDrugs('metformin', 20);

// Get drug details
const drug = await getDrugDetails('aspirin');

// Get hero cases
const heroes = await getHeroCases();

// Save generated output
await saveGeneratedOutput({
    output_type: 'prediction',
    drug_name: 'Metformin',
    cancer_type: 'Breast',
    confidence_score: 0.87
});
```

### 3. Configuration Options

Edit `frontend-config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    USE_DATABASE: true,  // Use database endpoints
    TIMEOUT: 30000,
    RESULTS_PER_PAGE: 20
};
```

---

##  Docker Deployment

### Full Stack Deployment

```powershell
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (caution: deletes data)
docker-compose down -v
```

### Services

- **mysql** - Port 3306
- **backend** - Port 8000

### Production Docker Build

```dockerfile
# Build production image
docker build -t oncopurpose:latest .

# Run with custom settings
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e WORKERS=4 \
  oncopurpose:latest
```

---

##  Production Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development` or `production` |
| `DATABASE_URL` | MySQL local | Full database connection string |
| `CORS_ORIGINS` | localhost | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `RATE_LIMIT_PER_MINUTE` | `60` | API requests per minute |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `WORKERS` | `1` | Number of worker processes |

### Rate Limiting

**Default limits:**
- General endpoints: 60 requests/minute
- Health check: 120 requests/minute

**Customize:**
```python
@app.get("/api/v1/custom")
@limiter.limit("10/minute")
async def custom_endpoint(request: Request):
    ...
```

### Security Best Practices

1. **Change default passwords** in `.env`
2. **Set specific CORS origins** for production
3. **Use HTTPS** with reverse proxy (nginx, Caddy)
4. **Enable rate limiting** in production
5. **Monitor logs** in `/logs` directory

---

##  Troubleshooting

### Database Connection Failed

```powershell
# Check MySQL is running
docker-compose ps

# Test connection
mysql -u oncopurpose_user -p -h localhost

# View MySQL logs
docker-compose logs mysql
```

### Migration Errors

```powershell
# Clear database and remigrate
python backend\migrate_data.py

# Select 'yes' when prompted to clear existing data
```

### Port Already in Use

```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Stop the process
Stop-Process -Id <PID>

# Or use different port
$env:PORT="8001"
python backend\server.py
```

### Module Not Found Errors

```powershell
# Reinstall dependencies
pip install -r backend\requirements.txt --force-reinstall

# Verify installation
pip list | Select-String "fastapi|sqlalchemy|pymysql"
```

### Frontend Can't Connect

1. Check server is running: `http://localhost:8000/health`
2. Check CORS settings in `.env`
3. Open browser console for errors
4. Verify `frontend-config.js` has correct `API_BASE_URL`

---

##  Monitoring

### Health Check

```powershell
# Check server health
Invoke-WebRequest http://localhost:8000/health | ConvertFrom-Json

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "in_memory_drugs": 6798
}
```

### Logs

```powershell
# View server logs (if running in background)
docker-compose logs -f backend

# Or check logs directory
Get-Content logs\server.log -Tail 50
```

---

##  Next Steps

1.  **Test the API** - Visit `http://localhost:8000/docs`
2.  **Explore data** - Search for "metformin", "aspirin", "cancer"
3.  **Generate outputs** - Use the generate button and check database
4.  **Monitor performance** - Check `/health` and database stats
5.  **Deploy to cloud** - Use Docker Compose for cloud deployment

---

##  Support

- **Documentation**: `/docs` endpoint
- **Issues**: Check logs in `/logs` directory
- **Database**: Use `migrate_data.py` to reset

---

**Built for Founders Fest 2025** 
