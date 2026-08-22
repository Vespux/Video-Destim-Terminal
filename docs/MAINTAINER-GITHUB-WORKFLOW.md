# Maintainer GitHub Publishing Workflow

This guide is for publishing the prepared VDT source without accidentally uploading a private self-hosted instance.

## Initial public release

The initial GitHub release is **v1.30**.

Recommended repository name:

```text
video-destim-terminal
```

Suggested description:

```text
A self-hosted, low-stimulation interface for intentional video selection.
```

Suggested topics (optional):

```text
self-hosted  youtube-api  docker  digital-wellbeing  minimal-ui
```

## Release artifact status

The canonical initial release artifact is `video-destim-terminal-v1.30.zip`. Any earlier v1.30 ZIP used during private VM testing should be treated as superseded by the final sanitized/publication package.

Before publishing, compute a SHA-256 checksum of the exact asset you intend to upload and keep that checksum with the release notes or alongside the asset.

## 1. Start from the prepared release source

Use the clean release folder/ZIP created for GitHub. Do **not** initialize Git from the directory of a live personal instance unless you have independently sanitized it.

A public source tree should include:

```text
.env.example
.github/
data/.gitkeep
docs/
app.py
index.html
compose.yaml
Dockerfile
requirements.txt
setup.sh
README.md
LICENSE
PRIVACY.md
TERMS.md
SECURITY.md
COMPLIANCE.md
CONTRIBUTING.md
CHANGELOG.md
favicon/icon/manifest assets
```

It should **not** include:

```text
.env
data/video-destim-terminal.db
*.db
*.db-wal
*.db-shm
*.sqlite*
__pycache__/
*.pyc
private backups
exports
release ZIPs nested inside the repository
private SSH config
private IPs/hostnames copied from your environment
real API keys/PINs/tokens
```

## 2. Run a pre-publication sanity check

From the release source folder:

```bash
find . -type f -print | sort
```

Validate the guided setup helper syntax:

```bash
bash -n setup.sh
```

Look specifically for ignored/private file types:

```bash
find . -type f \( -name '.env' -o -name '*.db' -o -name '*.db-*' -o -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.pyc' -o -name '*.zip' \) -print
```

That command should print nothing in the clean repository source tree.

Search for common secret/private deployment artifacts before first push:

```bash
grep -RInE 'AIza[0-9A-Za-z_-]{20,}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|192\.168\.|10\.[0-9]+\.|172\.(1[6-9]|2[0-9]|3[01])\.|\.ts\.net|password[[:space:]]*=|token[[:space:]]*=' . --exclude-dir=.git --exclude='*.png' || true
```

Review every match. Some documentation can legitimately contain words such as `token`, but a real credential/private hostname must not be present.

## 3. Create the GitHub repository

### GitHub web interface

1. Sign in to GitHub.
2. Choose **New repository**.
3. Name it `video-destim-terminal`.
4. Add the description above if desired.
5. Choose **Public**.
6. Do **not** auto-create a second README/license/gitignore if you are uploading the prepared source as-is.
7. Create the repository.
8. Upload the **contents** of the prepared release folder, preserving `.github/`, `docs/`, and `data/.gitkeep`.
9. Commit with a message such as `Release v1.30`.

### Git command line

From the prepared source folder:

```bash
git init
git add .
git status
```

**Stop and inspect `git status` before committing.** `.env`, databases, backups, and ZIPs must not appear.

Then:

```bash
git commit -m "Release v1.30"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

## 4. Inspect the public repository as a stranger

Before announcing it, open the repository in a private/incognito browser window and verify:

- README renders correctly;
- docs links work;
- `.env.example` contains no real secret;
- `setup.sh` is present and contains no hard-coded API key/PIN;
- no `.env` exists;
- `data/` contains only `.gitkeep`;
- no private hostname/IP appears;
- issue templates are present;
- license/privacy/terms/security/compliance files are visible.

## 5. Create GitHub Release v1.30

1. Open **Releases** → **Draft a new release**.
2. Create tag `v1.30` from `main`.
3. Release title: `Video Destim Terminal v1.30`.
4. Use the v1.30 section of `CHANGELOG.md` as the release notes, trimming internal/pre-release detail if desired.
5. Attach the clean `video-destim-terminal-v1.30.zip` release asset if you want users to follow the release-ZIP installation path.
6. Publish.

GitHub will also generate its own source archives for the tag.

## 6. Post-publication clean-room check

For the strongest final sanity check, clone/download the **public** repository/release into a fresh directory or fresh VM and follow the public installation documentation exactly.

Confirm the guided configuration path first:

```bash
bash setup.sh
```

Then confirm:

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8790/health
```

Then test:

- first-run legal acknowledgement;
- creator add;
- Request a Watch;
- Config save/cancel/unsaved-change prompts;
- Reorder Creators save/cancel/unsaved-change prompts;
- `COMMAND DOC` and clickable commands;
- `support` confirmation;
- `export-data` excludes API key/PIN;
- `delete-data` confirmation;
- favicon/mobile layout;
- Tailscale Serve/reverse-proxy access if documented for the test environment.

## 7. Recommended repository settings

- Enable Issues if you want public bug reports/feature requests.
- Enable Private Vulnerability Reporting / Security Advisories if available.
- Enable Dependabot alerts if desired.
- Protect `main` once outside contributors begin submitting pull requests.
- Consider GitHub Discussions later if usage/support volume warrants it.

## Before every future release

1. Develop/test the change.
2. Update app/UI/manifest version references.
3. Update `CHANGELOG.md` and affected docs.
4. Backward-compatibility review for the SQLite schema/update path.
5. Run syntax/build/health checks.
6. Run the secret/private-data audit again.
7. Re-review current YouTube API Terms/Developer Policies/Branding/Revision History.
8. Build the clean versioned release ZIP.
9. Inspect ZIP contents before upload.
10. Commit/push/tag/publish the matching GitHub Release.

YouTube API policy is external to VDT and can change even when the application code does not.
