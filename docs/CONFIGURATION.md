# Configuration

VDT configuration is stored in the local SQLite database. The main `CONFIG` screen stages changes until you explicitly save them.

## Default settings

| # | Setting | Default |
|---:|---|---|
| 1 | Credit Allowance Interval | Weekly |
| 2 | Weekly Reset Day | Monday |
| 3 | Credit Allowance Amount | 3 |
| 4 | Unused Credits Rollover | No |
| 5 | Available Creators | Empty on a fresh install |
| 6 | Reorder Creators | — |
| 7 | Block Consecutive Watches? | Yes |
| 8 | Request Cooldown | 1H 0M |
| 9 | Default Sort for Videos | Upload date |
| 10 | Watched Videos Cost Credits? | No |
| 11 | Normalize Video Title Caps? | No |

## Save / cancel behavior

Changes made to the main Config settings are staged locally until you choose:

- `[S] SAVE` — save Config and return home.
- `[C] CANCEL` — discard the Config draft and return home.
- `[B] BACK` — attempt to leave Config.

If you try to leave the Config workflow with unsaved settings, VDT prompts:

```text
LEAVE CONFIG? [Y/N/S]
```

- `Y` — discard the pending settings and continue to the requested destination.
- `N` — stay where you were.
- `S` — **SAVE AND EXIT**, then continue to the requested destination.

This protection also follows a pending Config draft through `AVAILABLE CREATORS` and `ADD CREATOR`. An unfinished Add Creator text field is not itself treated as a staged Config change; however, Config changes you made before entering that screen remain protected if you navigate away.

## 1. Credit Allowance Interval

Cycles the allowance reset schedule through:

- Daily
- Weekly
- Monthly
- Yearly

The reset is calculated in the browser/device's detected timezone and stored in the VDT settings.

## 2. Weekly Reset Day

Only applies when the allowance interval is Weekly.

The item remains visible for layout consistency and displays `N/A` when the active interval is not Weekly.

## 3. Credit Allowance Amount

Number of new watch credits granted at each allowance reset.

## 4. Unused Credits Rollover

- `NO`: the next reset replaces the remaining balance with the configured allowance.
- `YES`: the next allowance is added to remaining credits.

There is no separate rollover cap.

## 5. Available Creators

Creators are the only sources VDT browses for watch requests.

Supported add formats:

- YouTube `@handle` URLs;
- `/channel/` URLs;
- legacy `/user/` URLs.

Adding a creator resolves its current public channel metadata with the YouTube Data API.

Removing a creator removes it from the available creator list. Existing local watch-request history can remain as historical VDT activity.

## 6. Reorder Creators

Reorder supports:

- sort by name;
- sort by date added;
- manual `MOVE CREATOR #` → `NEW POSITION`.

Reorder changes are staged separately from main Config settings. You can `SAVE`, `CANCEL`, or `BACK`.

If you try to leave Reorder Creators with unsaved order changes — including through the `CONFIG` breadcrumb or the `VIDEO-DESTIM-TERMINAL` home title — VDT prompts:

```text
LEAVE REORDER CREATORS? [Y/N/S]
```

`S` saves the new order before continuing to the destination you selected.

## 7. Block Consecutive Watches?

When `YES`, a successful watch request starts the configured request cooldown and normal requests are locked until it expires.

When `NO`, the Request Cooldown setting is displayed as `N/A` and consecutive requests are allowed.

## 8. Request Cooldown

Sets cooldown hours/minutes used when Block Consecutive Watches is enabled.

During a cooldown, `REQUEST A WATCH` shows `REQUESTS LOCKED` and offers `MANUAL OVERRIDE`. 

## Manual override

The four-digit PIN comes from `.env`.

A successful override only authorizes the next request. After that request, the normal cooldown behavior resumes.

## 9. Default Sort for Videos

Available sorts:

- Name
- Upload date
- Length

VDT first gathers up to 20 recent eligible uploads, then sorts that eligible set for display.

The video list also provides `CHANGE SORT` for a temporary list-level sort change.

## 10. Watched Videos Cost Credits?

- `NO` (default): re-requesting a video already marked watched by VDT costs 0 credits.
- `YES`: a re-request costs a credit like an initial request.

Watched state is local VDT state. It is not a read of your YouTube account watch history.

## 11. Normalize Video Title Caps?

Default: `NO`.

When enabled, VDT normalizes unnecessary ALL-CAPS words of three or more letters while preserving a built-in list of common acronyms/initialisms and tokens containing digits.

Example:

```text
I Bought the WORST Controller on AMAZON
```

becomes:

```text
I Bought the Worst Controller on Amazon
```

This changes VDT's displayed/recorded title text; it does not rename the video on YouTube.

**API policy note:** current YouTube developer-policy guidance says video metadata such as titles should be shown unmodified. For that reason this option is disabled by default. Review [COMPLIANCE.md](../COMPLIANCE.md) before enabling it in a deployment where strict API-policy compliance is a priority.

## Eligibility rules

The public release excludes:

- videos with a duration of **3:00 or shorter**;
- current live broadcasts;
- upcoming broadcasts/premieres;
- items carrying live-stream origin metadata.

Eligible creator lists are capped at 20 items. VDT can scan multiple uploads-playlist pages to find those items; the maximum scan depth is controlled by `MAX_PLAYLIST_PAGES` in `.env`.

## Cache tuning

`CACHE_TTL_SECONDS` in `.env` controls the short-lived creator-video-list cache. Default:

```text
CACHE_TTL_SECONDS=900
```

That is 15 minutes. `REFRESH CREATOR` bypasses the normal list cache, and the `flush-cache` command clears all creator-video-list cache entries after confirmation.
