# Networking & HTTPS

VDT does not have user authentication. The safest default is therefore:

```text
VIDEO_DESTIM_BIND=127.0.0.1
VIDEO_DESTIM_PORT=8790
```

Do **not** expose port `8790` directly to the public internet.

## Option A — Localhost only

Leave the defaults unchanged and use VDT only from the host itself.

## Option B — Tailscale Serve (recommended for personal remote access)

Tailscale Serve can place HTTPS in front of the localhost-only VDT service and make it available only to devices/users allowed by your tailnet.

Authoritative docs:

- Linux install: https://tailscale.com/docs/install/linux
- Tailscale Serve: https://tailscale.com/docs/features/tailscale-serve
- Serve CLI: https://tailscale.com/docs/reference/tailscale-cli/serve

### If Tailscale is already installed and authenticated

Skip to **Enable Serve**.

### Blank Ubuntu host: install Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

If you prefer not to use `curl | sh`, use Tailscale's current distribution-specific package instructions from the official Linux install page instead.

Join your tailnet:

```bash
sudo tailscale up
```

Open the authentication URL printed by Tailscale, approve the machine, then confirm:

```bash
tailscale status
```

### Enable Serve

With VDT running on localhost port 8790:

```bash
sudo tailscale serve --bg 8790
```

Inspect the result:

```bash
tailscale serve status
```

Tailscale prints the private HTTPS `*.ts.net` address for the node. Access remains subject to your tailnet access rules.

### Remove the Serve configuration

```bash
sudo tailscale serve reset
```

### Serve vs Funnel

Use **Serve** for private tailnet access.

Do not substitute **Funnel** unless you intentionally want an internet-public service. VDT is designed to remain private by default.

## Option C — HTTPS reverse proxy

Caddy, Traefik, nginx, or another reverse proxy can terminate TLS and forward to:

```text
http://127.0.0.1:8790
```

If anyone other than the intended operator can reach the proxy, add real authentication/access control at the proxy layer. VDT's override PIN is not a login system.

Keep VDT's own Docker binding on localhost unless you have a specific network design that requires otherwise.

## Direct private-LAN testing

For temporary testing on a trusted private LAN, you can set:

```text
VIDEO_DESTIM_BIND=0.0.0.0
```

Then rebuild/restart:

```bash
docker compose up -d --build
```

This exposes port 8790 on the host's network interfaces and is less safe than localhost + VPN/reverse proxy. Return the bind value to `127.0.0.1` when finished.

## Existing Tailscale Serve after a VDT update

If an existing Serve configuration already targets local port `8790`, normal VDT release updates do not require re-running `tailscale serve` as long as the new version continues to listen on the same host/port.

## Troubleshooting

Check VDT locally first:

```bash
curl http://127.0.0.1:8790/health
```

Then check Tailscale:

```bash
tailscale status
tailscale serve status
```

If local health works but remote HTTPS does not, the problem is in the network/Serve/reverse-proxy layer rather than the VDT container itself.
