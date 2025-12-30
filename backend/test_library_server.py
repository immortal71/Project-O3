"""
Simple test server for library API
"""
from fastapi import FastAPI
import uvicorn
from library_api import router as library_router

app = FastAPI(title="Library API Test")
app.include_router(library_router)

@app.get("/")
def read_root():
    return {"status": "Library API Test Server", "endpoints": ["/api/v1/library/papers", "/api/v1/library/stats"]}

if __name__ == "__main__":
    print("Starting library API test server on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
