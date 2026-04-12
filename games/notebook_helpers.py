import marimo as mo
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr


def reveal_and_run(
    button_value: int,
    filepath: str,
    exec_namespace: dict = None,
    output_var: str = None,
):
    """Reads a file, displays it, executes it, and returns the UI + extracted variable."""
    if exec_namespace is None:
        exec_namespace = {}

    if button_value > 0:
        with open(filepath, "r") as f:
            code = f.read()

        editor = mo.ui.code_editor(value=code, language="python")
        original_replace = mo.output.replace

        def patched_replace(live_frame):
            original_replace(mo.vstack([editor, live_frame]))

        mo.output.replace = patched_replace

        stdout_catcher = io.StringIO()
        stderr_catcher = io.StringIO()
        traceback_error = None

        try:
            with redirect_stdout(stdout_catcher), redirect_stderr(stderr_catcher):
                exec(code, exec_namespace)
        except Exception:
            traceback_error = traceback.format_exc()
        finally:
            mo.output.replace = original_replace

        elements = [editor]

        if stdout_catcher.getvalue():
            elements.append(
                mo.md(
                    f"**Standard Output:**\n```text\n{stdout_catcher.getvalue()}\n```"
                )
            )
        if stderr_catcher.getvalue():
            elements.append(
                mo.md(f"**Standard Error:**\n```text\n{stderr_catcher.getvalue()}\n```")
            )
        if traceback_error:
            elements.append(
                mo.md(f"**Execution Crash:**\n```python\n{traceback_error}\n```")
            )

        extracted_obj = None
        if output_var and output_var in exec_namespace:
            extracted_obj = exec_namespace[output_var]

        return mo.vstack(elements), extracted_obj

    else:
        return mo.md("🔒 Click the button below to reveal the solution"), None
