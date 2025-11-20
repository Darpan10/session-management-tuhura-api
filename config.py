from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Session Management API"
    debug: bool = True


settings = Settings()