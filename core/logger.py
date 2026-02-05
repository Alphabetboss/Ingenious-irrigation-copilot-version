import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any


LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"


def _ensure_log_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def configure_root_logger(config: Dict[str, Any]) -> logging.Logger:
    system_cfg = config.get("system", {})
    logging_cfg = config.get("logging", {})

    log_level_str = system_cfg.get("log_level", "INFO").upper()
    level = getattr(logging, log_level_str, logging.INFO)

    log_dir = Path(logging_cfg.get("directory", "data/logs"))
    rotation_cfg = logging_cfg.get("rotation", {})
    rotation_enabled = rotation_cfg.get("enabled", True)
    max_size_mb = rotation_cfg.get("max_size_mb", 10)
    backup_count = rotation_cfg.get("backup_count", 5)

    _ensure_log_dir(log_dir)
    log_file = log_dir / "ingenious_irrigation.log"

    logger = logging.getLogger("ingenious_irrigation")
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler with rotation
    if rotation_enabled:
        fh = RotatingFileHandler(
            log_file,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
        )
    else:
        fh = logging.FileHandler(log_file)

    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Logger initialized. Level=%s, file=%s", log_level_str, log_file)
    return logger
