from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ---- Anthropic / LLM ----
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20240620"  # pin to a real model id
    use_claude_real: bool = False
    prompt_cache_ttl_seconds: Optional[int] = None  # NEW: if set, we cache the long prompt

    # ---- app/runtime ----
    db_url: str = "sqlite:///./app.db"
    storage_dir: str = "./local_storage"
    storage_backend: str = "local"  # "local" or "s3"
    s3_bucket_name: str = "med-docs-dev"
    aws_region: str = "ap-south-1"
    allow_origins: str = "http://localhost:5173"

    # pydantic v2 settings
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",            # NEW: ignore any other unknown env keys
    )

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.allow_origins.split(",") if o.strip()]

settings = Settings()
