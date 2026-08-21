# Backup & Restore

The two important local items are:

```text
.env
data/
```

`data/` contains the SQLite database. `.env` contains the YouTube API key and override PIN.

Treat both as private.

## Simple consistent backup

Stop the app so SQLite is at rest:

```bash
docker compose stop
```

Create a timestamped backup directory:

```bash
BACKUP_DIR="backups/vdt-$(date +%Y%m%d-%H%M%S)" && mkdir -p "$BACKUP_DIR"
```

Copy the private environment file and the entire persistent-data directory:

```bash
cp -a .env data "$BACKUP_DIR"/
```

Restrict the backup directory:

```bash
chmod -R go-rwx "$BACKUP_DIR"
```

Restart VDT:

```bash
docker compose start
```

Copy the resulting backup somewhere appropriate for your own backup strategy. Do not publish it with the repository or attach it to a public issue.

## Restore

Stop VDT:

```bash
docker compose stop
```

Make a safety copy of the current `.env`/`data/` before overwriting them if needed.

Restore the known-good backup into the VDT project directory, preserving the names `.env` and `data/`, then:

```bash
chmod 600 .env
docker compose start
```

Verify:

```bash
curl http://127.0.0.1:8790/health
```

## Release-folder updates are also a rollback snapshot

When you update using [UPDATING.md](UPDATING.md), the previous versioned folder remains untouched after its data is copied to the new release. That gives you a convenient pre-upgrade snapshot in addition to any proper backup you created.

Do not treat this as your only backup: deleting the old folder would also delete that snapshot.

## Built-in `export-data`

`export-data` creates a readable JSON export of local VDT configuration/creator/history state and intentionally excludes the API key and override PIN.

It is useful for inspection/archival, but the stopped `data/` directory is the authoritative artifact for an exact full restore.
