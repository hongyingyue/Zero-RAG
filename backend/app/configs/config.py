from pathlib import Path
from typing import Final

APP_ID: Final[str] = "4D4D2CAB-E810-4897-9558-F20E77445DD5"
APP_NAME: Final[str] = "agentic-rag"

ROOT_DIR: Final[Path] = Path(__file__).parent.parent.parent
LOGGING_CONFIG_PATH: Final[Path] = ROOT_DIR / "logging.yaml"
