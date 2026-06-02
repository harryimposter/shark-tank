#!/usr/bin/env bash
# Market Map — double-click (or ./run.sh) to trigger Claude Code to build today's brief.
#
# This does not call any market API. It mints a session id via main.py, then asks
# the Claude Code CLI to do the web searches and write output.html per PROMPT.md.

set -uo pipefail
cd "$(dirname "$0")"

# 1) Mint a session id (try whatever Python is available; non-fatal if absent).
SESSION_ID=""
for PY in python python3 py; do
  if command -v "$PY" >/dev/null 2>&1; then
    SESSION_ID="$("$PY" main.py 2>/dev/null | tail -n 1)"
    break
  fi
done
[ -n "$SESSION_ID" ] && echo "Session: $SESSION_ID"

# 2) The trigger prompt for Claude Code.
read -r -d '' PROMPT <<EOF || true
Run the Market Map for $(date +%F) (session ${SESSION_ID:-n/a}).
Do all the web searches yourself (>=16, allowlist in sources.py). Follow the full
system prompt and 18-section spec in PROMPT.md: voice rules, the 5-layer wrap, the
correlation breaks panel, vol/skew, positioning, funding/plumbing, and trade cards
with the conviction rubric. Mark the trades.json book to market and grade
yesterday's calls, render the four inline-SVG charts via charts.py, assemble the
page with book.build_html, write the complete self-contained brief to output.html,
and persist trades.json and regime_log.json.
EOF

# 3) Fire it, or print it if the CLI isn't installed.
if command -v claude >/dev/null 2>&1; then
  echo "Triggering Claude Code..."
  claude "$PROMPT"
else
  echo
  echo "Claude Code CLI ('claude') not found on PATH."
  echo "Open Claude Code in this folder and paste this:"
  echo "------------------------------------------------------------"
  echo "$PROMPT"
  echo "------------------------------------------------------------"
fi

# 4) Open the result if it was produced.
if [ -f output.html ]; then
  if command -v start    >/dev/null 2>&1; then start output.html
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open output.html
  elif command -v open     >/dev/null 2>&1; then open output.html
  fi
fi
