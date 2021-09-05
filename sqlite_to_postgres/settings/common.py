from logging import config

from pydantic import BaseSettings


class TargetDBSettings(BaseSettings):
    DSN: str = "postgresql://postgres:passwd@db:5432/movies"
    SCHEMA: str = "content"
    MIN_POOL_SIZE: int = 5
    MAX_POOL_SIZE: int = 10


class ETLSettings(BaseSettings):
    TARGET_DB = TargetDBSettings()
    SOURCE_DB_DSN: str = "db.sqlite"
    CHUNK_SIZE: int = 500

    class Config:
        env_prefix = "ETL_"


class CommonSettings(BaseSettings):
    ETL: ETLSettings = ETLSettings()

    logging_conf = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "__main__": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    config.dictConfig(logging_conf)
