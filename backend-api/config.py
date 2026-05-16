from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Echo-Weave Backend"
    # Placeholder for API keys
    # openai_api_key: str = ""
    # elevenlabs_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
