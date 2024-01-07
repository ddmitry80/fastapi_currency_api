# from pydantic_settings import BaseSettings
# from core.config import Settings
from app.core.config import Settings


class AuthConfig(Settings):
    # class Config:
    #     env_file = '.env'
    #     env_file_encoding = 'utf-8'
    #     extra = 'ignore'
        
    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 5  # minutes

    REFRESH_TOKEN_KEY: str = "refreshToken"
    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days

    SECURE_COOKIES: bool = True


auth_config = AuthConfig()