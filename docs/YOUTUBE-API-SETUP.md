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

Do not use a browser HTTP-referrer restriction for a server-side key unless your deployment specifically routes the API call in a way that supports it; an incorrect restriction will simply make VDT's server-side requests fail.

## Put the key in VDT

Copy the example environment file if you have not already:

```bash
cp .env.example .env
```

Set:

```text
YOUTUBE_API_KEY=your_real_key_here
```

Also set the required four-digit cooldown override PIN:

```text
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
{"appVersion":"v1.30","ok":true,"youtubeConfigured":true}
```

`youtubeConfigured:true` only means a non-empty key was loaded. The first real creator/API request is the practical verification that the credential, API enablement, restrictions, and quota all work together.

## How VDT uses quota

For normal creator refreshes, VDT resolves channel data, reads the creator's uploads playlist, and requests video metadata in batches. It does not use YouTube search for ordinary creator browsing.

The default video-list cache is 15 minutes (`CACHE_TTL_SECONDS=900`) to avoid unnecessary repeated API requests.

VDT also performs best-effort refresh of stored public YouTube API resource metadata before it reaches 30 days old. Those refreshes are batched where possible.

YouTube/Google can change quota, credential, and policy behavior. Do not rely on old screenshots or a fixed quota assumption; use the current official documentation for your project.

## Keep the key private

Never commit or paste publicly:

- `.env`;
- the API key;
- logs that contain a credential;
- screenshots of the Google Cloud credentials page with the key visible.

VDT's `export-data` output intentionally does not include the API key.
