# aiostreams-art

Self-updating cover art for my AIOStreams / AIOMetadata collections.

Each folder cover is rebuilt from whatever title is currently #1 in that folder (official backdrop art from the folder's own catalogs, via AIOMetadata), with the folder name set in Montserrat. No AI-generated imagery.

## What's here

- `covers/`: folder covers, plus a hero backdrop per streaming service in `covers/heroes/`.
- `logos/`: streaming service logos, rendered from Wikimedia Commons.
- `covers.json`: one entry per folder: output file, title, subtitle, and the catalogs to pick from (in priority order).
- `make_covers.py`: renders `covers/<file>` and records each pick in `covers/state.json`. A folder skips titles already used by another folder in the same run, and keeps its previous cover if nothing usable comes back.
- `update.sh`: regenerates the covers, then commits and pushes only if something changed. Runs on a daily schedule.
- `addons/toonami/`: a small static addon with the Toonami Aftermath live channels.

## Links

Every image keeps one fixed link; only the picture behind it changes:
`https://raw.githubusercontent.com/Romulo-Souza12/aiostreams-art/main/covers/<file>`

Fonts: Montserrat (SIL Open Font License, `fonts/OFL.txt`).
