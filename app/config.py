from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "llama3-8b-8192"
    embedding_model: str = "all-MiniLM-L6-v2"
    faiss_index_path: str = "indexes/faiss.index"
    metadata_path: str = "indexes/metadata.json"
    top_k: int = 10

    class Config:
        env_file = ".env"

settings = Settings()