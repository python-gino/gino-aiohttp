import os

from sqlalchemy.engine.url import URL

DB_DRIVER = os.getenv("DB_DRIVER", "postgresql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DATABASE = os.getenv("DB_DATABASE", "postgres")
DB_DSN = URL(
    drivername=DB_DRIVER,
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_DATABASE,
)
DB_ECHO = os.getenv("DB_ECHO", "false").lower() in ("true", "yes", "1")
DB_POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", 1))
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", 16))
DB_SSL = os.getenv("DB_SSL", "false").lower() in ("true", "yes", "1")
DB_RETRY_LIMIT = int(os.getenv("DB_RETRY_LIMIT", 32))
DB_RETRY_INTERVAL = int(os.getenv("DB_RETRY_INTERVAL", 1))
DB_KWARGS = dict(map(lambda s: s.split("=", 1), os.getenv("DB_KWARGS", "").split()))
