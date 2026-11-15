#!/usr/bin/env bash
# Regenerate covers and push them if anything changed. Safe to run on a schedule.
set -euo pipefail
cd "$(dirname "$0")"
export HOME=/opt/data/profiles/jeongyeon/home
git pull -q --rebase origin main || true
python3 -I make_covers.py
if [[ -n "$(git status --porcelain covers)" ]]; then
  git add covers
  git -c user.name="Jeongyeon" -c user.email="Romulo-Souza12@users.noreply.github.com" \
    commit -q -m "Refresh covers $(date -u +%Y-%m-%d)"
  git push -q origin HEAD:main
  echo "pushed"
else
  echo "no changes"
fi
