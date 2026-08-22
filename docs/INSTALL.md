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
. /etc/os-release && printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n' "${UBUNTU_CODENAME:-$VERSION_CODENAME}" "$(dpkg --print-architecture)" | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
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

## Configure the YouTube API key and override PIN

### Recommended — guided SSH setup

Run:

```bash
bash setup.sh
```

The helper prompts for:

```text
ENTER YOUTUBE API KEY:
CHOOSE OVERRIDE PIN:
```

Both values are hidden while you enter them. The helper:

- requires a non-empty YouTube API key;
- rejects API-key input containing whitespace;
- requires the override PIN to be exactly four digits;
- writes the values to `.env` without printing them back to the terminal;
- preserves the other settings already present in `.env`;
- applies `chmod 600 .env`;
- does **not** start Docker automatically.

If `.env` already exists, `setup.sh` asks before updating the stored API key and PIN. Choosing No leaves the file unchanged.

The override PIN only bypasses VDT's request cooldown. It is not login/authentication.

### Manual alternative

If you prefer to edit the environment file yourself:

```bash
cp .env.example .env
```

Open `.env` in your preferred editor and set both required values:

```text
YOUTUBE_API_KEY=<your own YouTube Data API v3 key>
OVERRIDE_PIN=<your own four-digit PIN>
```

**CHOOSE OVERRIDE PIN:** do not leave the placeholder from `.env.example` unchanged.

Then protect the environment file:

```bash
chmod 600 .env
```

See [YouTube API Setup](YOUTUBE-API-SETUP.md) for key creation/restriction guidance.

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

If `youtubeConfigured` is false, rerun `bash setup.sh` or re-check `.env`. If the container exits, verify `OVERRIDE_PIN` is exactly four digits.

## Secure access from another device

The default Compose file binds to:

```text
127.0.0.1:8790
```

That means VDT is not directly reachable from other machines. This is intentional because VDT has no login system.

For phone/remote access, see [Networking & HTTPS](NETWORKING.md). The guide includes:

- Tailscale already installed;
- blank-Ubuntu Tailscale installation;
- Tailscale Serve;
- authenticated HTTPS reverse-proxy guidance;
- temporary private-LAN testing.

## First launch

The first browser/device that opens VDT sees a legal/privacy acknowledgement before the main interface.

After accepting:

1. Open `CONFIG`.
2. Review the defaults.
3. Open `AVAILABLE CREATORS`.
4. Add a creator using a supported YouTube `@handle`, `/channel/`, or legacy `/user/` URL.
5. Return home.
6. Choose `REQUEST A WATCH`.

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

- [Configuration](CONFIGURATION.md)
- [Networking & HTTPS](NETWORKING.md)
- [Backup & Restore](BACKUP-RESTORE.md)
- [Terminal Commands](COMMANDS.md)
- [Troubleshooting](TROUBLESHOOTING.md)
