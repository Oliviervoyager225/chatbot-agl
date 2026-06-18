import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import gradio as gr
from backend.app.api import app as fastapi_app
from backend.gradio import _create_app

_demo = _create_app()
app = gr.mount_gradio_app(fastapi_app, _demo, path="/gradio")
