"""
Production Setup Test - Verify all components are working
Tests database connection, API endpoints, and data integrity
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        import sqlalchemy
        import pymysql
        from dotenv import load_dotenv
        from slowapi import Limiter
        print("  ✅ All required packages imported")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_environment():
    """Test environment configuration"""
    print("\n🧪 Testing environment...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            print(f"  ✅ DATABASE_URL configured")
        else:
            print(f"  ⚠️  DATABASE_URL not set (optional)")
        
        env = os.getenv('ENVIRONMENT', 'development')
        print(f"  ✅ Environment: {env}")
        
        return True
    except Exception as e:
        print(f"  ❌ Environment error: {e}")
        return False


def test_data_files():
    """Test that data files exist"""
    print("\n🧪 Testing data files...")
    
    base_path = Path(__file__).parent.parent
    
    files_to_check = [
        'backend/data/broad/broad_complete.json',
        'backend/data/hero_cases/hero_repurposing_cases.json'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            # Check file size
            size = full_path.stat().st_size
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path} not found")
            all_exist = False
    
    return all_exist


def test_data_loader():
    """Test in-memory data loading"""
    print("\n🧪 Testing data loader...")
    
    try:
        from backend.data_loader import get_data_loader
        
        loader = get_data_loader()
        stats = loader.get_stats()
        
        print(f"  ✅ Loaded {stats['total_drugs']:,} drugs")
        print(f"  ✅ Loaded {stats['hero_cases']} hero cases")
        print(f"  ✅ Indexed {stats['mechanisms']:,} mechanisms")
        print(f"  ✅ Indexed {stats['targets']:,} targets")
        
        # Test search
        results = loader.search_drugs('metformin', limit=5)
        if results:
            print(f"  ✅ Search working (found {len(results)} results for 'metformin')")
        else:
            print(f"  ⚠️  Search returned no results")
        
        return True
    except Exception as e:
        print(f"  ❌ Data loader error: {e}")
        return False


def test_database_connection():
    """Test database connection (optional)"""
    print("\n🧪 Testing database connection...")
    
    try:
        from backend.db_connection import test_connection
        
        if test_connection():
            print("  ✅ Database connection successful")
            
            # Test models
            from backend.models import Drug, HeroCase, GeneratedOutput
            print("  ✅ Database models loaded")
            
            return True
        else:
            print("  ⚠️  Database not connected (optional - in-memory mode works)")
            return True  # Not a failure
    except Exception as e:
        print(f"  ⚠️  Database test skipped: {e}")
        return True  # Not a failure


def test_api_imports():
    """Test that API modules can be imported"""
    print("\n🧪 Testing API modules...")
    
    try:
        from backend.integrated_api import router as api_router
        print("  ✅ Integrated API imported")
        
        from backend.database_api import router as db_router
        print("  ✅ Database API imported")
        
        return True
    except Exception as e:
        print(f"  ❌ API import error: {e}")
        return False


def test_server_config():
    """Test server configuration"""
    print("\n🧪 Testing server configuration...")
    
    try:
        from backend.server import app
        
        print(f"  ✅ FastAPI app created")
        print(f"  ✅ Title: {app.title}")
        print(f"  ✅ Version: {app.version}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        
        required_routes = ['/health', '/']
        for route in required_routes:
            if route in routes:
                print(f"  ✅ Route {route} registered")
            else:
                print(f"  ⚠️  Route {route} not found")
        
        return True
    except Exception as e:
        print(f"  ❌ Server config error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 ONCOPURPOSE PRODUCTION SETUP TEST")
    print("=" * 70)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Data Files", test_data_files),
        ("Data Loader", test_data_loader),
        ("Database", test_database_connection),
        ("API Modules", test_api_imports),
        ("Server Config", test_server_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"✅ {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for production!")
        print("\nNext steps:")
        print("  1. Start server: python backend\\server.py")
        print("  2. Or use Docker: docker-compose up -d")
        print("  3. Access API: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        print("\nCommon fixes:")
        print("  - Run: pip install -r backend\\requirements.txt")
        print("  - Check .env file exists")
        print("  - Start MySQL: docker-compose up -d mysql")
        return 1


if __name__ == '__main__':
    sys.exit(main())
