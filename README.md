# Video Destim Terminal

**Video Destim Terminal (VDT)** is a deliberately low-stimulation, self-hosted interface for choosing videos from your own curated list of YouTube creators and then handing playback off to YouTube.

VDT is a tool that allows users a more intentional way of selecting videos to watch. It also has the option of self-imposed video consumption limits by implementing Watch Credits and Cooldowns, which can be configured in a variety of ways. These can also be disabled if you only are only here for the terminal interface.

Eager to get started? Jump to [Install](docs/INSTALL.md)

If you feel it's time we ditch the endless scrolling, attention-economy based, engagement-based & algorithmically fed slop and slow down a bit, VDT is probably for you.

You choose which creators are available, VDT shows a compact text-first list of eligible recent uploads, and a confirmed request opens the normal YouTube watch URL in whatever browser/player you use. (We certainly have some recommendations for this that align with the goal of VDT!)

> **Current release: v1.31 · Initial public GitHub release: v1.30**
>
> Video Destim Terminal is an independent project. It is not affiliated with, sponsored by, or endorsed by YouTube, Google, ReVanced, Mozilla, NewPipe, PipePipe, SponsorBlock, uBlock Origin, Unhook, or Tailscale.

## What VDT does

- Maintains a user-curated creator list.
- Lets you save videos with a star and browse them later in one aggregated Saved Videos list.
- Retrieves public channel/video metadata with the YouTube Data API v3.
- Shows up to 20 recent eligible uploads per creator in a text-first terminal interface.
- Excludes videos **3:00 or shorter** and excludes live/upcoming/live-origin items.
- Supports configurable watch credits, allowance intervals, rollover, cooldowns, manual override, and rewatch-cost behavior.
- Tracks local VDT request history and local request-behavior stats.
- Marks locally requested videos as watched and can make rewatches free or credit-costing.
- Supports creator reordering and per-list video sorting.
- Optionally normalizes unnecessary ALL-CAPS title words; this is **off by default**.
- Preserves creator-provided emoji text while applying a display-only terminal-style tint to emoji glyphs where the browser allows it.
- Launches the selected standard `youtube.com/watch` URL after confirmation.
- Keeps the YouTube API key on the server; it is not intentionally sent to the browser.

VDT does **not** host, proxy, download, transcode, or embed audiovisual content.

## Design goals

VDT is intentionally narrow in scope, while offering intuitive controls across devices and input methods. The project favors:

- intentional video selection over discovery feeds;
- text over thumbnails/cards;
- a small creator list over broad browsing;
- visible, reversible local controls;
- self-hosting so *your* data stays with you.

## Self-hosted by design

There is no VDT cloud account and no central VDT database. Each installation runs independently.

Your instance stores its configuration, creator list, saved videos, credit state, request history, watched state, cached public metadata, and stats in a local SQLite database under `data/`. Your `.env` file contains the YouTube API key and override PIN. Those files are not shared.

**Do not share or publish your YouTube API key, `.env`, database, exports, or backups.**

## Requirements

- A Linux machine capable of running Docker Engine and Docker Compose.
- A YouTube Data API v3 key created by the person operating the instance.
- For access from another device: a secure access layer. **Tailscale Serve** is the documented private-access option; an authenticated HTTPS reverse proxy also works.

The initial public release was clean-install tested on **Ubuntu Server 26.04 LTS**, Docker Engine **29.7.2**, and Docker Compose **v5.5.0**. Those exact versions are not hard requirements.

## Quick start — Docker already installed

Download/clone the project, enter its directory, then run the guided setup:

```bash
bash setup.sh
```

VDT prompts for your YouTube API key and a four-digit override PIN, writes them to `.env`, and protects that file. Manual `.env` setup remains available if you prefer it.

Then start VDT:

```bash
docker compose up -d --build
```

Check health:

```bash
curl http://127.0.0.1:8790/health
```

Expected result:

```json
{"appVersion":"v1.30.1","ok":true,"youtubeConfigured":true}
```

The default Compose configuration binds VDT to `127.0.0.1:8790`. That is intentional. See the complete [Installation guide](docs/INSTALL.md) and [Networking & HTTPS](docs/NETWORKING.md) guide before using VDT from another device.

## First use

On the first browser/device launch, VDT shows a legal/privacy acknowledgement. After accepting:

1. Open `CONFIG` and review the defaults.
2. Open `AVAILABLE CREATORS` and add one or more YouTube creators.
3. Return home and choose `REQUEST A WATCH`.
4. Select a creator, then an eligible video, then confirm the request.

VDT hands the confirmed URL to your device for playback. See [Configuration](docs/CONFIGURATION.md) for the complete settings reference.

## Home screen and commands

The home screen exposes:

