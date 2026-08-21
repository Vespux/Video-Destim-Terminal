# FAQ

## Is Video Destim Terminal a YouTube replacement?

No. VDT is a self-hosted selection layer. It uses YouTube's public API metadata to present a deliberately limited text-first list, then opens the normal YouTube watch URL for playback.

## Does VDT play or download videos itself?

No. It does not host, proxy, download, transcode, or embed audiovisual content.

## Does it need my YouTube login?

No. The normal VDT feature set uses an operator-created YouTube Data API v3 key for public metadata. It does not use YouTube OAuth or ask for your YouTube username/password.

## Does each user need an API key?

Each independently hosted **instance/operator** should use its own Google Cloud project/API key. VDT is not a centrally hosted multi-user service.

## Does VDT know my YouTube watch history?

No. VDT tracks its own confirmed watch requests locally. It does not read your YouTube account watch history.

Whether a confirmed playback appears in your YouTube account history depends on the playback environment you open and whether that environment is signed into YouTube.

## Does VDT remove recommendations after the video opens?

VDT controls only the selection interface **before** playback. Once it opens the standard watch URL, the browser/player controls the playback UI.

See [PLAYBACK-OPTIONS.md](PLAYBACK-OPTIONS.md) for optional playback environments that can reduce suggested/next surfaces.

## Why are videos 3 minutes or shorter missing?

That is intentional. VDT excludes videos at or below 3:00 as part of its low-stimulation eligibility rules. This also excludes Shorts by duration without relying on a separate Shorts classification.

## Why are live videos missing?

Live, upcoming, and live-origin items are intentionally excluded from Request a Watch.

## Why are some creator titles/videos stale?

Creator video lists use a short cache to reduce API traffic. Use `REFRESH CREATOR` or the `flush-cache` command if you need to bypass/clear it.

Stored public API metadata in local history/creator records also has separate best-effort refresh housekeeping for API data-retention purposes.

## What happens to emoji in video titles?

VDT preserves the creator-provided emoji characters. The UI applies a display-only grayscale/green treatment to make them fit the terminal aesthetic better. Browser/OS emoji engines can still make those glyphs look different from the VT323 text font.

## What does Normalize Video Title Caps do?

When enabled, it changes unnecessary ALL-CAPS words in VDT's displayed/recorded title text while preserving common acronyms and digit-containing tokens. It is off by default.

Current YouTube API policy guidance says video metadata such as titles should remain unmodified, so review [COMPLIANCE.md](../COMPLIANCE.md) before enabling that option where strict policy compliance matters.

## Is the override PIN a password?

No. It only bypasses the configured request cooldown for the next request. Anyone who can reach an unprotected VDT web interface can access other application functions.

Use Tailscale/private VPN or a reverse proxy with real authentication/access control.

## Can I expose VDT directly to the internet?

You should not expose port 8790 directly. The public Compose file binds to localhost by default specifically because VDT has no login system.

## Can multiple people share one instance?

Technically anyone who can reach the interface operates the same shared database/credit state, but VDT has no accounts, permissions, or per-user separation. The intended design is personal/small trusted-access self-hosting.

## Does VDT send analytics to the project author?

No VDT analytics/telemetry service is included in the unmodified release, and independently hosted instance databases are not sent to the author.

The browser does contact Google Fonts for the VT323 web font, and VDT uses Google/YouTube services for the API/legal/watch handoff described in [PRIVACY.md](../PRIVACY.md).

## What does SUPPORT do?

It asks `OPEN CREATOR'S TIP JAR? [Y/N]`. Only after choosing Yes does VDT open the creator's Ko-fi page.

## Can I back up/move my instance?

Yes. Stop the container and preserve `.env` plus the `data/` directory. See [BACKUP-RESTORE.md](BACKUP-RESTORE.md).

## How do I update?

See [UPDATING.md](UPDATING.md). It includes one all-at-once copy/paste command and the same workflow broken into one command per step.
