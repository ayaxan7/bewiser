#!/usr/bin/env python3
"""
Render deployment startup script for BeWiser Smart Advisor
"""
import os
import sys
import uvicorn

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the FastAPI app
from app.main import app

if __name__ == "__main__":
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get("PORT", 10000))
    
    print("🚀 Starting BeWiser Smart Advisor...")
    print(f"📊 Server will be available on port {port}")
    print("📈 Endpoints:")
    print("  - GET / (Health check)")
    print("  - GET /top5smallcap (Basic fund analysis)")
    print("  - GET /top5smallcap-benchmark (Benchmark analysis)")
    print("  - GET /smart-advisor (Smart recommendations)")
    print("  - GET /docs (API documentation)")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
