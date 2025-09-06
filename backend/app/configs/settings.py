import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8777
    WORKERS: int = 4
    RELOAD: bool = False
    ACCESS_LOG: bool = False

    # Streamlit Configuration
    STREAMLIT_HOST: str = "0.0.0.0"
    STREAMLIT_PORT: int = 8501
    STREAMLIT_SERVER_HEADLESS: bool = True
    STREAMLIT_SERVER_ENABLE_CORS: bool = True
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION: bool = False

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    API_TITLE: str = "QAnything API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "QAnything Knowledge Base API"

    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Application Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Optional[Path] = None
    STATIC_DIR: Optional[Path] = None
    UPLOAD_DIR: Optional[Path] = None
    LOG_DIR: Optional[Path] = None

    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"

    # QAnything Specific
    KNOWLEDGE_BASE_ROOT: Optional[Path] = None
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    SUPPORTED_FILE_TYPES: list = [".pdf", ".txt", ".md", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"]

    # Performance
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 300  # 5 minutes
    CHUNK_SIZE: int = 1024

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    TESTING: bool = False

    @validator("ROOT_DIR", pre=True, always=True)
    def set_root_dir(cls, v, values):
        if v is None:
            base_dir = values.get("BASE_DIR")
            return base_dir.parent.parent if base_dir else Path.cwd()
        return Path(v)

    @validator("STATIC_DIR", pre=True, always=True)
    def set_static_dir(cls, v, values):
        if v is None:
            root_dir = values.get("ROOT_DIR") or Path.cwd()
            return root_dir / "qanything_kernel" / "qanything_server" / "dist" / "qanything"
        return Path(v)

    @validator("UPLOAD_DIR", pre=True, always=True)
    def set_upload_dir(cls, v, values):
        if v is None:
            root_dir = values.get("ROOT_DIR") or Path.cwd()
            return root_dir / "uploads"
        return Path(v)

    @validator("LOG_DIR", pre=True, always=True)
    def set_log_dir(cls, v, values):
        if v is None:
            root_dir = values.get("ROOT_DIR") or Path.cwd()
            return root_dir / "logs"
        return Path(v)

    @validator("KNOWLEDGE_BASE_ROOT", pre=True, always=True)
    def set_kb_root(cls, v, values):
        if v is None:
            root_dir = values.get("ROOT_DIR") or Path.cwd()
            return root_dir / "knowledge_bases"
        return Path(v)

    @validator("DEBUG", pre=True, always=True)
    def set_debug_mode(cls, v, values):
        env = values.get("ENVIRONMENT", "development")
        return env.lower() in ["development", "dev", "debug"]

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [self.UPLOAD_DIR, self.LOG_DIR, self.KNOWLEDGE_BASE_ROOT]

        for directory in directories:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.create_directories()
    return settings


# For backward compatibility and easy imports
settings = get_settings()

# Export commonly used paths
BASE_DIR = settings.BASE_DIR
ROOT_DIR = settings.ROOT_DIR
STATIC_DIR = settings.STATIC_DIR
UPLOAD_DIR = settings.UPLOAD_DIR
LOG_DIR = settings.LOG_DIR
