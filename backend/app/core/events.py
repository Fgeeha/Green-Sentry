from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.core.logging import setup_logging


def create_start_app_handler(app: FastAPI):
    """Startup event handler"""
    async def start_app() -> None:
        setup_logging()
        # Additional startup tasks
        pass
    return start_app


def create_stop_app_handler(app: FastAPI):
    """Shutdown event handler"""
    async def stop_app() -> None:
        # Cleanup tasks
        pass
    return stop_app