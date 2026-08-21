import json
import os
import re
import sqlite3
import time
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests
from flask import Flask, Response, jsonify, request, send_from_directory

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", APP_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "video-destim-terminal.db"
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
OVERRIDE_PIN = os.environ.get("OVERRIDE_PIN", "").strip()
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "900"))
MAX_PLAYLIST_PAGES = int(os.environ.get("MAX_PLAYLIST_PAGES", "4"))
MIN_VIDEO_SECONDS = 181
API_DATA_MAX_AGE_SECONDS = 29 * 24 * 60 * 60
API_REFRESH_CHECK_INTERVAL_SECONDS = 6 * 60 * 60
APP_VERSION = "v1.30"

if not re.fullmatch(r"\d{4}", OVERRIDE_PIN):
    raise RuntimeError("OVERRIDE_PIN MUST BE SET TO EXACTLY 4 DIGITS IN .env")

app = Flask(__name__, static_folder=None)

DEFAULT_SETTINGS = {
    "interval": "weekly",
    "amount": 3,
    "weekDay": 1,  # JS-style: Sunday=0, Monday=1 ...
    "rollover": False,
    "block": True,
    "cdH": 1,
    "cdM": 0,
    "sort": "upload",
    "repeatCosts": False,
    "normalizeCaps": False,
    "timezone": "UTC",
}


class APIError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


@app.errorhandler(APIError)
def handle_api_error(err):
    return jsonify({"error": err.message}), err.status


@app.errorhandler(Exception)
def handle_unexpected(err):
    app.logger.exception("Unhandled error")
    return jsonify({"error": "SERVER ERROR. CHECK CONTAINER LOGS."}), 500


