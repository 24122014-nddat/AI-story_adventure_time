from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    app_name: str = "AI Story Adventure Backend"
    debug: bool = True

    text_provider: str = os.getenv("TEXT_PROVIDER", "groq")
    text_model: str = os.getenv("TEXT_MODEL", "openai/gpt-oss-120b")
    save_dir: str = os.getenv("SAVE_DIR", "saves")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    xai_base_url: str = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")

    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Image generation settings
    image_provider: str = os.getenv("IMAGE_PROVIDER", "kaggle")
    kaggle_api_url: str = os.getenv(
        "KAGGLE_API_URL",
        "https://onion-vertical-squash.ngrok-free.dev",
    )


settings = Settings()