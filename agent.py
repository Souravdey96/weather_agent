from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import hashlib
import json
import requests
import subprocess
import time

load_dotenv()
client = OpenAI()
WORKSPACE_ROOT = Path(__file__).resolve().parent


def resolve_workspace_path(file_path: str) -> Path:
    candidate = (WORKSPACE_ROOT / file_path).resolve()
    if candidate != WORKSPACE_ROOT and WORKSPACE_ROOT not in candidate.parents:
        raise ValueError("Path must stay inside the workspace")
    return candidate


def read_file(file_path: str) -> str:
    try:
        path = resolve_workspace_path(file_path)
        if not path.is_file():
            return f"Error: File not found: {file_path}"
        return path.read_text(encoding="utf-8")
    except Exception as error:
        return f"Read failed: {error}"


def write_file(file_path: str, content: str) -> str:
    try:
        path = resolve_workspace_path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        written = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(written.encode("utf-8")).hexdigest()[:12]
        return f"Wrote and verified {file_path} ({len(written)} bytes, sha256:{digest})"
    except Exception as error:
        return f"Write failed: {error}"


def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = "\n".join(
            part for part in (result.stdout.strip(), result.stderr.strip()) if part
        )
        if result.returncode != 0:
            return f"Command failed (exit code {result.returncode}):\n{output}"
        return output or "Command completed successfully (exit code 0)."
    except Exception as error:
        return f"Execution failed: {error}"


def test_weather(location: str) -> str:
    url = f"https://wttr.in/{location}?format=%C+%t"
    try:
        response = requests.get(url, timeout=5)
        return response.text if response.status_code == 200 else f"Server error code: {response.status_code}"
    except Exception as error:
        return f"Network error details: {error}"


def invoke_tool(tool_name: str, tool_input: str) -> str:
    if tool_name == "write_file":
        try:
            arguments = json.loads(tool_input)
            file_path = arguments["file_path"]
            content = arguments["content"]
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            return (
                "Tool input error: write_file requires JSON with "
                f"file_path and content ({error})"
            )
        return write_file(file_path, content)

    if tool_name == "read_file":
        return read_file(tool_input)
    if tool_name == "run_command":
        return run_command(tool_input)
    if tool_name == "test_weather":
        return test_weather(tool_input)
    return f"Error: Tool not found: {tool_name}"


available_tools = {
    "test_weather": test_weather,
    "run_command": run_command,
    "read_file": read_file,
    "write_file": write_file,
}

SYSTEM_PROMPT = """
You are a web coding agent working in the project workspace.
Return exactly one JSON object at a time:
{"step":"START|PLAN|OUTPUT|TOOL","content":"...","tool":"...","input":"..."}
Use TOOL steps when you need to inspect or change files, and wait for the OBSERVE result.

File editing rules:
- Use read_file with a project-relative path to inspect files.
- For write_file, set input to a JSON string exactly like {"file_path":"todo_app/style.css","content":"body { color: red; }"}.
- write_file writes and reads the file back before it reports success.
- Never use Unix heredocs, cat, or shell redirection. This agent runs on Windows.
- Never claim a file task is complete unless write_file reported that it wrote and verified the file.
- Use run_command only for Windows-compatible commands. Treat a nonzero exit code as failure.

Available tools:
- test_weather(location: str)
- run_command(command: str)
- read_file(file_path: str)
- write_file(file_path: str, content: str)
"""


class MyOutputFormat(BaseModel):
    step: str = Field(..., description="START, PLAN, OUTPUT, or TOOL")
    content: Optional[str] = None
    tool: Optional[str] = None
    input: Optional[str] = None


message_history = [{"role": "system", "content": SYSTEM_PROMPT}]

while True:
    user_query = input("👉 ")
    message_history.append({"role": "user", "content": user_query})

    for _ in range(15):
        try:
            response = client.chat.completions.parse(
                model="gpt-4o",
                response_format=MyOutputFormat,
                messages=message_history,
            )
        except RateLimitError as error:
            print("Rate limit hit, retrying in 3s...", error)
            time.sleep(3)
            continue

        raw_result = response.choices[0].message.content
        message_history.append({"role": "assistant", "content": raw_result})
        parsed_result = response.choices[0].message.parsed
        if parsed_result is None:
            print("Failed to parse output schema.")
            break

        step = parsed_result.step.upper()
        if step == "TOOL":
            tool_name = parsed_result.tool
            tool_input = parsed_result.input or ""
            print(f"Call Tool: {tool_name} ({tool_input})")
            tool_output = invoke_tool(tool_name, tool_input)
            print(f"Observe: {tool_output}")
            message_history.append({
                "role": "developer",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_name,
                    "input": tool_input,
                    "output": tool_output,
                }),
            })
            continue

        if step in {"START", "PLAN"}:
            print(parsed_result.content or "")
        elif step == "OUTPUT":
            print(f"Final Answer: {parsed_result.content or ''}")
            break
        else:
            print(f"Unknown step: {step}")
            break

    print("\n")
