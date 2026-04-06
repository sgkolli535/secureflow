from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # GitHub
    github_token: str = ""
    github_owner: str = ""
    github_repo: str = ""
    github_webhook_secret: str = ""

    # Devin
    devin_api_key: str = ""
    devin_base_url: str = "https://api.devin.ai/v1"
    devin_playbook_id: str = ""

    # Slack
    slack_webhook_url: str = ""
    slack_enabled: bool = False

    # Pipeline
    poll_interval_seconds: int = 30
    max_concurrent_sessions: int = 3
    session_timeout_minutes: int = 60
    confidence_threshold: float = 0.7

    # Database
    database_url: str = "sqlite:///secureflow.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
