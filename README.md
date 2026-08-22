# Video Destim Terminal

**Video Destim Terminal (VDT)** is a deliberately low-stimulation, self-hosted interface for choosing videos from your own curated list of YouTube creators and then handing playback off to YouTube.

VDT is a tool that allows users a more intentional way of selecting videos to watch. It also has the option of self-imposed video consumption limits by implementing Watch Credits and Cooldowns, which can be configured in a variety of ways. These can also be disabled if you only are only here for the terminal interface.

If you feel it's time we ditch the endless scrolling, attention-economy based, engagement-based & algorithmicly fed slop and slow down a bit, VDT is probably for you. 

You choose which creators are available, VDT shows a compact text-first list of eligible recent uploads, and a confirmed request opens the normal YouTube watch URL in whatever browser/player you use. (We certainly have some recommendations for this that align with the goal of VDT!)

> **Initial public GitHub release: v1.30**
>
> Video Destim Terminal is an independent project. It is not affiliated with, sponsored by, or endorsed by YouTube, Google, ReVanced, Mozilla, NewPipe, PipePipe, SponsorBlock, uBlock Origin, Unhook, or Tailscale.

## What VDT does

- Maintains a user-curated creator list.
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
- self-hosting so *your* data stays with you

## Self-hosted by design

There is no VDT cloud account and no central VDT database. Each installation runs independently.

Your instance stores its configuration, creator list, credit state, request history, watched state, cached public metadata, and stats in a local SQLite database under `data/`. Your `.env` file contains the YouTube API key and override PIN. Those files are not shared.

(IMPORTANT: Please ensure YOU do NOT share your YouTube API key once it is created.)

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

VDT will prompt you for:

```text
ENTER YOUTUBE API KEY:
CHOOSE OVERRIDE PIN:
```

The API key and PIN are hidden while you enter them. The setup helper requires a non-empty API key, validates that the override PIN is exactly four digits, writes both values to `.env`, and protects the file with `chmod 600`. It does **not** start Docker automatically.

If `.env` already exists, the helper asks before updating the stored API key and PIN instead of silently overwriting them.

Prefer to configure it manually? Copy `.env.example` to `.env`, set `YOUTUBE_API_KEY` and a four-digit `OVERRIDE_PIN`, then run `chmod 600 .env`. The complete [Installation guide](docs/INSTALL.md) includes both methods.

Start VDT:

```bash
docker compose up -d --build
```

Check health:

```bash
curl http://127.0.0.1:8790/health
```

Expected result:

```json
{"appVersion":"v1.30","ok":true,"youtubeConfigured":true}
```

The default Compose configuration binds VDT to `127.0.0.1:8790`. That is intentional. See [Networking & HTTPS](docs/NETWORKING.md) before using it from another device.

Starting from blank Ubuntu? Use the complete [Installation guide](docs/INSTALL.md).

## First use

On the first browser/device launch, VDT shows a legal/privacy acknowledgement. After accepting:

1. Open `CONFIG`.
2. Review the credit/cooldown defaults.
3. Open `AVAILABLE CREATORS` and add one or more YouTube creators.
4. Return home and choose `REQUEST A WATCH`.
5. Select a creator, then an eligible video, then confirm the request.

VDT returns you to the creator's video list and hands the confirmed URL to your device for playback.

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

## Updating

The update guide includes both formats requested for public use:

1. a **single copy/paste command chain** for normal SSH/terminal use; and
2. the **same process one command at a time** for mobile or limited SSH clients.

Both preserve `.env` and `data/`, stop the old container before copying live SQLite data, leave the previous release folder intact for rollback, rebuild the new release, and finish with a health check.

See [Updating](docs/UPDATING.md).

## Optional playback environments

VDT itself only opens a normal YouTube watch URL. The amount of stimulation you see **after** that handoff depends on the playback environment selected on your device. 

It is recommended to use one of the suggested [Playback Options](docs/PLAYBACK-OPTIONS.md) covered in the guide. (currently ReVanced, Firefox with Unhook/uBlock Origin/SponsorBlock/PiP Fix, PipePipe, and NewPipe)

## Security model

VDT does **not** contain a login system. 

For that reason:

- the service binds to localhost by default;
- you should not directly expose port `8790` to the public internet;
- remote access should use a private network/VPN such as Tailscale Serve or a reverse proxy with real authentication/access control;
- `.env`, the SQLite database, exports, and backups should be treated as private files.

See [SECURITY.md](SECURITY.md).

## YouTube API / policy note

This project uses YouTube API Services, and YouTube's API terms/policies can change independently of VDT. The project includes privacy/terms/data controls and best-effort refresh of stored public API metadata before 30 days, but **the project does not claim legal advice, policy certification, or YouTube approval**.

See [COMPLIANCE.md](COMPLIANCE.md) before publishing a modified build or operating VDT beyond personal self-hosting.

## Documentation & Guides

| Guide | Purpose |
|---|---|
| [Installation](docs/INSTALL.md) | Existing-Docker and blank-Ubuntu setup paths |
| [YouTube API setup](docs/YOUTUBE-API-SETUP.md) | Create/restrict your own API key |
| [Networking & HTTPS](docs/NETWORKING.md) | Localhost, Tailscale Serve, reverse proxies |
| [Configuration](docs/CONFIGURATION.md) | Every VDT setting and save behavior |
| [Terminal Commands](docs/COMMANDS.md) | Main navigation and utility commands |
| [Playback Options](docs/PLAYBACK-OPTIONS.md) | Optional low-stimulation playback environments |
| [Backup & Restore](docs/BACKUP-RESTORE.md) | Protect/restore `.env` and local data |
| [Updating](docs/UPDATING.md) | Safe release upgrades and rollback |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Health, logs, API, networking, cache issues |
| [Architecture](docs/ARCHITECTURE.md) | Data flow, components, storage, network calls |
| [FAQ](docs/FAQ.md) | Common behavior/self-hosting questions |
| [GitHub Publishing](docs/MAINTAINER-GITHUB-WORKFLOW.md) | Maintainer first-release/future-release workflow |
| [API & Distribution Notes](COMPLIANCE.md) | Current YouTube API policy review points |

## Privacy and data controls

The running application provides an always-available `LEGAL` screen and first-run acknowledgement. Packaged notices are also served at:

- `/privacy`
- `/terms`

`export-data` creates a local JSON export without the API key or override PIN. `delete-data` permanently resets the local VDT database after confirmation; it does not delete data held by YouTube or third-party playback apps.

## Support

The in-app `SUPPORT` link and `support` command ask for confirmation before opening the creator's tip jar:

https://ko-fi.com/vespux

## License

MIT. See [LICENSE](LICENSE).

Vibe-coded by Vespux, 2026.
