# Architecture

```
forge/
├── bootstrap/      entry points, CLI, config load
├── core/           account engine + state machine
├── handlers/       per-step feature handlers
├── services/       external I/O (tiktok, proxy, captcha, mail)
├── fingerprint/    device + browser fingerprint generation
├── proxy/          proxy pool, health, vault
├── models/         pydantic domain models
├── utils/          logging, retry, crypto, io helpers
└── gui/            optional Tkinter launcher
```

## Layers

**Bootstrap.** `forge.bootstrap.cli` parses args, loads settings via
`pydantic-settings`, initializes logging, then hands a `ForgeConfig` to
`AccountEngine`. Nothing in `bootstrap/` contains business logic.

**Core.** `AccountEngine` is an async state machine. Each account moves
through states: `QUEUED → FINGERPRINTING → PROXYING → REGISTERING →
VERIFYING → WARMING → EXPORTED`. Handlers subscribe to state transitions
and are invoked by the engine. The engine owns retries, concurrency
(semaphore-bounded), and persistence.

**Handlers.** One handler per step. Handlers are pure-ish: they receive a
`ForgeContext` and mutate only the `Account` they were given. Side effects
go through `services/`.

**Services.** `TikTokClient` wraps the HTTP session and Playwright browser.
`ProxyService` rotates and health-checks the pool. `CaptchaService` talks
to a solver. `MailService` provisions inboxes for verification.

**Models.** Pydantic v2 models. `Account`, `Fingerprint`, `Proxy`,
`ForgeConfig`, `RunReport`. Serialized to `forge_state/accounts.sqlite3`.

## Concurrency

Default concurrency is 4. Each concurrent account gets its own Playwright
context and its own proxy binding. The engine holds a single
`asyncio.Semaphore` sized by `config.concurrency`.

## Persistence

SQLite at `forge_state/accounts.sqlite3`. Schema is created on first run
and migrated forward via `forge/core/migrations.py`. Sessions are written
as JSON under `sessions/`.

## Failure model

Handlers raise `ForgeStepError` for retryable failures and
`ForgeFatalError` for terminal ones. The engine applies a `tenacity`
retry policy: 3 attempts, exponential backoff 2s→8s, jitter on. Fatal
errors park the account in `FAILED` and continue the batch.