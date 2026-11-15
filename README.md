# aiostreams-art

Self-updating folder covers for Romulo's AIOStreams / AIOMetadata collections.

Each cover is rebuilt from whatever title is currently #1 in that folder (official backdrop art from the folder's own catalogs, via AIOMetadata), with the folder name set in Montserrat. No AI-generated imagery.

- `covers.json`: one entry per folder: output file, title, subtitle, and the catalogs to pick from (in priority order).
- `make_covers.py`: renders `covers/<file>` and records each pick in `covers/state.json`. A folder skips titles already used by another folder in the same run, and keeps its previous cover if nothing usable comes back.
- `update.sh`: regenerate, then commit and push only if something changed. Meant to run on a schedule.

Stable image URLs (what AIOMetadata points at):
`https://raw.githubusercontent.com/Romulo-Souza12/aiostreams-art/main/covers/<file>`

Fonts: Montserrat (SIL Open Font License, `fonts/OFL.txt`).
