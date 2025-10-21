# AI-Agent

A local AI coding assistant that uses the Google GenAI SDK to plan and execute filesystem and Python operations inside a constrained working directory (default: `./calculator`). The agent accepts a user prompt, asks the model for a plan (including function calls), executes safe helper functions, and returns a final answer.

---

## Table of contents

- Features
- Requirements
- Quick start
- Using the `uv` package manager
- Usage
- Project layout
- How the system prompt is applied
- Available tools
- Running tests
- Troubleshooting
- Security notes
- Contributing
- License

---

## Features

- Sends a prompt to a Gemini model and accepts structured function-call responses.
- Built-in tools to:
  - List directory contents
  - Read file contents (truncated)
  - Write files
  - Execute Python files within a sandboxed working directory
- Iterative loop: handles multiple model-function-call cycles until a final textual response is produced.
- Verbose mode for debugging token usage and function call flow.

---

## Requirements

- macOS / Linux / Windows with Python 3.14
- Python packages (see `pyproject.toml` or `requirements.txt`), examples:
  - google-genai
  - python-dotenv

Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
python -m pip install -r requirements.txt
```

Set your Gemini API key (create `.env` or export):
```env
GEMINI_API_KEY=sk-...
```

---

## Quick start

Run the assistant with a prompt:

```bash
python main.py "How do I fix the calculator?" --verbose
```

- `--verbose` prints token usage, function call details and tool results.
- Provide the prompt as a single argument. Multiple arguments are joined.

---

## Using the `uv` package manager

If you prefer the `uv` package manager to run scripts (you used `uv run tests.py`), the agent works with `uv` as a runner. Typical `uv` usage (no dependency management implied — `uv` simply runs scripts in your environment):

- Run the assistant:
```bash
uv run main.py "How do I fix the calculator?" -- --verbose
```
Note: some `uv` setups pass script args after `--`. If your `uv` variant accepts arguments directly, use:
```bash
uv run main.py "How do I fix the calculator?" --verbose
```

- Run tests/example script:
```bash
uv run calculator/tests.py
```

If `uv` is not installed or the `uv` command is not on PATH, use the Python fallback:
```bash
python3 main.py "Prompt here" --verbose
python3 calculator/tests.py
```

If `uv` reports "command not found", install or enable `uv` per its documentation, or run with Python directly.

---

## Usage examples

- List files in the calculator directory:
  - Prompt: `List files in the calculator directory.`
- Show file contents:
  - Prompt: `Show contents of calculator/pkg/calculator.py`
- Run tests:
  - Prompt: `Run the calculator tests.`

Example run:
```bash
python main.py "Run the calculator tests" --verbose
# or, if using uv:
uv run calculator/tests.py
```

---

## Project layout

Important files and modules:

- `main.py` — entrypoint and orchestration loop.
- `prompts.py` — contains `system_prompt` used to instruct the model.
- `functions/` — tool implementations and schema declarations:
  - `functions/call_function.py` — dispatcher, `available_functions` schemas.
  - `functions/get_files_info.py` — list files and directories.
  - `functions/get_file_content.py` — read file contents (truncated).
  - `functions/write_file.py` — write or overwrite files.
  - `functions/run_python_file.py` — run Python files in working dir and collect stdout/stderr.
- `calculator/` — example project used as the working directory:
  - `calculator/pkg/calculator.py`, `calculator/tests.py`, etc.

---

## How the system prompt is applied

Some SDK/model versions expect the system instruction as a dedicated system-role message inside the `contents` array rather than (or in addition to) a `GenerateContentConfig.system_instruction` field.

If the system prompt appears ignored, ensure `main.py` includes a system message as the first content element, for example:

```python
messages = [
    types.Content(role="system", parts=[types.Part(text=system_prompt)]),
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]
```

Also ensure `GenerateContentConfig(system_instruction=system_prompt)` is provided if your SDK version supports it. Use both when in doubt.

---

## Available tools (overview)

Each tool exposes a schema (in `functions/call_function.py`) and is passed to the model so it can return function calls.

- get_files_info
  - parameter: `directory` (string)
  - returns: list of file/directory names and metadata
- get_file_content
  - parameter: `file_path` (string)
  - returns: content truncated to a safe length (e.g., 10,000 chars)
- write_file
  - parameters: `file_path` (string), `content` (string)
  - writes file under working directory
- run_python_file
  - parameter: `file_path` (string)
  - runs a Python file within the working directory and returns stdout/stderr and exit code

All tools enforce canonical path checks to prevent escape from the configured working directory.

---

## Running tests

Example: run tests for the calculator example

From the project root:
```bash
# run the example tests directly
python calculator/tests.py

# or use unittest module
python -m unittest calculator.tests

# with uv (if installed)
uv run calculator/tests.py
```

If tests import fails with circular import errors, inspect `calculator/pkg/calculator.py` for accidental self-imports and remove them. Ensure `calculator/pkg/__init__.py` exists.

---

## Troubleshooting

- "zsh: command not found: bootdev"
  - Means `bootdev` is not installed or not on PATH. Use the Python script directly.

- System prompt ignored:
  - Add a system-role message to `messages` as shown above.
  - Confirm SDK version and that `GenerateContentConfig.system_instruction` is supported.
  - Check `resp` for errors and validate `GEMINI_API_KEY`.

- Circular import when running tests:
  - Remove circular self-imports in module files (e.g., `from pkg.calculator import Calculator` inside `pkg/calculator.py`).
  - Ensure proper package initialization (`__init__.py`).

- Model returns no function calls or empty responses:
  - Check `resp` structure and `resp.usage_metadata` for tokens consumed.
  - Ensure `available_functions` is passed correctly to `GenerateContentConfig`.

---

## Security notes

- The agent restricts filesystem operations to a configured working directory (default: `./calculator`). Tools validate canonical paths and refuse operations outside that directory.
- File reads are truncated to prevent leaking huge files.
- Running arbitrary Python files has inherent risk — review code before running or run inside isolated environments.

---

## Contributing

- Add new tool functions under `functions/`. Export their JSON schema to `available_functions`.
- Update `prompts.py` to change instructions.
- Add tests under the `calculator/` example or create new example projects.
- Open issues or PRs with clear descriptions and reproducible steps.

---

## License

Choose and add a license file (e.g., `MIT`, `Apache-2.0`) in the repository root.
