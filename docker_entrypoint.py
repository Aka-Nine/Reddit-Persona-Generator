#!/usr/bin/env python3
"""Start gunicorn with PORT from the environment (no shell — avoids literal '$PORT' on Railway)."""
import os
import sys


def _port() -> str:
    raw = (os.environ.get("PORT") or "").strip()
    # Railway injects a numeric PORT. If someone set PORT to the literal "$PORT" in the dashboard, recover.
    if raw.isdigit() and int(raw) > 0:
        return raw
    return "8080"


def main() -> None:
    port = _port()
    bind = f"0.0.0.0:{port}"
    args = [
        "gunicorn",
        "--bind",
        bind,
        "--workers",
        "2",
        "--threads",
        "2",
        "--timeout",
        "180",
        "--graceful-timeout",
        "30",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "server:app",
    ]
    os.execvp("gunicorn", args)


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print(f"Failed to start gunicorn: {e}", file=sys.stderr)
        sys.exit(1)
