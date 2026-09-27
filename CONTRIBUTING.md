# Contributing to tiktok-account-forge

Thanks for poking at the forge. This is a hobbyist Windows desktop tool for
batch TikTok account provisioning — device fingerprint rotation, proxy
binding, session warmup, and export. It is not affiliated with TikTok.

## Ground rules

- Read `docs/ARCHITECTURE.md` before touching `forge/core/`. The engine is a
  state machine; handlers only observe and mutate state through the
  `ForgeContext`.
- One PR = one concern. Fingerprint work stays in `forge/fingerprint/`.
  Proxy work stays in `forge/proxy/`. Don't cross the streams.
- New handlers go in `forge/handlers/` and register via
  `@register_handler("name")`. No monkey-patching the registry.
- Type hints required on all public callables. `mypy --strict` must pass.

## Dev setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
playwright install chromium
pytest -q
```

## Style

- `ruff format` and `ruff check --fix` before every commit.
- Loguru for logs, never `print`. Level `DEBUG` for noise, `INFO` for
  state transitions, `WARNING` for retries, `ERROR` for terminal failures.
- No bare `except`. Catch specific exceptions; log and re-raise or bubble
  into the retry policy.

## Reporting bugs

Open an issue with: forge version (`forge --version`), Windows build,
proxy provider, and the tail of `logs/forge.log`. Redact cookies and
`x-tt-token` headers before posting.

## Pull request checklist

- [ ] `pytest -q` green
- [ ] `ruff check` clean
- [ ] `mypy forge` clean
- [ ] Docs updated if a public interface changed
- [ ] No hardcoded credentials, keys, or proxy URIs