# YouTube Data API v3 Setup

Each VDT operator should use their **own** Google Cloud project and API key.

Official starting point:

https://developers.google.com/youtube/v3/getting-started

VDT uses an API key for public channel/video metadata. It does not require YouTube OAuth login for its normal feature set.

## Create a project and key

1. Open Google Cloud Console.
2. Create a new project, or intentionally select an existing project you control.
3. Open **APIs & Services → Library**.
4. Enable **YouTube Data API v3**.
5. Open **APIs & Services → Credentials**.
6. Create an **API key**.
7. Edit/restrict the key.
8. Under **API restrictions**, restrict the key to **YouTube Data API v3**.

### Application restrictions

VDT makes YouTube API calls from the **server**, not from browser JavaScript.

If your server has a stable public egress IP and Google Cloud offers an appropriate IP-address application restriction for your setup, you can consider restricting the key to that IP as an additional safeguard.

Do not use a browser HTTP-referrer restriction for a server-side key unless your deployment specifically supports it; an incompatible restriction will make VDT's server-side requests fail.

## Put the key in VDT

### Recommended — guided SSH setup

From the VDT project directory, run:

```bash
bash setup.sh
```

The helper prompts for:

```text
ENTER YOUTUBE API KEY:
CHOOSE OVERRIDE PIN:
```

Both values are hidden while you enter them. The helper:

- requires a non-empty API key and rejects whitespace in it;
- requires the override PIN to be exactly four digits;
- writes both values to `.env` without echoing them back;
- preserves the other `.env` settings;
- applies `chmod 600 .env`;
- asks before changing credentials if `.env` already exists;
- does **not** start Docker automatically.

The override PIN only bypasses VDT's request cooldown. It is not login/authentication.

After configuration:

```bash
docker compose up -d --build
```

### Manual alternative

If you prefer to manage `.env` yourself:

```bash
cp .env.example .env
```

Set:

```text
YOUTUBE_API_KEY=your_real_key_here
OVERRIDE_PIN=your_four_digits
```

Then:

```bash
chmod 600 .env
docker compose up -d --build
```

## Verify

```bash
curl http://127.0.0.1:8790/health
```

You want:

```json
{"appVersion":"v1.30.1","ok":true,"youtubeConfigured":true}
```

`youtubeConfigured:true` only means a non-empty key was loaded. The first real creator/API request is the practical verification that the credential, API enablement, restrictions, and quota all work together.

## YouTube API Quota & Usage

Video Destim Terminal uses the YouTube Data API to retrieve creator and video information. Google applies daily quota limits to YouTube Data API projects, but normal VDT usage is unlikely to come close to the default allowance.

At the time of writing, Google provides a default quota of **10,000 units per day** combined for the API methods used by VDT. VDT does **not** use the separately limited `search.list` endpoint.

VDT primarily uses:

- `channels.list` — 1 quota unit
- `playlistItems.list` — 1 quota unit
- `videos.list` — 1 quota unit

A typical fresh refresh of one creator therefore uses about **2 quota units**: one request to retrieve videos from the creator's uploads playlist and one request to retrieve the associated video information.

When additional pages must be checked—for example, when filtering short videos, live streams, or other excluded results—VDT can make additional requests. VDT currently checks a maximum of four uploads-playlist pages, making approximately **8 units** the upper end of a normal creator refresh.

Adding a new creator generally requires one additional `channels.list` request.

VDT also caches creator video lists for 15 minutes by default (`CACHE_TTL_SECONDS=900`), so repeatedly opening the same creator during that window does not normally make additional YouTube API requests. Separate best-effort metadata-refresh housekeeping is batched where possible.

For perspective, a 10,000-unit daily quota would allow roughly **5,000 typical two-unit creator refreshes** in a day, or roughly **1,250 four-page/eight-unit refreshes**. Even unusually heavy personal use *should* therefore remain well below the default limit.

API quota is a usage limit, **not a pay-as-you-go billing meter**. Reaching the applicable quota does not automatically purchase or begin billing for additional YouTube Data API requests. Requests instead begin failing after the quota is exhausted until the quota resets or additional quota is approved.

Daily quota resets occur at **midnight Pacific Time**.

Google can change quota allocations, buckets, or API costs. Check the current official quota documentation and your project's Google Cloud quota page rather than relying indefinitely on the numbers above:

- Quota calculator/costs: https://developers.google.com/youtube/v3/determine_quota_cost
- Google Cloud Console: **APIs & Services → YouTube Data API v3 → Quotas & System Limits**

## Keep the key private

Never commit or paste publicly:

- `.env`;
- the API key;
- logs that contain a credential;
- screenshots of the Google Cloud credentials page with the key visible.

VDT's `export-data` output intentionally does not include the API key.

For broader private-file and network guidance, see [SECURITY.md](../SECURITY.md).
