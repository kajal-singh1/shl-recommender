from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "llama-3.1-8b-instant"
    embedding_model: str = "all-MiniLM-L6-v2"
    faiss_index_path: str = "indexes/faiss.index"
    metadata_path: str = "indexes/metadata.json"
    top_k: int = 10

    model_config = {"env_file": ".env", "protected_namespaces": ("settings_",)}

settings = Settings()