def db():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with db() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS creators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                uploads_playlist TEXT,
                position INTEGER NOT NULL DEFAULT 0,
                added_at REAL NOT NULL DEFAULT 0,
                metadata_refreshed_at REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS watched (
                video_id TEXT PRIMARY KEY,
                watched_at REAL NOT NULL,
                watch_count INTEGER NOT NULL DEFAULT 1,
                metadata_refreshed_at REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS video_cache (
                creator_id INTEGER PRIMARY KEY,
                fetched_at REAL NOT NULL,
                payload TEXT NOT NULL,
                FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS watch_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requested_at REAL NOT NULL,
                creator_id INTEGER,
                creator_name TEXT NOT NULL,
                video_id TEXT NOT NULL,
                video_title TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL DEFAULT 0,
                credit_cost INTEGER NOT NULL DEFAULT 0,
                was_rewatch INTEGER NOT NULL DEFAULT 0,
                override_used INTEGER NOT NULL DEFAULT 0,
                metadata_refreshed_at REAL NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_watch_events_requested_at
                ON watch_events(requested_at);
            CREATE INDEX IF NOT EXISTS idx_watch_events_creator_name
                ON watch_events(creator_name);
            """
        )
        if meta_get(con, "settings") is None:
            meta_set(con, "settings", json.dumps(DEFAULT_SETTINGS))
        if meta_get(con, "credits") is None:
            meta_set(con, "credits", str(DEFAULT_SETTINGS["amount"]))
        if meta_get(con, "anchor") is None:
            meta_set(con, "anchor", "")
        if meta_get(con, "cooldown_until") is None:
            meta_set(con, "cooldown_until", "0")
        if meta_get(con, "initialized") is None:
            meta_set(con, "initialized", "0")
        if meta_get(con, "stats_started_at") is None:
            meta_set(con, "stats_started_at", str(time.time()))
        creator_columns = {row["name"] for row in con.execute("PRAGMA table_info(creators)").fetchall()}
        if "added_at" not in creator_columns:
            con.execute("ALTER TABLE creators ADD COLUMN added_at REAL NOT NULL DEFAULT 0")
        if "metadata_refreshed_at" not in creator_columns:
            con.execute("ALTER TABLE creators ADD COLUMN metadata_refreshed_at REAL NOT NULL DEFAULT 0")
        watched_columns = {row["name"] for row in con.execute("PRAGMA table_info(watched)").fetchall()}
        if "metadata_refreshed_at" not in watched_columns:
            con.execute("ALTER TABLE watched ADD COLUMN metadata_refreshed_at REAL NOT NULL DEFAULT 0")
        event_columns = {row["name"] for row in con.execute("PRAGMA table_info(watch_events)").fetchall()}
        if "metadata_refreshed_at" not in event_columns:
            con.execute("ALTER TABLE watch_events ADD COLUMN metadata_refreshed_at REAL NOT NULL DEFAULT 0")
        con.execute("UPDATE creators SET added_at=id WHERE added_at IS NULL OR added_at=0")


def meta_get(con, key):
    row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def meta_set(con, key, value):
    con.execute(
        "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


def load_settings(con):
    raw = meta_get(con, "settings")
    try:
        saved = json.loads(raw) if raw else {}
    except Exception:
        saved = {}
    return {**DEFAULT_SETTINGS, **saved}


def save_settings(con, settings):
    meta_set(con, "settings", json.dumps(settings, separators=(",", ":")))


def valid_timezone(name):
    try:
        ZoneInfo(name)
        return True
    except Exception:
        return False


def tz_for(settings):
    name = settings.get("timezone") or "UTC"
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("UTC")


def period_start(settings, now=None):
    tz = tz_for(settings)
    now = now or datetime.now(tz)
    d = now.replace(hour=0, minute=0, second=0, microsecond=0)
    interval = settings.get("interval")
    if interval == "daily":
        return d
    if interval == "weekly":
        js_day = (d.weekday() + 1) % 7
        target = int(settings.get("weekDay", 1)) % 7
        return d - timedelta(days=(js_day - target) % 7)
    if interval == "monthly":
        return d.replace(day=1)
    return d.replace(month=1, day=1)


def next_reset(settings, now=None):
    start = period_start(settings, now)
    interval = settings.get("interval")
    if interval == "daily":
        return start + timedelta(days=1)
    if interval == "weekly":
        return start + timedelta(days=7)
    if interval == "monthly":
        if start.month == 12:
            return start.replace(year=start.year + 1, month=1)
        return start.replace(month=start.month + 1)
    return start.replace(year=start.year + 1)


def apply_allowance_reset(con):
    settings = load_settings(con)
    start = period_start(settings)
    anchor_raw = meta_get(con, "anchor") or ""
    credits = int(float(meta_get(con, "credits") or 0))
    if not anchor_raw:
        meta_set(con, "anchor", start.isoformat())
        meta_set(con, "credits", settings["amount"])
        return settings, int(settings["amount"])
    try:
        anchor = datetime.fromisoformat(anchor_raw)
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=tz_for(settings))
    except Exception:
        anchor = start
        meta_set(con, "anchor", start.isoformat())
    if anchor < start:
        amount = int(settings.get("amount", 0))
        credits = credits + amount if settings.get("rollover") else amount
        meta_set(con, "credits", credits)
        meta_set(con, "anchor", start.isoformat())
    return settings, credits


def cooldown_remaining_ms(con):
    try:
        until = float(meta_get(con, "cooldown_until") or 0)
    except Exception:
        until = 0
    return max(0, int((until - time.time()) * 1000))


def creator_rows(con):
    return con.execute(
        "SELECT id,channel_id,name,link,uploads_playlist,position,added_at FROM creators ORDER BY position,id"
    ).fetchall()


def creator_dict(row):
    return {
        "id": row["id"],
        "channelId": row["channel_id"],
        "name": row["name"],
        "link": row["link"],
        "addedAt": row["added_at"],
        "resolved": bool(row["channel_id"] and row["uploads_playlist"]),
    }


def state_payload(con):
    settings, credits = apply_allowance_reset(con)
    creators = [creator_dict(r) for r in creator_rows(con)]
    return {
        "settings": settings,
        "credits": credits,
        "creators": creators,
        "cooldownRemainingMs": cooldown_remaining_ms(con),
        "nextReset": next_reset(settings).isoformat(),
        "youtubeConfigured": bool(YOUTUBE_API_KEY),
        "needsMigration": meta_get(con, "initialized") != "1",
    }



def stats_tracking_started_at(con):
    try:
        return float(meta_get(con, "stats_started_at") or time.time())
    except Exception:
        return time.time()


def stats_payload(con, scope):
    settings, credits = apply_allowance_reset(con)
    tracking_started = stats_tracking_started_at(con)

    if scope == "period":
        period_start_dt = period_start(settings)
        period_end_dt = next_reset(settings)
        query_start = max(period_start_dt.timestamp(), tracking_started)
    else:
        scope = "all"
        period_start_dt = None
        period_end_dt = None
        query_start = tracking_started

    rows = con.execute(
        """
        SELECT requested_at,creator_name,video_id,video_title,duration_seconds,
               credit_cost,was_rewatch,override_used
        FROM watch_events
        WHERE requested_at >= ?
        ORDER BY requested_at ASC, id ASC
        """,
        (query_start,),
    ).fetchall()

    request_count = len(rows)
    credits_spent = sum(int(r["credit_cost"] or 0) for r in rows)
    video_seconds = sum(max(0, int(r["duration_seconds"] or 0)) for r in rows)
    rewatches = sum(1 for r in rows if int(r["was_rewatch"] or 0))
    manual_overrides = sum(1 for r in rows if int(r["override_used"] or 0))

    avg_video_seconds = round(video_seconds / request_count) if request_count else None

    avg_gap_seconds = None
    if request_count >= 2:
        timestamps = [float(r["requested_at"]) for r in rows]
        gaps = [
            max(0, timestamps[i] - timestamps[i - 1])
            for i in range(1, len(timestamps))
        ]
        avg_gap_seconds = round(sum(gaps) / len(gaps)) if gaps else None

    creator_counts = Counter(
        str(r["creator_name"]).strip()
        for r in rows
        if str(r["creator_name"] or "").strip()
    )
    most_creator = None
    if creator_counts:
        name, count = sorted(
            creator_counts.items(),
            key=lambda item: (-item[1], item[0].casefold()),
        )[0]
        most_creator = {"name": name, "count": count}

    result = {
        "scope": scope,
        "trackingSince": datetime.fromtimestamp(
            tracking_started, tz=tz_for(settings)
        ).isoformat(),
        "watchRequests": request_count,
        "creditsSpent": credits_spent,
        "videoSeconds": video_seconds,
        "avgVideoSeconds": avg_video_seconds,
        "avgGapSeconds": avg_gap_seconds,
        "rewatches": rewatches,
        "manualOverrides": manual_overrides,
        "uniqueCreators": len(creator_counts),
        "mostWatchedCreator": most_creator,
    }

    if scope == "period":
        total_credit_pool = max(0, int(credits)) + max(0, credits_spent)
        allowance_used = (
            round((credits_spent / total_credit_pool) * 100)
            if total_credit_pool > 0
            else 0
        )
        result.update(
            {
                "creditsRemaining": int(credits),
                "allowanceUsedPct": allowance_used,
                "periodStart": period_start_dt.isoformat(),
                "periodEnd": period_end_dt.isoformat(),
            }
        )

    return result


def youtube_get(resource, params):
    if not YOUTUBE_API_KEY:
        raise APIError("YOUTUBE API KEY NOT CONFIGURED.", 503)
    url = f"https://www.googleapis.com/youtube/v3/{resource}"
    try:
        r = requests.get(
            url,
            params=params,
            headers={"X-Goog-Api-Key": YOUTUBE_API_KEY},
            timeout=15,
        )
    except requests.RequestException:
        raise APIError("YOUTUBE API REQUEST FAILED.", 502)
    if r.status_code >= 400:
        try:
            detail = r.json().get("error", {}).get("message", "YOUTUBE API ERROR")
        except Exception:
            detail = "YOUTUBE API ERROR"
        raise APIError(detail.upper(), 502)
    return r.json()



def _chunks(values, size=50):
    values = list(values)
    for i in range(0, len(values), size):
        yield values[i:i + size]


def refresh_stored_api_data(con, force=False):
    """Refresh non-authorized YouTube API metadata before it reaches 30 days old.

    This is a best-effort housekeeping pass for the public self-hosted build. It
    batches channel/video refreshes to keep quota use low and strips stale API
    metadata for resources that are no longer returned.
    """
    if not YOUTUBE_API_KEY:
        return {"checked": False, "reason": "api-key-not-configured"}

    now = time.time()
    try:
        last_check = float(meta_get(con, "api_data_refresh_checked_at") or 0)
    except Exception:
        last_check = 0
    if not force and now - last_check < API_REFRESH_CHECK_INTERVAL_SECONDS:
        return {"checked": False, "reason": "recently-checked"}

    stale_before = now - API_DATA_MAX_AGE_SECONDS

    # Refresh saved creator metadata in channel-ID batches.
    stale_creators = con.execute(
        """
        SELECT id,channel_id FROM creators
        WHERE channel_id IS NOT NULL AND channel_id != ''
          AND metadata_refreshed_at < ?
        """,
        (stale_before,),
    ).fetchall()
    for batch in _chunks(stale_creators, 50):
        ids = [str(r["channel_id"]) for r in batch]
        data = youtube_get(
            "channels",
            {"part": "snippet,contentDetails", "id": ",".join(ids), "maxResults": 50},
        )
        found = {str(item.get("id")): item for item in (data.get("items") or [])}
        for row in batch:
            cid = str(row["channel_id"])
            item = found.get(cid)
            if not item:
                # Keep the operator's original link but discard stale API metadata.
                con.execute(
                    """
                    UPDATE creators
                    SET channel_id=NULL,name='UNAVAILABLE CREATOR',uploads_playlist=NULL,
                        metadata_refreshed_at=?
                    WHERE id=?
                    """,
                    (now, row["id"]),
                )
                con.execute("DELETE FROM video_cache WHERE creator_id=?", (row["id"],))
                continue
            uploads = (
                item.get("contentDetails", {})
                .get("relatedPlaylists", {})
                .get("uploads")
            )
            name = item.get("snippet", {}).get("title") or "CREATOR"
            con.execute(
                """
                UPDATE creators
                SET name=?,uploads_playlist=?,metadata_refreshed_at=?
                WHERE id=?
                """,
                (name, uploads, now, row["id"]),
            )

    # Refresh video metadata referenced by local request/watched records.
    stale_event_rows = con.execute(
        """
        SELECT id,creator_id,video_id FROM watch_events
        WHERE video_id != '' AND metadata_refreshed_at < ?
        """,
        (stale_before,),
    ).fetchall()
    stale_watched_rows = con.execute(
        """
        SELECT video_id FROM watched
        WHERE metadata_refreshed_at < ?
        """,
        (stale_before,),
    ).fetchall()
    video_ids = sorted(
        {str(r["video_id"]) for r in stale_event_rows if r["video_id"]}
        | {str(r["video_id"]) for r in stale_watched_rows if r["video_id"]}
    )

    current_creator_names = {
        int(r["id"]): str(r["name"])
        for r in con.execute("SELECT id,name FROM creators").fetchall()
    }
    events_by_video = {}
    for row in stale_event_rows:
        events_by_video.setdefault(str(row["video_id"]), []).append(row)

    for batch_ids in _chunks(video_ids, 50):
        data = youtube_get(
            "videos",
            {"part": "snippet,contentDetails", "id": ",".join(batch_ids), "maxResults": 50},
        )
        found = {str(item.get("id")): item for item in (data.get("items") or [])}
        for vid in batch_ids:
            item = found.get(vid)
            event_rows = events_by_video.get(vid, [])
            if item:
                title = item.get("snippet", {}).get("title") or "VIDEO"
                duration = iso_duration_seconds(item.get("contentDetails", {}).get("duration"))
                for event in event_rows:
                    creator_name = current_creator_names.get(
                        int(event["creator_id"]) if event["creator_id"] is not None else -1,
                        "REMOVED CREATOR",
                    )
                    con.execute(
                        """
                        UPDATE watch_events
                        SET creator_name=?,video_title=?,duration_seconds=?,metadata_refreshed_at=?
                        WHERE id=?
                        """,
                        (creator_name, title, duration, now, event["id"]),
                    )
                con.execute(
                    "UPDATE watched SET metadata_refreshed_at=? WHERE video_id=?",
                    (now, vid),
                )
            else:
                # If YouTube no longer returns the resource, remove stale API data.
                con.execute("DELETE FROM watched WHERE video_id=?", (vid,))
                for event in event_rows:
                    creator_name = current_creator_names.get(
                        int(event["creator_id"]) if event["creator_id"] is not None else -1,
                        "REMOVED CREATOR",
                    )
                    con.execute(
                        """
                        UPDATE watch_events
                        SET creator_name=?,video_id='',video_title='UNAVAILABLE VIDEO',
                            duration_seconds=0,metadata_refreshed_at=?
                        WHERE id=?
                        """,
                        (creator_name, now, event["id"]),
                    )

    meta_set(con, "api_data_refresh_checked_at", now)
    return {
        "checked": True,
        "creatorRows": len(stale_creators),
        "videoIds": len(video_ids),
    }

def parse_channel_link(link):
    raw = (link or "").strip()
    if not raw:
        raise APIError("PASTE A YOUTUBE CHANNEL LINK.")
    if raw.startswith("@"):
        return "handle", raw[1:]
    if "://" not in raw:
        raw = "https://" + raw
    try:
        u = urlparse(raw)
    except Exception:
        raise APIError("INVALID CHANNEL LINK.")
    host = (u.hostname or "").lower()
    if host not in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        raise APIError("LINK MUST BE A YOUTUBE CHANNEL LINK.")
    parts = [p for p in u.path.split("/") if p]
    if not parts:
        raise APIError("INVALID CHANNEL LINK.")
    if parts[0].startswith("@"):
        return "handle", parts[0][1:]
    if parts[0] == "channel" and len(parts) > 1:
        return "id", parts[1]
    if parts[0] == "user" and len(parts) > 1:
        return "username", parts[1]
    raise APIError("USE A YOUTUBE @HANDLE OR /CHANNEL/ LINK.")


def resolve_channel(link):
    kind, value = parse_channel_link(link)
    params = {"part": "snippet,contentDetails"}
    if kind == "handle":
        params["forHandle"] = value
    elif kind == "id":
        params["id"] = value
    else:
        params["forUsername"] = value
    data = youtube_get("channels", params)
    items = data.get("items") or []
    if not items:
        raise APIError("CHANNEL NOT FOUND.", 404)
    c = items[0]
    uploads = (
        c.get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads")
    )
    if not uploads:
        raise APIError("CHANNEL UPLOADS PLAYLIST NOT AVAILABLE.", 502)
    return {
        "channel_id": c["id"],
        "name": c.get("snippet", {}).get("title") or value,
        "uploads_playlist": uploads,
    }


def ensure_creator_resolved(con, creator_id):
    row = con.execute("SELECT * FROM creators WHERE id=?", (creator_id,)).fetchone()
    if not row:
        raise APIError("CREATOR NOT FOUND.", 404)
    if row["channel_id"] and row["uploads_playlist"]:
        return row
    resolved = resolve_channel(row["link"])
    try:
        con.execute(
            "UPDATE creators SET channel_id=?,name=?,uploads_playlist=?,metadata_refreshed_at=? WHERE id=?",
            (resolved["channel_id"], resolved["name"], resolved["uploads_playlist"], time.time(), creator_id),
        )
    except sqlite3.IntegrityError:
        raise APIError("THAT CREATOR IS ALREADY IN AVAILABLE CREATORS.", 409)
    con.execute("DELETE FROM video_cache WHERE creator_id=?", (creator_id,))
    return con.execute("SELECT * FROM creators WHERE id=?", (creator_id,)).fetchone()


def iso_duration_seconds(value):
    if not value:
        return 0
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if not m:
        return 0
    h, mins, sec = (int(x or 0) for x in m.groups())
    return h * 3600 + mins * 60 + sec


def fetch_creator_videos(con, creator_id, refresh=False):
    creator = ensure_creator_resolved(con, creator_id)
    cache = con.execute(
        "SELECT fetched_at,payload FROM video_cache WHERE creator_id=?", (creator_id,)
    ).fetchone()
    if cache and not refresh and time.time() - cache["fetched_at"] < CACHE_TTL_SECONDS:
        return json.loads(cache["payload"])

    eligible = []
    token = None
    pages = 0
    seen = set()
    while len(eligible) < 20 and pages < MAX_PLAYLIST_PAGES:
        params = {
            "part": "contentDetails",
            "playlistId": creator["uploads_playlist"],
            "maxResults": 50,
        }
        if token:
            params["pageToken"] = token
        pl = youtube_get("playlistItems", params)
        ids = []
        for item in pl.get("items") or []:
            vid = item.get("contentDetails", {}).get("videoId")
            if vid and vid not in seen:
                seen.add(vid)
                ids.append(vid)
        if ids:
            vd = youtube_get(
                "videos",
                {
                    "part": "snippet,contentDetails,liveStreamingDetails",
                    "id": ",".join(ids),
                },
            )
            by_id = {v["id"]: v for v in vd.get("items") or []}
            for vid in ids:
                v = by_id.get(vid)
                if not v:
                    continue
                snippet = v.get("snippet", {})
                duration = iso_duration_seconds(v.get("contentDetails", {}).get("duration"))
                if duration < MIN_VIDEO_SECONDS:
                    continue
                if snippet.get("liveBroadcastContent") in {"live", "upcoming"}:
                    continue
                if "liveStreamingDetails" in v:
                    continue
                eligible.append(
                    {
                        "id": vid,
                        "title": snippet.get("title") or "UNTITLED VIDEO",
                        "publishedAt": snippet.get("publishedAt"),
                        "durationSeconds": duration,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                    }
                )
                if len(eligible) >= 20:
                    break
        pages += 1
        token = pl.get("nextPageToken")
        if not token:
            break

    payload = eligible[:20]
    con.execute(
        "INSERT INTO video_cache(creator_id,fetched_at,payload) VALUES(?,?,?) "
        "ON CONFLICT(creator_id) DO UPDATE SET fetched_at=excluded.fetched_at,payload=excluded.payload",
        (creator_id, time.time(), json.dumps(payload, separators=(",", ":"))),
    )
    return payload


def validate_settings(raw, old=None):
    old = old or DEFAULT_SETTINGS
    out = {**old}
    interval = raw.get("interval", out["interval"])
    if interval in {"daily", "weekly", "monthly", "yearly"}:
        out["interval"] = interval
    out["amount"] = max(0, min(100000, int(raw.get("amount", out["amount"]))))
    out["weekDay"] = int(raw.get("weekDay", out["weekDay"])) % 7
    out["rollover"] = bool(raw.get("rollover", out["rollover"]))
    out["block"] = bool(raw.get("block", out["block"]))
    out["cdH"] = max(0, min(999, int(raw.get("cdH", out["cdH"]))))
    out["cdM"] = max(0, min(59, int(raw.get("cdM", out["cdM"]))))
    sort = raw.get("sort", out["sort"])
    if sort in {"name", "upload", "length"}:
        out["sort"] = sort
    out["repeatCosts"] = bool(raw.get("repeatCosts", out["repeatCosts"]))
    out["normalizeCaps"] = bool(raw.get("normalizeCaps", out.get("normalizeCaps", False)))
    tz = raw.get("timezone", out.get("timezone", "UTC"))
    if isinstance(tz, str) and valid_timezone(tz):
        out["timezone"] = tz
    return out


@app.after_request
def security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "frame-ancestors 'none'; form-action 'self'",
    )
    return response


@app.get("/privacy")
def privacy_notice():
    response = send_from_directory(APP_DIR, "PRIVACY.md")
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/terms")
def project_terms():
    response = send_from_directory(APP_DIR, "TERMS.md")
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/favicon.svg")
def favicon_svg():
    return send_from_directory(APP_DIR, "favicon.svg")


@app.get("/apple-touch-icon.png")
def apple_touch_icon():
    return send_from_directory(APP_DIR, "apple-touch-icon.png")


@app.get("/icon-192.png")
def icon_192():
    return send_from_directory(APP_DIR, "icon-192.png")


@app.get("/icon-512.png")
def icon_512():
    return send_from_directory(APP_DIR, "icon-512.png")


@app.get("/manifest.webmanifest")
def web_manifest():
    response = send_from_directory(APP_DIR, "manifest.webmanifest")
    response.headers["Content-Type"] = "application/manifest+json; charset=utf-8"
    return response


@app.get("/")
def index():
    response = send_from_directory(APP_DIR, "index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/state")
def get_state():
    tz = request.args.get("tz", "").strip()
    with db() as con:
        try:
            refresh_stored_api_data(con)
        except Exception:
            app.logger.warning("Stored API metadata refresh failed", exc_info=True)
        if tz and valid_timezone(tz):
            settings = load_settings(con)
            if settings.get("timezone") != tz:
                settings["timezone"] = tz
                save_settings(con, settings)
        return jsonify(state_payload(con))


@app.post("/api/initialize")
def initialize():
    with db() as con:
        meta_set(con, "initialized", "1")
        return jsonify(state_payload(con))


@app.post("/api/migrate")
def migrate():
    payload = request.get_json(silent=True) or {}
    with db() as con:
        if meta_get(con, "initialized") == "1":
            return jsonify(state_payload(con))
        incoming_settings = payload.get("settings") or {}
        settings = validate_settings(incoming_settings, load_settings(con))
        save_settings(con, settings)
        try:
            meta_set(con, "credits", max(0, int(payload.get("credits", settings["amount"]))))
        except Exception:
            meta_set(con, "credits", settings["amount"])
        anchor = payload.get("anchor")
        if isinstance(anchor, str):
            meta_set(con, "anchor", anchor)
        cooldown = payload.get("cooldownUntil")
        if isinstance(cooldown, str) and cooldown:
            try:
                meta_set(con, "cooldown_until", datetime.fromisoformat(cooldown.replace("Z", "+00:00")).timestamp())
            except Exception:
                pass
        con.execute("DELETE FROM creators")
        creators = payload.get("creators") or []
        for pos, c in enumerate(creators):
            link = str(c.get("link") or "").strip()
            name = str(c.get("name") or "UNRESOLVED CREATOR").strip()
            if not link:
                continue
            con.execute(
                "INSERT INTO creators(name,link,position,added_at) VALUES(?,?,?,?)",
                (name, link, pos, time.time() + (pos * 0.001)),
            )
        meta_set(con, "initialized", "1")
        return jsonify(state_payload(con))


@app.put("/api/settings")
def update_settings():
    payload = request.get_json(silent=True) or {}
    incoming = payload.get("settings") or {}
    with db() as con:
        old = load_settings(con)
        new = validate_settings(incoming, old)
        save_settings(con, new)
        if old.get("interval") != new.get("interval") or old.get("weekDay") != new.get("weekDay"):
            meta_set(con, "anchor", period_start(new).isoformat())
        return jsonify(state_payload(con))


@app.get("/api/stats")
def get_stats():
    scope = request.args.get("scope", "period").strip().lower()
    if scope not in {"period", "all"}:
        scope = "period"
    with db() as con:
        try:
            refresh_stored_api_data(con)
        except Exception:
            app.logger.warning("Stored API metadata refresh failed", exc_info=True)
        return jsonify(stats_payload(con, scope))



@app.post("/api/credits/eject")
def eject_credit():
    with db() as con:
        apply_allowance_reset(con)
        credits = int(float(meta_get(con, "credits") or 0))
        if credits <= 0:
            raise APIError("NO WATCH CREDITS AVAILABLE TO EJECT.", 409)
        meta_set(con, "credits", credits - 1)
        return jsonify(state_payload(con))


@app.post("/api/creators")
def add_creator():
    payload = request.get_json(silent=True) or {}
    link = str(payload.get("link") or "").strip()
    resolved = resolve_channel(link)
    with db() as con:
        if con.execute("SELECT 1 FROM creators WHERE channel_id=?", (resolved["channel_id"],)).fetchone():
            raise APIError("THAT CREATOR IS ALREADY IN AVAILABLE CREATORS.", 409)
        pos = con.execute("SELECT COALESCE(MAX(position),-1)+1 FROM creators").fetchone()[0]
        con.execute(
            "INSERT INTO creators(channel_id,name,link,uploads_playlist,position,added_at,metadata_refreshed_at) VALUES(?,?,?,?,?,?,?)",
            (resolved["channel_id"], resolved["name"], link, resolved["uploads_playlist"], pos, time.time(), time.time()),
        )
        return jsonify(state_payload(con))


@app.delete("/api/creators/<int:creator_id>")
def remove_creator(creator_id):
    with db() as con:
        cur = con.execute("DELETE FROM creators WHERE id=?", (creator_id,))
        if cur.rowcount == 0:
            raise APIError("CREATOR NOT FOUND.", 404)
        rows = creator_rows(con)
        for i, row in enumerate(rows):
            con.execute("UPDATE creators SET position=? WHERE id=?", (i, row["id"]))
        return jsonify(state_payload(con))


@app.post("/api/creators/reorder")
def reorder_creators():
    payload = request.get_json(silent=True) or {}
    with db() as con:
        rows = list(creator_rows(con))
        requested_order = payload.get("order")
        if isinstance(requested_order, list):
            try:
                ids = [int(x) for x in requested_order]
            except Exception:
                raise APIError("INVALID CREATOR ORDER.")
            existing = [int(r["id"]) for r in rows]
            if len(ids) != len(existing) or len(set(ids)) != len(ids) or set(ids) != set(existing):
                raise APIError("INVALID CREATOR ORDER.")
            by_id = {int(r["id"]): r for r in rows}
            rows = [by_id[i] for i in ids]
        else:
            try:
                from_pos = int(payload.get("from")) - 1
                to_pos = int(payload.get("to")) - 1
            except Exception:
                raise APIError("INVALID CREATOR POSITION.")
            if not (0 <= from_pos < len(rows) and 0 <= to_pos < len(rows)):
                raise APIError("INVALID CREATOR POSITION.")
            moved = rows.pop(from_pos)
            rows.insert(to_pos, moved)
        for i, row in enumerate(rows):
            con.execute("UPDATE creators SET position=? WHERE id=?", (i, row["id"]))
        return jsonify(state_payload(con))


@app.get("/api/creators/<int:creator_id>/videos")
def creator_videos(creator_id):
    sort = request.args.get("sort", "upload")
    if sort not in {"name", "upload", "length"}:
        sort = "upload"
    refresh = request.args.get("refresh") == "1"
    with db() as con:
        videos = list(fetch_creator_videos(con, creator_id, refresh=refresh))
        watched_rows = con.execute("SELECT video_id FROM watched").fetchall()
        watched = {r["video_id"] for r in watched_rows}
        settings = load_settings(con)
        for v in videos:
            v["watched"] = v["id"] in watched
            v["cost"] = 0 if v["watched"] and not settings.get("repeatCosts") else 1
        if sort == "name":
            videos.sort(key=lambda x: x["title"].casefold())
        elif sort == "length":
            videos.sort(key=lambda x: x["durationSeconds"])
        else:
            videos.sort(key=lambda x: x.get("publishedAt") or "", reverse=True)
        creator = con.execute("SELECT * FROM creators WHERE id=?", (creator_id,)).fetchone()
        return jsonify({"creator": creator_dict(creator), "videos": videos})


@app.post("/api/override/check")
def check_override():
    payload = request.get_json(silent=True) or {}
    if str(payload.get("pin") or "") != OVERRIDE_PIN:
        raise APIError("INVALID PIN.", 403)
    return jsonify({"ok": True})


@app.post("/api/watch")
def watch():
    payload = request.get_json(silent=True) or {}
    video_id = str(payload.get("videoId") or "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise APIError("INVALID VIDEO ID.")

    override_pin = str(payload.get("overridePin") or "")

    try:
        creator_id = int(payload.get("creatorId"))
    except Exception:
        creator_id = None

    video_title = str(payload.get("videoTitle") or video_id).strip()[:1000]
    try:
        duration_seconds = max(0, int(payload.get("durationSeconds") or 0))
    except Exception:
        duration_seconds = 0

    with db() as con:
        settings, credits = apply_allowance_reset(con)
        remaining = cooldown_remaining_ms(con)
        if settings.get("block") and remaining > 0 and override_pin != OVERRIDE_PIN:
            raise APIError("REQUESTS LOCKED. COOLDOWN ACTIVE.", 423)

        creator = (
            con.execute("SELECT id,name FROM creators WHERE id=?", (creator_id,)).fetchone()
            if creator_id is not None
            else None
        )
        creator_name = creator["name"] if creator else "UNKNOWN CREATOR"

        row = con.execute("SELECT watch_count FROM watched WHERE video_id=?", (video_id,)).fetchone()
        was_watched = bool(row)
        cost = 0 if was_watched and not settings.get("repeatCosts") else 1
        if credits < cost:
            raise APIError("INSUFFICIENT WATCH CREDITS.", 402)
        meta_set(con, "credits", credits - cost)
        now = time.time()
        override_used = bool(
            settings.get("block") and remaining > 0 and override_pin == OVERRIDE_PIN
        )
        con.execute(
            """
            INSERT INTO watch_events(
                requested_at,creator_id,creator_name,video_id,video_title,
                duration_seconds,credit_cost,was_rewatch,override_used,metadata_refreshed_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                now,
                creator["id"] if creator else creator_id,
                creator_name,
                video_id,
                video_title,
                duration_seconds,
                cost,
                1 if was_watched else 0,
                1 if override_used else 0,
                now,
            ),
        )
        if row:
            con.execute(
                "UPDATE watched SET watched_at=?,watch_count=watch_count+1,metadata_refreshed_at=? WHERE video_id=?",
                (now, now, video_id),
            )
        else:
            con.execute(
                "INSERT INTO watched(video_id,watched_at,watch_count,metadata_refreshed_at) VALUES(?,?,1,?)",
                (video_id, now, now),
            )
        if settings.get("block"):
            cooldown_seconds = (int(settings.get("cdH", 0)) * 60 + int(settings.get("cdM", 0))) * 60
            meta_set(con, "cooldown_until", now + cooldown_seconds)
        return jsonify(
            {
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "cost": cost,
                "state": state_payload(con),
            }
        )


@app.get("/api/history")
def history():
    try:
        limit = int(request.args.get("limit", "10"))
    except Exception:
        limit = 10
    limit = min(50, max(1, limit))

    with db() as con:
        try:
            refresh_stored_api_data(con)
        except Exception:
            app.logger.warning("Stored API metadata refresh failed", exc_info=True)
        settings = load_settings(con)
        rows = con.execute(
            """
            SELECT requested_at,creator_name,video_id,video_title,duration_seconds,
                   credit_cost,was_rewatch,override_used
            FROM watch_events
            ORDER BY requested_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        tz = tz_for(settings)
        return jsonify(
            {
                "items": [
                    {
                        "requestedAt": datetime.fromtimestamp(
                            float(row["requested_at"]), tz=tz
                        ).isoformat(),
                        "creatorName": row["creator_name"],
                        "videoId": row["video_id"],
                        "videoTitle": row["video_title"],
                        "durationSeconds": int(row["duration_seconds"] or 0),
                        "creditCost": int(row["credit_cost"] or 0),
                        "wasRewatch": bool(row["was_rewatch"]),
                        "overrideUsed": bool(row["override_used"]),
                    }
                    for row in rows
                ]
            }
        )


@app.get("/api/diag")
def diag():
    with db() as con:
        # A real query doubles as the DB connectivity test.
        con.execute("SELECT 1").fetchone()

    try:
        db_size = DB_PATH.stat().st_size
    except Exception:
        db_size = 0

    return jsonify(
        {
            "appVersion": APP_VERSION,
            "backend": "OK",
            "database": "OK",
            "youtubeConfigured": bool(YOUTUBE_API_KEY),
            "databaseBytes": int(db_size),
            "serverTime": datetime.now().astimezone().isoformat(),
        }
    )


@app.post("/api/cache/flush")
def flush_cache():
    with db() as con:
        removed = int(con.execute("SELECT COUNT(*) FROM video_cache").fetchone()[0])
        con.execute("DELETE FROM video_cache")
        return jsonify({"ok": True, "removed": removed})


@app.get("/api/export")
def export_data():
    with db() as con:
        try:
            refresh_stored_api_data(con)
        except Exception:
            app.logger.warning("Stored API metadata refresh failed", exc_info=True)
        settings, credits = apply_allowance_reset(con)

        creators = [
            {
                "id": int(row["id"]),
                "channelId": row["channel_id"],
                "name": row["name"],
                "link": row["link"],
                "uploadsPlaylist": row["uploads_playlist"],
                "position": int(row["position"]),
                "addedAt": float(row["added_at"] or 0),
                "metadataRefreshedAt": float(row["metadata_refreshed_at"] or 0),
            }
            for row in con.execute(
                """
                SELECT id,channel_id,name,link,uploads_playlist,position,added_at,metadata_refreshed_at
                FROM creators
                ORDER BY position ASC, id ASC
                """
            ).fetchall()
        ]

        watched = [
            {
                "videoId": row["video_id"],
                "watchedAt": float(row["watched_at"]),
                "watchCount": int(row["watch_count"]),
                "metadataRefreshedAt": float(row["metadata_refreshed_at"] or 0),
            }
            for row in con.execute(
                "SELECT video_id,watched_at,watch_count,metadata_refreshed_at FROM watched ORDER BY watched_at ASC"
            ).fetchall()
        ]

        watch_events = [
            {
                "requestedAt": float(row["requested_at"]),
                "creatorId": row["creator_id"],
                "creatorName": row["creator_name"],
                "videoId": row["video_id"],
                "videoTitle": row["video_title"],
                "durationSeconds": int(row["duration_seconds"] or 0),
                "creditCost": int(row["credit_cost"] or 0),
                "wasRewatch": bool(row["was_rewatch"]),
                "overrideUsed": bool(row["override_used"]),
                "metadataRefreshedAt": float(row["metadata_refreshed_at"] or 0),
            }
            for row in con.execute(
                """
                SELECT requested_at,creator_id,creator_name,video_id,video_title,
                       duration_seconds,credit_cost,was_rewatch,override_used,metadata_refreshed_at
                FROM watch_events
                ORDER BY requested_at ASC, id ASC
                """
            ).fetchall()
        ]

        try:
            cooldown_until = float(meta_get(con, "cooldown_until") or 0)
        except Exception:
            cooldown_until = 0

        try:
            stats_started = float(meta_get(con, "stats_started_at") or 0)
        except Exception:
            stats_started = 0

        payload = {
            "schemaVersion": 1,
            "appVersion": APP_VERSION,
            "exportedAt": datetime.now().astimezone().isoformat(),
            "settings": settings,
            "credits": int(credits),
            "cooldownUntil": cooldown_until,
            "statsTrackingSince": stats_started,
            "creators": creators,
            "watched": watched,
            "watchEvents": watch_events,
        }

    body = json.dumps(payload, indent=2, ensure_ascii=False)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    response = Response(body, mimetype="application/json")
    response.headers["Content-Disposition"] = (
        f'attachment; filename="video-destim-terminal-export-{stamp}.json"'
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.post("/api/data/delete")
def delete_local_data():
    with db() as con:
        con.execute("DELETE FROM video_cache")
        con.execute("DELETE FROM watch_events")
        con.execute("DELETE FROM watched")
        con.execute("DELETE FROM creators")
        con.execute("DELETE FROM sqlite_sequence WHERE name IN ('creators','watch_events')")
        settings = dict(DEFAULT_SETTINGS)
        save_settings(con, settings)
        meta_set(con, "credits", settings["amount"])
        meta_set(con, "anchor", "")
        meta_set(con, "cooldown_until", "0")
        meta_set(con, "initialized", "1")
        meta_set(con, "stats_started_at", str(time.time()))
        meta_set(con, "api_data_refresh_checked_at", "0")
        return jsonify(state_payload(con))


@app.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "appVersion": APP_VERSION,
            "youtubeConfigured": bool(YOUTUBE_API_KEY),
        }
    )


init_db()
