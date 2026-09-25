# Web Coding Agent

A small Python coding agent that can inspect and modify files inside its workspace. It is designed for requests such as changing the theme or behavior of the included todo app, while verifying that edits really reached disk.

## What It Does

- Accepts natural-language requests in an interactive terminal loop.
- Uses structured JSON responses to choose between planning, tool calls, and final answers.
- Reads project files with `read_file`.
- Rewrites project files with `write_file`, then reads them back and reports a SHA-256 digest.
- Runs Windows-compatible commands from the project workspace.
- Prevents file edits outside the project directory.
- Returns tool observations to the model before it claims completion.

## Project Layout

```text
agent.py             Main web coding agent
main.py              Simple weather API example
todo_app/index.html  Todo app markup
todo_app/script.js   Todo app behavior
todo_app/style.css   Todo app styling
```

## Requirements

- Python 3.10 or newer
- An OpenAI API key
- Windows PowerShell or another supported shell

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env` or share its contents.

## Run the Agent

```powershell
python agent.py
```

Example requests:

```text
Change the todo app to a dark blue theme.
Add a completed checkbox to every todo item.
Make the todo app responsive on mobile.
```

For a file edit, the model sends `write_file` input as JSON:

```json
{"file_path":"todo_app/style.css","content":"body { background: #121212; }"}
```

The adapter parses that JSON into the two Python arguments required by `write_file`. The write function then reads the file back before returning success, so a final response is based on a real verified edit rather than an assumed command result.

## Open the Todo App

Open [todo_app/index.html](todo_app/index.html) directly in a browser, or use VS Code Live Server.

## Security Notes

This is a learning project. The agent executes commands supplied by the model, so use it only in a workspace you trust. File-writing tools are restricted to this project directory, and secrets in `.env` are excluded from Git.
