# Changelog

## v1.30 — Initial public GitHub release

This is the first public GitHub release of Video Destim Terminal.

### Core experience

- Text-first, low-stimulation creator/video selection interface with no thumbnail/feed wall inside VDT.
- User-curated creator list with add/remove/reorder controls.
- Up to 20 recent eligible uploads per creator; videos 3:00 or shorter and live/upcoming/live-origin items are excluded.
- Configurable credit allowance interval/amount, rollover, consecutive-watch blocking, cooldown, default sort, rewatch credit cost, and optional title-cap normalization.
- Manual cooldown override with operator-chosen four-digit PIN.
- Local watched state, request history, and VDT request/activity Stats.
- Confirmed selections hand off to a standard YouTube watch URL; VDT does not embed/proxy/download the audiovisual stream.

### Terminal navigation / utilities

- Home menu exposes Request a Watch, Config, Stats, and Command Doc.
- Global text commands include `request-watch`, `config`, `stats`, `command-doc`, `about`, `history`, `diag`, `flush-cache`, `export-data`, `support`, `legal`, `delete-data`, and `credit-eject`.
- Command Doc entries are clickable.
- `read-doc` remains an unadvertised compatibility alias for older pre-release builds.
- Touch/mouse controls, visible letter/number shortcuts, multi-digit selection buffering, keyboard shortcuts, and terminal prompt coexist.

### Data/privacy/security

- Self-hosted SQLite persistence under `data/`.
- API key stays server-side and is excluded from `export-data`.
- First-run legal/privacy acknowledgement plus persistent `LEGAL` access.
- Confirmed local data deletion.
- Best-effort refresh/removal of stored public YouTube API metadata before 30 days.
- Docker binds to localhost by default; Tailscale Serve/authenticated reverse proxy documented for remote access.
- `.gitignore`, security/privacy/terms/compliance docs, and public issue templates included.

### UI polish

- Responsive green terminal frame for desktop/mobile.
- Custom green/black favicon, touch icon, and PWA manifest icons.
- `VIDEO-DESTIM-TERMINAL` visible header.
- `SUPPORT · LEGAL` header actions.
- Creator-title emoji characters preserved while using a display-only grayscale/green terminal treatment where browser rendering allows it.

### Public documentation

- Added `setup.sh` as the recommended guided SSH configuration path for entering the YouTube API key and four-digit override PIN without opening `.env` in an editor; manual `.env` setup remains available.
- Separate existing-Docker and blank-Ubuntu install paths.
- YouTube API key setup/restriction guide.
- Tailscale Serve/networking guide.
- Full Config and Command reference.
- Optional playback-options comparison.
- Backup/restore, troubleshooting, architecture, FAQ, updating/rollback, contribution, security, privacy, terms, compliance, and GitHub publishing guides.
- Update guide includes both one-shot copy/paste and one-command-at-a-time/mobile SSH workflows.

---

## Pre-public release checkpoints

The following versions were development/distribution checkpoints used to reach the v1.30 public release. They are retained for project history but were not the initial GitHub release.

### v1.29 — Terminal-style emoji presentation

- Requested text/monochrome emoji presentation while preserving creator-provided title characters.
- Added display-only fallback behavior for browsers that did not honor the text-emoji request.

### v1.28 — Clickable Command Doc + support command

- Made every listed global Command Doc command clickable.
- Added `support` as a global text command.
- Clarified `delete-data` description with `AFTER Y/N CONFIRMATION`.

### v1.27 — Command access

- Added `[4] COMMAND DOC` to the home screen.
- Renamed the advertised command-reference command from `read-doc` to `command-doc`, retaining `read-doc` as a compatibility alias.
- Added `request-watch`, `config`, and `stats` text commands.
- Routed navigation commands through Config/Reorder unsaved-change safeguards.

### v1.26 — Navigation safeguards + support link

- Added `[S] SAVE AND EXIT` to Config/Reorder unsaved-change prompts and changed prompts to `[Y/N/S]`.
- Extended pending Config-change protection through Available Creators/Add Creator navigation.
- Fixed Reorder Creators navigation so both the CONFIG breadcrumb and main title protect unsaved reorder changes.
- Added `SUPPORT` to the left of `LEGAL`; Yes opens the creator tip jar.
- Added one-shot and one-command-at-a-time updating/rollback documentation.

### v1.25 — UI polish + blank-server install path

- Added responsive terminal border/frame.
- Added custom favicon/touch/PWA icons.
- Changed visible header to `VIDEO-DESTIM-TERMINAL`.
- Removed the Stats-only CYA disclaimer line.
- Updated About attribution to `Developed with YouTube API`.
- Added blank-Ubuntu Docker and optional Tailscale Serve installation documentation.
- Standardized **CHOOSE OVERRIDE PIN** setup wording.

### v1.24 — Public-distribution preparation

- Renamed project to **Video Destim Terminal** across package/docs/application.
- Restored optional `NORMALIZE VIDEO TITLE CAPS?` (default No).
- Moved API attribution out of the persistent footer and into About.
- Added legal/privacy acknowledgement, data deletion, API metadata refresh, localhost binding, and playback-options documentation.

### v1.23 — First sanitized packaging checkpoint

- Created first GitHub-oriented sanitized distribution branch.
- Added initial README/license/privacy/terms/security/contribution/compliance files.
- Added first-run legal acknowledgement, local data deletion, API metadata refresh, and playback-options documentation.

### Earlier private iterations

The project went through numerous private v0.x/v1.x development iterations before the distribution checkpoints above. Those builds are intentionally not included as public releases.
