"""Verify the Roboflow setup for this project (see docs/ROBOFLOW_SETUP.md).

Checks, in order:
- .env / environment: ROBOFLOW_API_KEY and ROBOFLOW_WORKSPACE present
- Python packages: roboflow, python-dotenv, requests (requirements-roboflow.txt)
- .mcp.json at the repo root registering the Roboflow MCP server
- Live API: the key actually authenticates against https://api.roboflow.com

Prints a PASS/FAIL line per check plus the fix for anything failing. Exits
non-zero if any check fails, so it can gate scripts/CI. Never prints the API
key itself.

Usage:
    python tools/roboflow_check.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PASS = "PASS"
FAIL = "FAIL"
WARN = "warn"


def check(status: str, label: str, detail: str = "") -> bool:
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    return status != FAIL


def load_env() -> None:
    """Load .env via python-dotenv if available, else a minimal parser."""
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv  # noqa: PLC0415 — optional dependency

        load_dotenv(env_path)
    except ImportError:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    ok = True
    load_env()

    env_file = REPO_ROOT / ".env"
    ok &= check(
        PASS if env_file.is_file() else WARN,
        ".env file at repo root",
        str(env_file) if env_file.is_file() else "not found — fine if keys come from the shell environment",
    )

    api_key = os.environ.get("ROBOFLOW_API_KEY", "")
    ok &= check(
        PASS if api_key else FAIL,
        "ROBOFLOW_API_KEY set",
        f"({len(api_key)} chars)" if api_key else "add it to .env (gitignored) — never commit it",
    )
    workspace = os.environ.get("ROBOFLOW_WORKSPACE", "")
    ok &= check(
        PASS if workspace else WARN,
        "ROBOFLOW_WORKSPACE set",
        workspace or "needed by tools/roboflow_upload.py; add to .env",
    )

    for package, why in (
        ("roboflow", "SDK used by tools/roboflow_upload.py"),
        ("dotenv", ".env loading (python-dotenv)"),
        ("requests", "serverless inference API client (tools/roboflow_eval.py)"),
    ):
        found = importlib.util.find_spec(package) is not None
        ok &= check(
            PASS if found else FAIL,
            f"package '{package}' installed",
            why if found else f"{why} — pip install -r requirements-roboflow.txt",
        )

    mcp_path = REPO_ROOT / ".mcp.json"
    mcp_ok = False
    if mcp_path.is_file():
        try:
            mcp_ok = "roboflow" in json.loads(mcp_path.read_text()).get("mcpServers", {})
        except (json.JSONDecodeError, OSError):
            mcp_ok = False
    ok &= check(
        PASS if mcp_ok else WARN,
        ".mcp.json registers the Roboflow MCP server",
        "" if mcp_ok else "copy it from the claude_MV template root (or roboflow/computer-vision-skills)",
    )

    if api_key:
        try:
            import requests  # noqa: PLC0415 — optional dependency, checked above

            resp = requests.get("https://api.roboflow.com/", params={"api_key": api_key}, timeout=20)
            if resp.status_code == 200:
                workspaces = list(resp.json().get("workspaces", {}) or {})
                ok &= check(PASS, "API key authenticates", f"workspaces visible: {workspaces or 'none listed'}")
            else:
                ok &= check(FAIL, "API key authenticates", f"HTTP {resp.status_code} from api.roboflow.com — check the key")
        except ImportError:
            ok &= check(WARN, "API key authenticates", "skipped — requests not installed")
        except Exception as exc:  # network errors shouldn't crash the report
            ok &= check(WARN, "API key authenticates", f"could not reach api.roboflow.com: {exc}")
    else:
        ok &= check(WARN, "API key authenticates", "skipped — no key set")

    print("\nAll required checks passed." if ok else "\nSetup incomplete — fix the FAIL lines above (docs/ROBOFLOW_SETUP.md).")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
