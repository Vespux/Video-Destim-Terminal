# Terminal Commands

VDT supports three control methods at the same time:

1. tap/click a visible terminal option;
2. use a physical keyboard shortcut;
3. type a command/shortcut into the `>` prompt and press Enter.

The home screen also exposes `COMMAND DOC`, and every global command listed in the in-app Command Doc is clickable.

## Main navigation commands

| Command | Function |
|---|---|
| `request-watch` | Open Request a Watch |
| `config` | Open Config |
| `stats` | Open current-period Stats |
| `command-doc` | Open the built-in Command Doc |

These navigation commands respect Config/Reorder unsaved-change safeguards.

## Utility commands

| Command | Function |
|---|---|
| `about` | Show build/author information |
| `history` | Show the 10 most recent VDT watch requests |
| `diag` | Show backend/database/cache diagnostics |
| `flush-cache` | Clear cached creator video lists after Y/N confirmation |
| `export-data` | Download local configuration/creator/history JSON |
| `support` | Ask before opening the creator support/tip-jar page |
| `legal` | Open privacy/terms/data controls |
| `delete-data` | Permanently reset all local VDT data after Y/N confirmation |
| `credit-eject` | Remove one current watch credit after Y/N confirmation |

### Compatibility alias

`read-doc` from older pre-release builds still opens Command Doc, but `command-doc` is the documented command going forward.

## Context shortcuts

- A visible number selects the corresponding numbered item.
- A visible letter runs the corresponding `[LETTER]` action.
- Multi-digit numbered options are supported with a short numeric input buffer.
- `Esc` performs the safe Back/Cancel/No action where available.
- `Enter` activates a marked default action where available.

Keyboard shortcuts are ignored while focus is inside an input field so typing a creator URL, PIN, number, or command does not accidentally activate menu actions.

## `history`

History is **local VDT request history**, not YouTube account watch history. It records the video/creator involved in confirmed VDT requests, time, credit cost, rewatch status, and manual-override status.

## `diag`

Diagnostic output includes:

- VDT app version;
- backend/database status;
- whether a YouTube API key is configured;
- local database size;
- cache information;
- server time.

It intentionally does not print the API key or override PIN.

## `flush-cache`

Clears cached creator video lists. It does not remove creators, Config, watched state, request history, or stats.

## `export-data`

The JSON export includes local settings, creators/order, credits, watched state, cooldown timestamp, stats start time, and watch-request events.

It intentionally excludes the YouTube API key and override PIN.

Treat exports as private: they can contain creator choices and local request history.

## `support`

Shows:

```text
OPEN CREATOR'S TIP JAR? [Y/N]
```

`Y` opens the VDT creator's Ko-fi page in a new tab/window. `N` returns without opening an external site.

## `delete-data`

Resets the local VDT database after confirmation. It does **not** delete YouTube account history, subscriptions, Google data, or data stored by a third-party playback application.

## `credit-eject`

Removes one current watch credit after confirmation. This is a deliberate maintenance/self-control utility and cannot be undone except through normal allowance behavior or restoring a backup.

## Unadvertised easter eggs

The source contains a very small number of harmless easter eggs/debug-era curiosities that are intentionally omitted from Command Doc. 