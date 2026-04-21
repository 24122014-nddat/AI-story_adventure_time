from __future__ import annotations

import base64
import io
import os
import re
from pathlib import Path

import requests
from PIL import Image

from app.ai.providers.image_base import (
    BaseImageProvider,
    ImageGenerationRequest,
    ImageGenerationResponse,
)


class KaggleProvider(BaseImageProvider):
    """Provider để kết nối với API image generation trên Kaggle qua ngrok"""

    def __init__(self, api_url: str | None = None):
        """
        Khởi tạo KaggleProvider

        Args:
            api_url: URL endpoint của Kaggle API (mặc định từ env variable)
        """
        self.api_url = api_url or os.getenv(
            "KAGGLE_API_URL", "https://onion-vertical-squash.ngrok-free.dev/generate-image"
        )
        self.output_dir = "generated_imgs"
        self.theme_dir = Path(self.output_dir) / "theme_stories"
        # Ensure base directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResponse:
        """
        Gửi request tới Kaggle Backend /generate-world-theme endpoint

        Args:
            request: ImageGenerationRequest chứa prompt, style, size, name

        Returns:
            ImageGenerationResponse với đường dẫn file local
        """
        try:
            print(f"🎨 KaggleProvider.generate_image()")
            print(f"   Prompt: {request.prompt[:80]}...")
            print(f"   Style: {request.style}")
            print(f"   Name: {request.name}")
            
            # Map style to model format for Kaggle backend
            txt2img_model = self._map_style_to_model(request.style)
            
            # Prepare payload for Kaggle backend's /generate-world-theme endpoint
            payload = {
                "prompt": request.prompt,
                "world_name": request.name or "unknown",
                "summarize_model": "gemini-2.5-flash",  # Default model
                "txt2img_model": txt2img_model,
                "step": 4,  # Default steps
            }
            
            # Build correct endpoint URL
            endpoint_url = f"{self.api_url}/generate-world-theme"
            print(f"   Calling: {endpoint_url}")
            
            # Gửi request tới Kaggle Backend
            response = requests.post(
                endpoint_url,
                json=payload,
                timeout=600,  # Long timeout for image generation
            )

            if response.status_code != 200:
                error_detail = response.text
                print(f"   ❌ Kaggle API error {response.status_code}: {error_detail}")
                raise Exception(f"Kaggle API error {response.status_code}: {error_detail}")

            # Parse response from Kaggle backend
            data = response.json()
            print(f"   Response status: {data.get('status')}")
            
            if data.get("status") != "success":
                raise Exception(f"Kaggle backend failed: {data.get('error', 'Unknown error')}")

            # Decode base64 image từ response
            image_base64 = data.get("image_base64")
            if not image_base64:
                raise Exception("No image_base64 in Kaggle response")
            
            img_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(img_data))

            # Ensure theme_stories directory exists
            self.theme_dir.mkdir(parents=True, exist_ok=True)

            # Generate sanitized filename: <name>_<style>.png
            filename = self._generate_theme_filename(request.name or "unknown", request.style)
            filepath = self.theme_dir / filename

            # Save image (overwrites if exists - no timestamps/UUIDs)
            image.save(str(filepath))
            print(f"   ✅ Saved to: {filename}")

            # Build image URL for frontend to access via GET /theme_images/<filename>
            image_url = f"/theme_images/{filename}"

            return ImageGenerationResponse(
                image_url=image_url,
                local_path=str(filepath),
                provider_name="kaggle",
            )

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ KaggleProvider error: {error_msg}")
            raise Exception(f"Kaggle image generation failed: {error_msg}")

    def _build_prompt(self, base_prompt: str, style: str) -> str:
        """
        Enhance prompt với style information

        Args:
            base_prompt: Prompt gốc
            style: Style của hình ảnh (fantasy, realistic, etc.)

        Returns:
            Prompt được enhance
        """
        style_mapping = {
            "fantasy": "in the style of fantasy art, magical, epic",
            "realistic": "photorealistic, high quality, detailed",
            "anime": "anime art style, vibrant colors",
            "oil_painting": "oil painting style, classical art",
            "watercolor": "watercolor art style, soft colors",
            "cyberpunk": "cyberpunk style, neon lights, futuristic",
            "gothic": "gothic art style, dark atmosphere",
            "impressionism": "impressionism style, soft brushstrokes",
        }

        style_suffix = style_mapping.get(style, f"in {style} style")
        return f"{base_prompt}, {style_suffix}, high quality, detailed"

    def _map_style_to_model(self, style: str) -> str:
        """
        Map art style to Kaggle backend image generation model.
        
        Args:
            style: Art style (fantasy, cyberpunk, gothic, etc.)
        
        Returns:
            Model identifier for Kaggle backend
        """
        # Default to SDXL for most styles
        return "SDXL lightning"

    def _sanitize_filename(self, text: str) -> str:
        """
        Sanitize text to make it safe for file paths.
        Replaces spaces with underscores, removes special characters.

        Args:
            text: Text to sanitize

        Returns:
            Safe filename component
        """
        # Replace spaces with underscores
        text = text.replace(" ", "_")
        # Keep only alphanumeric, underscores, and hyphens
        text = re.sub(r'[^a-zA-Z0-9_-]', '', text)
        # Remove consecutive underscores
        text = re.sub(r'_+', '_', text)
        # Remove leading/trailing underscores
        text = text.strip("_")
        return text

    def _generate_theme_filename(self, name: str, style: str) -> str:
        """
        Generate filename in format: <name>_<style>.png
        Both name and style are sanitized to be file-path safe.

        Args:
            name: World/theme name (e.g., "Eldoria Tàn Tro")
            style: Art style (e.g., "gothic")

        Returns:
            Sanitized filename (e.g., "eldoria_tan_tro_gothic.png")
        """
        sanitized_name = self._sanitize_filename(name).lower()
        sanitized_style = self._sanitize_filename(style).lower()
        return f"{sanitized_name}_{sanitized_style}.png"
