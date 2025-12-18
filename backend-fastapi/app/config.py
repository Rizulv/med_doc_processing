from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ---- Google Gemini / LLM ----
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"  # Free tier model
    use_gemini: bool = True

    # ---- app/runtime ----
    db_url: str = "sqlite:///./app.db"
    storage_dir: str = "./local_storage"
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
