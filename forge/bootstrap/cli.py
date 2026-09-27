"""Command-line entry point for the forge.

Loads configuration, initializes logging, and dispatches to the
`AccountEngine`. This module owns no business logic — it only wires the
process together and translates CLI flags into a `ForgeConfig`.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console

from forge import __version__
from forge.bootstrap.settings import load_config
from forge.core.engine import AccountEngine
from forge.utils.logging import setup_logging

app = typer.Typer(
    name="forge",
    help="Batch TikTok account provisioning for Windows desktops.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def run(
    config: Path = typer.Option(Path("forge.toml"), "--config", "-c"),
    count: int = typer.Option(10, "--count", "-n", min=1, max=5000),
    concurrency: int = typer.Option(4, "--concurrency", "-j", min=1, max=32),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Provision `count` accounts using the given config."""
    setup_logging()
    cfg = load_config(config).model_copy(
        update={"target_count": count, "concurrency": concurrency, "dry_run": dry_run}
    )
    logger.info("forge {} starting — target={} concurrency={}", __version__, count, concurrency)
    engine = AccountEngine(cfg)
    report = asyncio.run(engine.run_batch())
    console.print(report.summary_line())
    sys.exit(0 if report.failed == 0 else 2)


@app.command()
def version() -> None:
    """Print the forge version."""
    console.print(f"tiktok-account-forge {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()