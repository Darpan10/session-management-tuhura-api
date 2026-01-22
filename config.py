from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Session Management API"
    debug: bool = True

    #secret key
    secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # Database settings
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    #mailgun settings
    mailgun_api_key: str
    mailgun_domain: str
    mailgun_base_url: str

    # Google Maps API
    google_maps_api_key: str

    # Logging
    log_level: str


    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings()
