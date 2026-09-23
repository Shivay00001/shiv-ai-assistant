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


def test_run_has_event_loop():
    """Regression: run() must contain a real input loop that dispatches
    to process_command(), not just print a banner."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    run_fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "run"
    )
    nodes = list(ast.walk(run_fn))
    assert any(isinstance(n, ast.While) for n in nodes), "run() has no loop"
    called = {
        n.func.attr
        for n in nodes
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "process_command" in called, "run() never dispatches to process_command()"


def test_cli_entry_point_exists():
    """Regression: module must expose main() and a __main__ guard so
    `python shiv_ai_assistant.py --help` works."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    funcs = {
        n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
    }
    assert "main" in funcs, "main() CLI entry point missing"
    src = MODULE.read_text(encoding="utf-8")
    assert '__name__ == "__main__"' in src, "__main__ guard missing"
