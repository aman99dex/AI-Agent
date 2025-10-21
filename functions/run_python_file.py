import os
import subprocess

from google.genai import types


def run_python_file(working_directory: str, file_path: str) -> str:
    try:
        working_path = os.path.abspath(working_directory)
        full_path = os.path.abspath(os.path.join(working_path, file_path))

        if not full_path.startswith(working_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(full_path):
            return f'Error: File "{file_path}" not found.'

        if not full_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'
    except Exception as e:
        return f"Error: {e}"

    try:
        result = subprocess.run(
            ["python3", file_path],
            cwd=working_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        output: list[str] = []

        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")

        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        return "\n".join(output) if output else "No output produced."
    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python 3 file within the working directory and returns the output from the interpreter.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)