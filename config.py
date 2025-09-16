from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    TIDB_HOST: str =''
    TIDB_PORT: int = 4000
    TIDB_USER: str =''
    TIDB_PASS: str =''
    TIDB_CA: str =""
    TIDB_DB: str = ""
    LLM_PROVIDER: str="Gemini"
    GEMINI_API_KEY: str =""
    OPENAI_MODEL: str = ".env."
    OPENAI_API_KEY: str = ".env"
    OLLAMA_HOST: str = "http://localhost:11434"
    SLACK_WEBHOOK: str =".env"

    JIRA_BASE_URL: str =""
    JIRA_EMAIL: str=""
    JIRA_API_TOKEN: str=""
    JIRA_PROJECT_KEY: str=""

    class Config:
        env_file = ".env"

settings = Settings()