```text
[1] REQUEST A WATCH
[2] CONFIG
[3] STATS
[4] COMMAND DOC
```

The same primary screens can be opened from the terminal prompt with:

```text
request-watch
config
stats
command-doc
```

`COMMAND DOC` also exposes clickable utility commands such as `history`, `diag`, `flush-cache`, `export-data`, `support`, `legal`, `delete-data`, and `credit-eject`.

See [Terminal Commands](docs/COMMANDS.md) for details.

## Default behavior

| Setting | Default |
|---|---|
| Credit allowance interval | Weekly |
| Weekly reset day | Monday |
| Credit allowance | 3 |
| Unused-credit rollover | No |
| Block consecutive watches | Yes |
| Request cooldown | 1 hour |
| Default video sort | Upload date |
| Watched videos cost credits | No |
| Normalize video title caps | No |

See [Configuration](docs/CONFIGURATION.md) for the full behavior, including unsaved-change protection and creator reordering.

## YouTube API quota

VDT uses low-cost YouTube Data API methods and does **not** use the separately limited `search.list` endpoint. A typical fresh creator refresh costs about **2 quota units**, while the current bounded four-page scan can use up to about **8 units**. Google currently provides a default **10,000-unit daily bucket** for the API methods VDT uses, so normal personal use is unlikely to approach the limit.

Quota is a usage limit, **not a pay-as-you-go meter**: exhausting the applicable quota does not automatically begin billing for extra VDT requests. See [YouTube API Setup — Quota & Usage](docs/YOUTUBE-API-SETUP.md#youtube-api-quota--usage) for the full explanation, current endpoint costs, caching behavior, reset timing, and where to check your own usage.

## Updating

VDT's update guide provides both a single copy/paste command chain and the same process one command at a time for mobile/limited SSH clients. The documented release-ZIP workflow preserves `.env` and `data/`, keeps the previous release available for rollback, and finishes with a health check.

See [Updating](docs/UPDATING.md).

## Optional playback environments

VDT only opens a normal YouTube watch URL. What you see after that handoff depends on the browser/player on your device.

See [Playback Options](docs/PLAYBACK-OPTIONS.md) for optional environments that better align with VDT's low-stimulation goal, including ReVanced, Firefox with selected extensions, PipePipe, and NewPipe.

## Security model

VDT does **not** contain a login system, and the override PIN is not authentication. The service therefore binds to localhost by default and should not be exposed directly to the public internet.

For private remote access and the full threat model, see [Networking & HTTPS](docs/NETWORKING.md) and [SECURITY.md](SECURITY.md).

## YouTube API / policy note

This project uses YouTube API Services, and YouTube's API terms/policies can change independently of VDT. The project includes privacy/terms/data controls and best-effort refresh of stored public API metadata before 30 days, but **the project does not claim legal advice, policy certification, or YouTube approval**.

See [COMPLIANCE.md](COMPLIANCE.md) before publishing a modified build or operating VDT beyond personal self-hosting.

## Documentation & Guides

| Guide | Purpose |
|---|---|
| [Installation](docs/INSTALL.md) | Existing-Docker and blank-Ubuntu setup paths |
| [YouTube API setup](docs/YOUTUBE-API-SETUP.md) | Create/restrict your API key and understand quota usage |
| [Networking & HTTPS](docs/NETWORKING.md) | Localhost, Tailscale Serve, reverse proxies |
| [Configuration](docs/CONFIGURATION.md) | Every VDT setting and save behavior |
| [Terminal Commands](docs/COMMANDS.md) | Main navigation and utility commands |
| [Playback Options](docs/PLAYBACK-OPTIONS.md) | Optional low-stimulation playback environments |
| [Backup & Restore](docs/BACKUP-RESTORE.md) | Protect/restore `.env` and local data |
| [Updating](docs/UPDATING.md) | Safe release upgrades and rollback |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Health, logs, API, networking, cache issues |
| [Architecture](docs/ARCHITECTURE.md) | Data flow, components, storage, network calls |
| [FAQ](docs/FAQ.md) | Common behavior/self-hosting questions |
| [API & Distribution Notes](COMPLIANCE.md) | Current YouTube API policy review points |

## Privacy and data controls

The running application provides an always-available `LEGAL` screen and first-run acknowledgement. Packaged notices are also served at `/privacy` and `/terms`.

`export-data` creates a local JSON export without the API key or override PIN. `delete-data` permanently resets the local VDT database after confirmation; it does not delete data held by YouTube or third-party playback apps.

See [PRIVACY.md](PRIVACY.md) for the full data-handling notice.

## Support

The in-app `SUPPORT` link and `support` command ask for confirmation before opening the creator's tip jar:

https://ko-fi.com/vespux

## License

MIT. See [LICENSE](LICENSE).

Vibe-coded by Vespux, 2026.
