from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml


def configure_logging(config_path: Path | None = None, log_path: Path | None = None) -> None:
    """Apply YAML logging config if present, then optionally add a file handler."""

    if config_path and config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )

    if log_path:
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
