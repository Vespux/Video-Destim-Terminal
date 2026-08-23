# FAQ

This page answers common questions briefly and links to the authoritative guide when a topic needs procedures or deeper detail.

## Is Video Destim Terminal a YouTube replacement?

No. VDT is a self-hosted selection layer that presents a deliberately limited text-first list, then opens the normal YouTube watch URL for playback.

## Does VDT play or download videos itself?

No. It does not host, proxy, download, transcode, or embed audiovisual content.

## Does it need my YouTube login?

No. VDT uses an operator-created YouTube Data API v3 key for public metadata. It does not use YouTube OAuth or ask for your YouTube username/password.

See [YouTube API Setup](YOUTUBE-API-SETUP.md).

## Does each user need an API key?

Each independently hosted **instance/operator** should use its own Google Cloud project/API key. VDT is not a centrally hosted multi-user service.

## Will normal VDT use exhaust my YouTube API quota?

Very unlikely. VDT uses low-cost API methods, does not use `search.list`, and caches creator video lists. A typical fresh creator refresh is about 2 quota units against Google's current 10,000-unit daily bucket for the methods VDT uses.

Reaching the quota does not automatically start billing for extra VDT requests. See [YouTube API Quota & Usage](YOUTUBE-API-SETUP.md#youtube-api-quota--usage) for the full breakdown and current caveats.

## Does VDT know my YouTube watch history?

No. VDT tracks only its own confirmed requests locally. Whether playback later appears in your YouTube account history depends on the playback environment and whether that environment is signed into YouTube.

## Does VDT remove recommendations after the video opens?

No. VDT controls the selection interface **before** playback; the browser/player controls what appears after handoff.

See [Playback Options](PLAYBACK-OPTIONS.md) for optional lower-stimulation playback environments.

## Why are videos 3 minutes or shorter missing?

That is intentional. VDT excludes videos at or below 3:00 as part of its eligibility rules. See [Configuration](CONFIGURATION.md#eligibility-rules).

## Why are live videos missing?

Live, upcoming, and live-origin items are intentionally excluded. See [Configuration](CONFIGURATION.md#eligibility-rules).

## Why are some creator titles/videos stale?

Creator video lists use a short cache to reduce API traffic. Use `REFRESH CREATOR` or `flush-cache` when you need to bypass/clear it. See [Troubleshooting](TROUBLESHOOTING.md#creator-list-seems-stale).

## What happens to emoji in video titles?

VDT preserves creator-provided emoji characters and applies a display-only grayscale/green treatment. Browser/OS emoji engines can still make those glyphs look different from the terminal font.

## What does Normalize Video Title Caps do?

It optionally changes unnecessary ALL-CAPS words in VDT's displayed/recorded title text. It is off by default. See [Configuration](CONFIGURATION.md#11-normalize-video-title-caps) and review [COMPLIANCE.md](../COMPLIANCE.md) before enabling it where strict YouTube API-policy compliance matters.

## Is the override PIN a password?

No. It only bypasses the configured request cooldown. It does not protect the interface. See [SECURITY.md](../SECURITY.md).

## Can I expose VDT directly to the internet?

Do not expose port `8790` directly. VDT has no login system and binds to localhost by default. See [Networking & HTTPS](NETWORKING.md).

## Can multiple people share one instance?

Technically, yes, but everyone operates the same database/credit state and there are no accounts or per-user permissions. The intended design is personal/small trusted-access self-hosting.

## Does VDT send analytics to the project author?

The unmodified release contains no VDT telemetry service and does not send an independently hosted instance database to the author. See [PRIVACY.md](../PRIVACY.md) for the complete network/data disclosure.

## What does SUPPORT do?

It asks `OPEN CREATOR'S TIP JAR? [Y/N]` before opening the creator's Ko-fi page. See [Terminal Commands](COMMANDS.md#support).

## Can I back up or move my instance?

Yes. See [Backup & Restore](BACKUP-RESTORE.md).

## How do I update?

See [Updating](UPDATING.md). It includes both an all-at-once copy/paste workflow and the same process one command at a time.
