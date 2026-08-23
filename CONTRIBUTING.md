# Contributing

Contributions are welcome if they preserve the project's intentionally narrow, low-stimulation goal.

## Project principles

Changes should generally preserve:

- text-first, low-stimulation presentation;
- no thumbnail/feed wall inside VDT;
- no VDT telemetry, ads, or external analytics;
- self-hosted/local data ownership;
- server-side handling of the YouTube API key;
- safe localhost network defaults;
- touch/mouse usability plus visible keyboard/command controls where practical;
- explicit confirmation for destructive actions.

## Before opening a pull request

1. Do not commit real API keys, `.env`, SQLite databases, exports, backups, private hostnames, or personal watch history.
2. Review `COMPLIANCE.md` when changing YouTube API usage, stored API data, stats/metrics, playback handoff, metadata display, branding, or legal/privacy behavior.
3. Update user-facing docs when behavior changes.
4. Update `CHANGELOG.md` for release-bound changes.
5. Preserve existing unsaved-change safeguards when adding navigation paths inside/out of Config/Reorder workflows.

## Local validation

Compile the Python backend:

```bash
python -m py_compile app.py
```

Build/start the container:

```bash
docker compose up -d --build
```

Check:

```bash
docker compose ps
curl http://127.0.0.1:8790/health
```

Then exercise the changed UI in a browser. For navigation changes, test both clicks/taps and terminal text commands. For Config/Reorder changes, explicitly test leaving with unsaved changes.

If Node.js is available, also syntax-check the inline JavaScript after extracting the `<script>` contents into a temporary `.js` file.

## Documentation style

- Prefer copy/pasteable commands.
- When an SSH workflow is lengthy, provide both an all-at-once block and one-command-at-a-time alternative where useful.
- Do not include private example IPs, hostnames, API keys, or personal paths in public docs.
- Link to authoritative upstream documentation for Docker, Tailscale, and YouTube API policy rather than freezing unnecessary third-party details in this repository.
- Give each topic one authoritative VDT guide. Elsewhere, repeat only the conclusion/context a reader needs and link to the canonical procedure instead of copying the full instructions.

## UI style

VDT intentionally avoids thumbnails, cards, feeds, and decorative modern-app UI. New features should feel like they belong in the terminal rather than turning the project into another content portal.
