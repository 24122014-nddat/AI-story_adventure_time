from __future__ import annotations

from app.ai.providers.kaggle_provider import KaggleProvider
from app.config import settings
from app.services.game_service import GameService
from app.services.image_service import ImageService


def get_game_service() -> GameService:
    try:
        return GameService()
    except Exception as e:
        print("🔥 GET_GAME_SERVICE ERROR:", repr(e))
        raise


def get_image_service() -> ImageService:
    """Factory để tạo ImageService với configured provider"""
    try:
        if settings.image_provider.lower() == "kaggle":
            provider = KaggleProvider(api_url=settings.kaggle_api_url)
            return ImageService(provider=provider)
        else:
            # Fallback: return ImageService without provider
            return ImageService(provider=None)
    except Exception as e:
        print("🔥 GET_IMAGE_SERVICE ERROR:", repr(e))
        raise