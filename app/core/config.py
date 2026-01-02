from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = 'Mini Social Media Feed API'
    API_VERSION_1: str = '/api/v1'
    DESCRIPTION: str = 'A REST API for a social media feed for altschool project'

    DATABASE_URL: str

    class config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
