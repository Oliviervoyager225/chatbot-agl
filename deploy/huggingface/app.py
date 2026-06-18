import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.app.api import app
