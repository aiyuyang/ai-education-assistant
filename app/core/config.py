"""
Core configuration module for AI Education Assistant
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings"""
    
    # Application
    app_name: str = "AI Education Assistant"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "mysql+pymysql://root:password@localhost:3306/ai_education_assistant"
    database_host: str = "localhost"
    database_port: int = 3306
    database_name: str = "ai_education_assistant"
    database_user: str = "root"
    database_password: str = "password"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # External AI Service (Gemini)
    gemini_api_key: str = "AIzaSyCDOFb2I_-8CgYirI5df3Nyf-xzA7tHEGE"
    gemini_model: str = "gemini-2.5-flash"
    
    # Legacy OpenAI settings (kept for compatibility)
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:7791"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    cors_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/gif", "text/plain"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    
    def __init__(self):
        # Load from environment variables
        self.app_name = os.getenv("APP_NAME", self.app_name)
        self.app_version = os.getenv("APP_VERSION", self.app_version)
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        
        # Database
        self.database_host = os.getenv("MYSQL_HOST", self.database_host)
        self.database_port = int(os.getenv("MYSQL_PORT", self.database_port))
        self.database_name = os.getenv("MYSQL_DB", self.database_name)
        self.database_user = os.getenv("MYSQL_USER", self.database_user)
        self.database_password = os.getenv("MYSQL_PASSWORD", self.database_password)
        self.database_url = f"mysql+pymysql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        
        # Redis
        self.redis_host = os.getenv("REDIS_HOST", self.redis_host)
        self.redis_port = int(os.getenv("REDIS_PORT", self.redis_port))
        self.redis_db = int(os.getenv("REDIS_DB", self.redis_db))
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        
        # JWT
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("ALGORITHM", self.algorithm)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", self.access_token_expire_minutes))
        
        # External AI Service (Gemini)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)
        self.gemini_model = os.getenv("GEMINI_MODEL", self.gemini_model)
        
        # Legacy OpenAI settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", self.openai_base_url)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        
        # CORS
        cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080,http://localhost:7791")
        self.cors_origins = cors_origins_env.split(",") if cors_origins_env else self.cors_origins
        
        cors_methods_env = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,PATCH")
        self.cors_methods = cors_methods_env.split(",") if cors_methods_env else self.cors_methods
        
        cors_headers_env = os.getenv("CORS_HEADERS", "*")
        self.cors_headers = cors_headers_env.split(",") if cors_headers_env else self.cors_headers


# Global settings instance
settings = Settings()
