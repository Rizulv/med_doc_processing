from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-latest"
    prompt_cache_ttl_seconds: int = 3600
    db_url: str = "sqlite:///./app.db"
    allow_origins: str = "http://localhost:5173"
    use_claude_real: bool = False
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allow_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
