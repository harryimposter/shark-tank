#!/usr/bin/env python3
"""Market Map — launcher stub (standard library only, no API calls).

This script does NOT generate the brief. The brief is produced by Claude Code
itself: you tell Claude "run the Market Map", and Claude does all the web
searches, follows the system prompt and 18-section spec in PROMPT.md, marks the
trades.json book to market, renders the inline-SVG charts via charts.py, and
writes the complete self-contained output.html using the engine in book.py.

Running this file just mints a session id and prints the ready line, so you have
a handle to paste into Claude Code.

    python main.py
"""

import uuid
from datetime import date


def main():
    session_id = f"market-map-{date.today().isoformat()}-{uuid.uuid4().hex[:8]}"
    print("Ready — paste this session ID into Claude Code")
    print(session_id)


if __name__ == "__main__":
    main()
