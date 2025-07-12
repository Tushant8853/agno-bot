#!/usr/bin/env python3
"""
Simple script to run the Agno chatbot application.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def main():
    """Run the Agno chatbot application."""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("Please copy env.example to .env and configure your environment variables.")
        print("Required variables:")
        print("  - GOOGLE_GEMINI_API_KEY")
        print("  - ZEP_API_KEY")
        print("  - MEM0_API_KEY")
        print("  - DATABASE_URL")
        print("  - SECRET_KEY")
        print()
        print("💡 Note: This is the backend directory. Make sure you're running from the backend folder.")
        print("   Virtual environment is located at: .venv/")
        print()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO").lower()
    
    print(f"🚀 Starting Agno Bot...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Log Level: {log_level}")
    print()
    
    try:
        # Run the application
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Agno Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting Agno Bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 