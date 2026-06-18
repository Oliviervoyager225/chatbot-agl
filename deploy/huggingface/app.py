import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.gradio import _create_app

demo = _create_app()

if __name__ == "__main__":
    demo.launch()
