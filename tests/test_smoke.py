"""Smoke test: the assistant module parses and exposes its expected entry point.

Avoids importing heavy runtime deps (pyttsx3 etc.); structural check only.
"""
import ast
from pathlib import Path

MODULE = Path(__file__).parent.parent / "shiv_ai_assistant.py"


def test_module_parses_and_has_agi_class():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    classes = {
        n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
    }
    assert "ShivAI_AGI" in classes, "ShivAI_AGI class missing"
    # Regression: run() was truncated mid-string and broke py_compile.
    src = MODULE.read_text(encoding="utf-8")
    assert 'self.speak("Welcome to Shiv AI. I am ready to assist you.")' in src
