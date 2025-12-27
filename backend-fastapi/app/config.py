from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ---- Anthropic Claude / LLM ----
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5
    use_claude: bool = True

    # ---- app/runtime ----
    db_url: str = "sqlite:///./app.db"
    storage_dir: str = "./local_storage"
    allow_origins: str = "http://localhost:5173"

    # pydantic v2 settings
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",            # ignore any other unknown env keys
    )

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.allow_origins.split(",") if o.strip()]

settings = Settings()
