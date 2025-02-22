
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_env: Optional[str] = os.environ["APP_ENV"]
    service_name: str
    otlp_grpc_endpoint: str
    otlp_http_endpoint: str
    inventory_service_url: str

    class Config:
        app_env = os.environ["APP_ENV"]
        env_file = os.getenv("ENV_FILE", f"app/core/{app_env}.env")


settings = Settings()


