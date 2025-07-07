from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application configuration using Pydantic.
    It reads settings from environment variables.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Microservice URLs
    # These should point to the other running services.
    # The default values are suitable for a local Docker Compose setup.
    PROMPT_PARSER_URL: str = "http://prompt-parser:8000/api/v1/parse"
    STYLE_ANALYSIS_URL: str = "http://style-analysis:8000/analyze/"
    SOUND_GENERATION_URL: str = "http://sound-generation:8000/generate"
    MIXING_MASTERING_URL: str = "http://mixing-mastering:8000/process"


# Create a single instance of the settings to be used throughout the application
settings = Settings()
