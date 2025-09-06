import sys
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any


def setup_logger(
    app_name: str = "rag-app",
    log_level: str = "INFO",
    log_dir: str = "./logs",
    enable_console: bool = True,
    enable_file_rotation: bool = True,
    max_file_size: str = "10 MB",
    retention: str = "30 days",
    compression: str = "gz",
    json_logs: bool = False,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Simple Loguru logger setup.
    """
    # Remove default logger
    logger.remove()

    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Console handler
    if enable_console:
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout,
            level=log_level.upper(),
            format=console_format,
            colorize=not json_logs,
            serialize=json_logs,
            backtrace=True,
            diagnose=True,
            extra=extra_fields or {},
        )

    # File handler with rotation
    if enable_file_rotation:
        log_file = log_path / f"{app_name}.log"
        logger.add(
            str(log_file),
            level=log_level.upper(),
            rotation=max_file_size,
            retention=retention,
            compression=compression,
            serialize=json_logs,
            backtrace=True,
            diagnose=True,
            extra=extra_fields or {},
        )

        error_log_file = log_path / f"{app_name}_errors.log"
        logger.add(
            str(error_log_file),
            level="ERROR",
            rotation=max_file_size,
            retention=retention,
            compression=compression,
            serialize=json_logs,
            backtrace=True,
            diagnose=True,
            extra=extra_fields or {},
        )

    logger.info(f"Logger initialized for {app_name} at {log_path.absolute()}")


if __name__ == "__main__":
    setup_logger(app_name="demo", log_level="DEBUG")

    logger.debug("This is a debug message")
    logger.info("Application started successfully")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
