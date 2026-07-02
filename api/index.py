import os
import sys
from pathlib import Path

# Add the backend directory to the Python path so app imports resolve correctly
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_path))

# Import the FastAPI app instance from app.main
from app.main import app
