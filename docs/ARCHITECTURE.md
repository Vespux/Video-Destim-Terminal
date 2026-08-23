# Architecture

VDT is intentionally small: a browser UI, a Flask backend, a local SQLite database, and server-side requests to the YouTube Data API v3.

## High-level flow

```text
Browser / phone
      |
      | HTTPS via Tailscale Serve or authenticated reverse proxy
      | (or localhost HTTP on the host itself)
      v
Video Destim Terminal Flask app
      |
      +--> local SQLite database: ./data/video-destim-terminal.db
      |
      +--> YouTube Data API v3 (server-side API key)
      |
      +--> confirmed request returns a normal youtube.com/watch URL

Browser/device then opens that watch URL in the selected browser/player.
```

VDT does not proxy the video stream and does not embed a YouTube player.

## Container layout

Docker Compose maps:

```text
host ./data  ->  container /app/data
```

The Flask/Gunicorn service listens on container port `8000`. Compose maps that to the host using:

```text
${VIDEO_DESTIM_BIND:-127.0.0.1}:${VIDEO_DESTIM_PORT:-8790}:8000
```

The public default therefore exposes only `127.0.0.1:8790` on the Docker host.

## Server-side secrets

`.env` provides:

- `YOUTUBE_API_KEY`
- `OVERRIDE_PIN`
- optional cache/playlist/network tuning values

The YouTube API key is consumed by Python `requests` calls in `app.py`; it is not intentionally placed in browser state or VDT JSON exports.

The override PIN is compared by the backend for cooldown overrides. It is not authentication.

## Local database

VDT stores:

- Config/settings;
- current credit state/reset anchor;
- creator list/order and public channel metadata;
- short-lived creator video-list cache;
- watched/request state;
- confirmed request events;
- stats tracking start time;
- timestamps used for API-metadata refresh housekeeping.

The database is local to each instance.

## Browser-side storage

Browser storage is limited to small interface/migration state; the authoritative current instance state is the server-side SQLite database. See [PRIVACY.md](../PRIVACY.md) for the complete browser-storage disclosure.

## YouTube API request pattern

VDT uses:

- channel resolution/metadata;
- channel uploads playlists;
- `playlistItems` to enumerate recent uploads;
- batched `videos` metadata requests.

Creator video lists use a short configurable cache, and stored API metadata has separate best-effort refresh housekeeping. See [YouTube API Setup](YOUTUBE-API-SETUP.md#youtube-api-quota--usage) for quota/caching details and [COMPLIANCE.md](../COMPLIANCE.md) for the metadata-retention policy notes.

## Video eligibility

The backend excludes items at or below 180 seconds and items identified as current/upcoming/live-origin content, then returns up to 20 eligible videos.

The browser can sort that eligible set by upload date, name, or length.

## Confirmed watch request

When the user confirms a video:

1. the backend validates credit/cooldown state;
2. the request event is recorded locally;
3. credit/watched/cooldown state is updated;
4. the backend returns the standard YouTube watch URL;
5. the browser navigates to that URL.

No audiovisual content passes through the VDT backend.

## External network destinations

The architecture makes server-side YouTube API requests and browser-side requests/navigation for the terminal font, confirmed YouTube handoff, legal links, and optional SUPPORT action. The complete destination-by-destination disclosure lives in [PRIVACY.md](../PRIVACY.md#network-requests-made-by-the-unmodified-interface).

## Security boundaries

VDT assumes the person who can reach the web interface is trusted to operate the instance; there is no per-user login or permissions model. See [SECURITY.md](../SECURITY.md) for the threat model and [Networking & HTTPS](NETWORKING.md) for access procedures.
