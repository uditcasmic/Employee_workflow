from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Workflow Engine", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(default="sqlite:///./workflow_engine.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    first_superuser_email: str = Field(default="admin@example.com", alias="FIRST_SUPERUSER_EMAIL")
    first_superuser_password: str = Field(default="admin12345", alias="FIRST_SUPERUSER_PASSWORD")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")
    bootstrap_admin_user: bool = Field(default=True, alias="BOOTSTRAP_ADMIN_USER")
    celery_task_always_eager: bool = Field(default=False, alias="CELERY_TASK_ALWAYS_EAGER")


settings = Settings()
