# Security Policy

## Supported version

The current public release line begins at **v1.30**.

## Important: there is no login system

VDT is designed primarily as a personal self-hosted application.

The four-digit `OVERRIDE_PIN` only bypasses a configured request cooldown. It is **not authentication** and does not protect the application from other people who can reach it.

The public Compose file therefore binds to `127.0.0.1` by default.

Recommended access patterns:

- localhost only;
- Tailscale Serve/private VPN with HTTPS and appropriate tailnet access rules;
- an HTTPS reverse proxy that also provides real authentication/access control.

Do not expose port `8790` directly to the public internet.

## What someone with web access can do

Because there is no account/permission layer, anyone who can reach the unprotected interface can potentially:

- view creators/config/local request history/stats;
- change settings/creator lists;
- consume/eject credits;
- export local VDT data;
- trigger local data deletion after the application's confirmation prompts.

Network access control is therefore the primary security boundary.

## Secrets and private data

Never commit or publish:

- `.env`;
- YouTube API keys;
- real override PINs;
- SQLite databases or database sidecar files;
- exports/backups containing local history/configuration;
- private hostnames/IP addresses copied from your deployment logs or commands.

`.gitignore` reduces accidental commits, but you should still inspect `git status` before every push.

Recommended local permission for `.env`:

```bash
chmod 600 .env
```

## Browser/server security headers

The Flask app sets restrictive response headers including frame denial, content-type sniffing protection, a Content Security Policy, a permissions policy, and a strict-origin-when-cross-origin referrer policy.

These are defense-in-depth measures; they do not turn VDT into an authenticated public web application.

## Dependencies

VDT is built from a Python Alpine base image and installs Flask, Requests, and Gunicorn from `requirements.txt` within declared major-version ranges. Rebuild regularly when updating the project so security fixes in the base image/dependencies can be incorporated.

## Backups

Backups of `.env` and `data/` contain sensitive local configuration/history. Store them with permissions appropriate for private data.

See [docs/BACKUP-RESTORE.md](docs/BACKUP-RESTORE.md).

## Reporting a vulnerability

If GitHub Private Vulnerability Reporting is enabled for the public repository, use the repository's **Security** tab/private report flow.

Do not put API keys, database contents, private hostnames, or detailed exploit/private-instance information in a public issue. If no private reporting channel is available, open only a minimal public issue asking the maintainer for a private contact method.
