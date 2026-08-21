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

VDT uses browser storage for small interface state, including:

- first-run legal acknowledgement;
- return-screen state used when handing playback off to another app/site;
- legacy migration input for older pre-database builds if present.

The authoritative current instance state is the server-side SQLite database.

## YouTube API request pattern

VDT uses:

- channel resolution/metadata;
- channel uploads playlists;
- `playlistItems` to enumerate recent uploads;
- batched `videos` metadata requests.

The creator list is cached for a short configurable TTL. Stored resource metadata used by local history/creator records is refreshed on a best-effort schedule before 30 days.

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

## External network destinations in the unmodified build

Normal operation can contact:

- `www.googleapis.com` — YouTube Data API v3, from the server;
- `fonts.googleapis.com` / `fonts.gstatic.com` — VT323 web font, from the browser;
- `youtube.com` — after a user confirms a watch request or opens YouTube legal links;
- `policies.google.com` — only if the user opens the Google Privacy Policy link;
- `ko-fi.com` — only after the user chooses SUPPORT and confirms opening the tip jar.

Optional playback tools and Tailscale have their own independent network behavior.

## Security boundaries

VDT assumes the person who can reach the web interface is trusted to operate the instance. There is no per-user login, CSRF token system, or multi-user permissions model.

That is why the default network binding is localhost and the documentation recommends private-network or authenticated-proxy access rather than public exposure.
