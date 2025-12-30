# OncoPurpose Production Setup Script
# Run this to set up the complete production environment

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🚀 ONCOPURPOSE PRODUCTION SETUP" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

# Step 1: Install Python dependencies
Write-Host "📦 Step 1: Installing Python dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python dependencies installed`n" -ForegroundColor Green

# Step 2: Check if MySQL is installed
Write-Host "🔍 Step 2: Checking for MySQL..." -ForegroundColor Yellow
$mysqlPath = Get-Command mysql -ErrorAction SilentlyContinue

if (-not $mysqlPath) {
    Write-Host "⚠️  MySQL not found. Please install MySQL 8.0 or use Docker." -ForegroundColor Yellow
    Write-Host "`nOption 1: Install MySQL manually from https://dev.mysql.com/downloads/installer/" -ForegroundColor Cyan
    Write-Host "Option 2: Use Docker Compose (recommended):" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d`n" -ForegroundColor White
    
    $useDocker = Read-Host "Use Docker Compose? (yes/no)"
    
    if ($useDocker -eq "yes") {
        Write-Host "`n🐳 Starting Docker Compose..." -ForegroundColor Yellow
        docker-compose up -d
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker Compose failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "⏳ Waiting for MySQL to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        Write-Host "✅ Docker containers started`n" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Please install MySQL and rerun this script" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "✅ MySQL found: $($mysqlPath.Source)`n" -ForegroundColor Green
}

# Step 3: Create .env file if it doesn't exist
Write-Host "📝 Step 3: Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Cyan
    Copy-Item ".env.template" ".env"
    Write-Host "✅ .env file created. Please update with your settings.`n" -ForegroundColor Green
}
else {
    Write-Host "✅ .env file already exists`n" -ForegroundColor Green
}

# Step 4: Migrate data to database
Write-Host "💾 Step 4: Migrating data to database..." -ForegroundColor Yellow
Write-Host "This will load 6,800+ drugs and hero cases into MySQL`n" -ForegroundColor Cyan

$migrate = Read-Host "Run database migration now? (yes/no)"

if ($migrate -eq "yes") {
    python backend\migrate_data.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Database migration failed. You can run it later with:" -ForegroundColor Yellow
        Write-Host "   python backend\migrate_data.py`n" -ForegroundColor White
    }
    else {
        Write-Host "✅ Database migration completed`n" -ForegroundColor Green
    }
}
else {
    Write-Host "⏭️  Skipping migration. Run later with:" -ForegroundColor Yellow
    Write-Host "   python backend\migrate_data.py`n" -ForegroundColor White
}

# Step 5: Create output directories
Write-Host "📁 Step 5: Creating output directories..." -ForegroundColor Yellow
$directories = @("logs", "outputs")

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  Created $dir/" -ForegroundColor Cyan
    }
}
Write-Host "✅ Directories created`n" -ForegroundColor Green

# Step 6: Ready to run
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "======================================================================`n" -ForegroundColor Cyan

Write-Host "📋 WHAT'S NEXT:`n" -ForegroundColor Yellow

Write-Host "1️⃣  Start the server:" -ForegroundColor Cyan
Write-Host "   python backend\server.py`n" -ForegroundColor White

Write-Host "2️⃣  Access the API:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs`n" -ForegroundColor White

Write-Host "3️⃣  Test endpoints:" -ForegroundColor Cyan
Write-Host "   - In-memory:  http://localhost:8000/api/v1/search?q=metformin" -ForegroundColor White
Write-Host "   - Database:   http://localhost:8000/api/v1/db/search?q=aspirin`n" -ForegroundColor White

Write-Host "4️⃣  For Docker deployment:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d`n" -ForegroundColor White

Write-Host "======================================================================`n" -ForegroundColor Cyan
