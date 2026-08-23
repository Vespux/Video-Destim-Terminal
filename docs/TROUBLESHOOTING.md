# Troubleshooting

Start with the local host before troubleshooting Tailscale, DNS, or a reverse proxy.

## 1. Is the container running?

```bash
docker compose ps
```

A healthy install should show the `video-destim-terminal` service running and eventually `healthy`.

## 2. Read recent logs

```bash
docker compose logs --tail=100 video-destim-terminal
```

Follow live logs if needed:

```bash
docker compose logs -f video-destim-terminal
```

Press `Ctrl+C` to stop following logs; it does not stop the container.

## 3. Health check

```bash
curl http://127.0.0.1:8790/health
```

Expected shape:

```json
{"appVersion":"v1.30","ok":true,"youtubeConfigured":true}
```

## `youtubeConfigured` is false

Rerun the guided configuration helper:

```bash
bash setup.sh
```

Or confirm `.env` exists beside `compose.yaml` and contains your actual key:

```text
YOUTUBE_API_KEY=...
```

Then rebuild/recreate:

```bash
docker compose up -d --build
```

## Container immediately exits

The public build requires `OVERRIDE_PIN` to be exactly four digits.

Run `bash setup.sh` to enter a valid PIN, or check `.env` and logs manually. The placeholder in `.env.example` is intentionally invalid until you choose a PIN.

## Permission denied when running Docker

If Docker was just installed and your user was added to the `docker` group, log out and back in before retrying. If the group was never added, follow the Docker-user step in [Installation](INSTALL.md#5-allow-your-normal-user-to-run-docker).

## Port 8790 is already in use

Check what is listening:

```bash
sudo ss -ltnp | grep ':8790'
```

You can stop the conflicting service or change `VIDEO_DESTIM_PORT` in `.env`, then rebuild/recreate.

If you change the VDT port, also update Tailscale Serve/reverse-proxy configuration accordingly.

## Creator cannot be added

Check:

- YouTube Data API v3 is enabled in the key's Google Cloud project.
- The key is restricted to YouTube Data API v3, not an unrelated API.
- Any application restriction is compatible with server-side requests from your host.
- The link is a supported `@handle`, `/channel/`, or legacy `/user/` URL.
- Container logs for the upstream API error.

## YouTube API reports quota exceeded

VDT does not automatically buy additional API quota. If Google reports that the applicable quota is exhausted, API-backed creator refreshes can fail until the quota resets or the project receives additional quota.

See [YouTube API Quota & Usage](YOUTUBE-API-SETUP.md#youtube-api-quota--usage) for VDT's endpoint costs, expected normal usage, reset timing, and where to inspect your project quota.

## Creator list seems stale

Use `REFRESH CREATOR` from that creator's video list.

To clear all cached creator-video lists:

```text
flush-cache
```

The command asks for confirmation before clearing cache.

## No eligible videos found

VDT intentionally excludes:

- videos 3:00 or shorter;
- live/upcoming/live-origin items.

It also scans only a bounded number of uploads-playlist pages. `MAX_PLAYLIST_PAGES` defaults to 4. A creator with many excluded recent uploads may therefore have no eligible item inside the scan window.

## Requests are locked

If `BLOCK CONSECUTIVE WATCHES?` is enabled, confirmed requests start the configured cooldown.

You can wait for the cooldown, change the Config setting, or use `MANUAL OVERRIDE` with the four-digit cooldown PIN.

The PIN is not a login credential.

## Remote/Tailscale URL does not work, but local health does

If the local health check succeeds, VDT itself is listening. Check `tailscale status` / `tailscale serve status` or your reverse-proxy/access-control layer, then follow [Networking & HTTPS](NETWORKING.md) for the authoritative access setup.

## Browser still shows an old favicon/UI after updating

VDT sends the main page with no-cache headers and versioned icon URLs, but mobile browsers can still cache favicons aggressively.

Try a normal refresh first. If the old icon persists, close/reopen the tab or clear site data/cache for that VDT hostname.

## Emoji are still visually different from the terminal font

Creator-provided emoji text is preserved. VDT applies a display-only grayscale/green treatment, but Android/browser emoji engines may still use their own emoji glyph shapes. The project intentionally does not delete or replace emoji characters from creator titles.

## Update failed halfway through

The documented release-ZIP update chain uses `&&`, so later dependent steps stop after a failure.

Inspect which step failed, then use the one-command-at-a-time instructions in [UPDATING.md](UPDATING.md). The previous release folder is intentionally left available for rollback.

## Database backup/restore questions

See [BACKUP-RESTORE.md](BACKUP-RESTORE.md). Stop the container before making a simple filesystem copy of the SQLite data.
