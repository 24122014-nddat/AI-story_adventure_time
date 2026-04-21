from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageGenerationRequest:
    prompt: str
    style: str = "fantasy"
    size: str = "1024x1024"
    name: str = ""  # Optional name used for filename generation


@dataclass
class ImageGenerationResponse:
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    provider_name: str = ""


class BaseImageProvider(ABC):
    @abstractmethod
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        raise NotImplementedError