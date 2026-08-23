# Installation

Video Destim Terminal supports two installation paths:

- **Path A:** Docker Engine + Docker Compose are already installed.
- **Path B:** a blank Ubuntu Server install that still needs Docker prerequisites.

The application itself is the same either way.

## Path A — Docker and Compose already installed

Verify:

```bash
docker --version
docker compose version
```

If both work for your normal user, skip to **Get Video Destim Terminal**.

---

## Path B — Blank Ubuntu server

These steps follow Docker's official Ubuntu APT-repository method. Docker's installation guidance can change, so the authoritative source is:

https://docs.docker.com/engine/install/ubuntu/

### 1. Install base packages

```bash
sudo apt update
sudo apt install -y ca-certificates curl git unzip
```

### 2. Add Docker's signing key

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### 3. Add Docker's Ubuntu repository

```bash
. /etc/os-release && printf 'Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: %s
Components: stable
Architectures: %s
Signed-By: /etc/apt/keyrings/docker.asc
' "${UBUNTU_CODENAME:-$VERSION_CODENAME}" "$(dpkg --print-architecture)" | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
```

### 4. Install Docker Engine + Compose

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify Docker itself:

```bash
sudo docker run --rm hello-world
```

### 5. Allow your normal user to run Docker

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in before continuing. Then verify without `sudo`:

```bash
docker --version
docker compose version
```

> Membership in the `docker` group effectively grants root-level control of the Docker host. Only add trusted local users.

---

## Get Video Destim Terminal

### Option 1 — Clone the Git repository

On the GitHub repository page, choose **Code**, copy the HTTPS clone URL, then run:

```bash
git clone <repository-url>
cd video-destim-terminal
```

### Option 2 — Download a release ZIP

Place the release ZIP in your current/home directory, then:

```bash
unzip video-destim-terminal-v1.30.zip
cd video-destim-terminal-v1.30
```

Release ZIP installs are intentionally versioned by folder so an old release can remain available for rollback.

## Configure VDT

The recommended no-editor setup is:

```bash
bash setup.sh
```

Enter your YouTube Data API key and choose a four-digit override PIN when prompted. The helper stores them in `.env` using hidden terminal input and does not start Docker automatically.

If you still need to create/restrict an API key—or want the full setup-helper, security, and quota explanation—see [YouTube API Setup](YOUTUBE-API-SETUP.md).

### Manual alternative

If you prefer to manage `.env` yourself:

```bash
cp .env.example .env
```

Set your own `YOUTUBE_API_KEY` and four-digit `OVERRIDE_PIN`, then protect the file:

```bash
chmod 600 .env
```

Do not leave the intentionally invalid `CHOOSE_4_DIGITS` placeholder from `.env.example` unchanged.

## Start VDT

```bash
docker compose up -d --build
```

Check container state:

```bash
docker compose ps
```

The service should become `healthy` after startup.

## Verify health

```bash
curl http://127.0.0.1:8790/health
```

Expected result for this release:

```json
{"appVersion":"v1.30","ok":true,"youtubeConfigured":true}
```

If the health check is wrong or the container exits, see [Troubleshooting](TROUBLESHOOTING.md).

## Secure access from another device

VDT binds to `127.0.0.1:8790` by default because it does not have a login system. Keep that safe default unless you intentionally configure another access layer.

For Tailscale Serve, authenticated HTTPS reverse proxies, localhost-only use, or temporary private-LAN testing, follow [Networking & HTTPS](NETWORKING.md).

## First launch

The first browser/device that opens VDT sees a legal/privacy acknowledgement. After accepting, review `CONFIG`, add at least one creator under `AVAILABLE CREATORS`, and return home to `REQUEST A WATCH`.

See [Configuration](CONFIGURATION.md) for the settings reference and [Terminal Commands](COMMANDS.md) for navigation/utility commands.

## Normal container controls

Stop without removing the container:

```bash
docker compose stop
```

Start it again:

```bash
docker compose start
```

Rebuild/recreate after a code or `.env` change:

```bash
docker compose up -d --build
```

Remove the running container/network without deleting local instance data:

```bash
docker compose down
```

Your persistent VDT data remains under `./data/` unless you explicitly delete it.

## Next steps

- [YouTube API Setup & Quota](YOUTUBE-API-SETUP.md)
- [Configuration](CONFIGURATION.md)
- [Networking & HTTPS](NETWORKING.md)
- [Backup & Restore](BACKUP-RESTORE.md)
- [Updating](UPDATING.md)
- [Troubleshooting](TROUBLESHOOTING.md)
