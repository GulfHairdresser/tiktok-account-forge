# Security Policy

## Scope

`tiktok-account-forge` is a local Windows desktop tool. It does not run a
server, does not phone home, and does not ship telemetry. Everything it
talks to is either TikTok's public web endpoints or a proxy you configured
yourself.

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.7.x   | yes       |
| 0.6.x   | security fixes only |
| < 0.6   | no        |

## Reporting a vulnerability

Email `security@forge-lab.sh` with subject `[forge] <one-line summary>`.
Include:

- Forge version (`forge --version`)
- Windows build (`winver`)
- Minimal reproduction (config + command)
- Redacted log excerpt

We aim to acknowledge within 72 hours. Please do not open a public issue
for anything that leaks cookies, proxy credentials, or session tokens.

## Handling of secrets

- Proxy credentials live in `.env` (gitignored) or the Windows Credential
  Manager via `forge/proxy/vault.py`.
- Session cookies are written to `sessions/<uuid>.json` in plaintext.
  Treat that directory as sensitive. Do not commit it.
- Captcha provider keys go in `captcha_keys.json` (gitignored).

## Known limitations

- The fingerprint cache at `fingerprints.cache` is unencrypted.
- Debug logs may include request bodies at `TRACE` level. Do not share
  `TRACE` logs publicly.