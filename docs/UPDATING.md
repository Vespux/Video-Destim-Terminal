# Updating Video Destim Terminal

VDT release-ZIP updates are designed to preserve your local `.env` and `data/` while keeping the previous release folder intact for rollback.

Before updating:

1. read the new release's `CHANGELOG.md`;
2. make a backup if the instance matters to you;
3. make sure the new release ZIP is already on the VDT host.

See [Backup & Restore](BACKUP-RESTORE.md).

## Release ZIP — quick all-at-once method

The following is the **tested v1.29 → v1.30 transition** used immediately before the initial public release. Future release documentation should update both version numbers to match the actual old/new release.

If `video-destim-terminal-v1.30.zip` is already in your home directory, this entire command can be pasted in one shot:

```bash
cd ~ && unzip -q ~/video-destim-terminal-v1.30.zip -d ~ && cp ~/video-destim-terminal-v1.29/.env ~/video-destim-terminal-v1.30/.env && cd ~/video-destim-terminal-v1.29 && docker compose down && cp -a ~/video-destim-terminal-v1.29/data/. ~/video-destim-terminal-v1.30/data/ && cd ~/video-destim-terminal-v1.30 && docker compose up -d --build && docker compose ps && curl http://127.0.0.1:8790/health
```

Why `&&`? Each dependent step runs only if the preceding step succeeds. If unzip/copy/shutdown/build fails, later steps do not blindly continue.

The old container is stopped **before the `data/` copy** so the SQLite database is at rest.

## Release ZIP — one command at a time / mobile SSH

Use this form when you want to inspect every step separately or your SSH client is easier to use with one physical command per paste.

### 1. Unpack the new release

```bash
unzip -q ~/video-destim-terminal-v1.30.zip -d ~
```

### 2. Copy the existing environment file

```bash
cp ~/video-destim-terminal-v1.29/.env ~/video-destim-terminal-v1.30/.env
```

### 3. Stop the old release before copying its data

```bash
cd ~/video-destim-terminal-v1.29 && docker compose down
```

### 4. Copy local VDT data

```bash
cp -a ~/video-destim-terminal-v1.29/data/. ~/video-destim-terminal-v1.30/data/
```

### 5. Build/start the new release

```bash
cd ~/video-destim-terminal-v1.30 && docker compose up -d --build
```

### 6. Verify the container

```bash
docker compose ps
```

### 7. Verify VDT

```bash
curl http://127.0.0.1:8790/health
```

For v1.30:

```json
{"appVersion":"v1.30","ok":true,"youtubeConfigured":true}
```

## Why the previous folder is left intact

A versioned release-ZIP install gives you an easy rollback point. The update process copies data **into** the new folder rather than repurposing/deleting the previous release folder.

Do not delete the old folder until you are satisfied with the new release and have a backup strategy.

## Existing Tailscale Serve / reverse proxy

If your access layer already forwards to:

```text
127.0.0.1:8790
```

it normally does not need to be reconfigured after a VDT release update.

## Roll back to the previous release ZIP

Stop the new release:

```bash
cd ~/video-destim-terminal-v1.30 && docker compose down
```

Start the previous release:

```bash
cd ~/video-destim-terminal-v1.29 && docker compose up -d --build
```

Verify:

```bash
curl http://127.0.0.1:8790/health
```

The old folder still contains the database snapshot from immediately before the upgrade. Activity created only while running the newer release will not exist in that older copy.

If a future release documents a database migration that is not backward compatible, follow that release's migration/rollback notes instead of assuming an older build can read a newer database.

## Git-clone installations

For a Git installation, first back up `.env` and `data/`. Then from the repository directory:

```bash
git status
```

Confirm your local private files are not tracked, then:

```bash
git pull --ff-only
```

Rebuild/restart:

```bash
docker compose up -d --build
```

Verify:

```bash
curl http://127.0.0.1:8790/health
```

For a major or migration-bearing release, read the release-specific notes before pulling.
