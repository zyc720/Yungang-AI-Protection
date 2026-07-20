"""
Yungang Grottoes Intelligent E-Dictionary — Backend Entry Point.

Usage:
    python main.py
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
from app.core.app_factory import create_app
from app.config.settings import get_settings

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower(),
    )
