from __future__ import annotations

from app.ai.providers.image_base import (
    BaseImageProvider,
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from app.domain.models import (
    CharacterProfile,
    GameState,
    NPC,
    WorldDefinition,
)


class ImageService:
    """Service để quản lý sinh hình ảnh cho game elements"""

    def __init__(self, provider: BaseImageProvider | None = None):
        """
        Khởi tạo ImageService

        Args:
            provider: Image provider (KaggleProvider, etc.)
        """
        self.provider = provider

    def generate_world_theme_image(
        self,
        world: WorldDefinition,
        style: str | None = None,
    ) -> ImageGenerationResponse:
        """
        Sinh hình ảnh theme cho một thế giới

        Args:
            world: WorldDefinition chứa thông tin thế giới
            style: Art style (nếu None sẽ tự detect từ genre)

        Returns:
            ImageGenerationResponse
        """
        if self.provider is None:
            raise ValueError("Chưa cấu hình image provider.")

        # Detect style từ genre nếu không chỉ định
        if style is None:
            style = self._infer_style_from_genre(world.genre)

        # Build prompt từ world definition
        prompt = self._build_world_prompt(world)

        request = ImageGenerationRequest(
            prompt=prompt,
            style=style,
            size="1024x1024",
            name=world.name,  # Pass world name for filename generation
        )
        return self.provider.generate_image(request)

    def generate_story_theme_image(
        self,
        game_state: GameState,
        style: str | None = None,
    ) -> ImageGenerationResponse:
        """
        Sinh hình ảnh theme cho story hiện tại

        Args:
            game_state: GameState chứa thông tin câu chuyện
            style: Art style (nếu None sẽ tự detect)

        Returns:
            ImageGenerationResponse
        """
        if self.provider is None:
            raise ValueError("Chưa cấu hình image provider.")

        if style is None:
            style = self._infer_style_from_genre(game_state.world_definition.genre)

        # Build prompt từ story state, character, world
        prompt = self._build_story_theme_prompt(game_state)

        request = ImageGenerationRequest(
            prompt=prompt,
            style=style,
            size="1024x1024",
        )
        return self.provider.generate_image(request)

    def generate_scene_image(
        self,
        scene_description: str,
        style: str = "fantasy",
        size: str = "1024x1024",
        name: str = "scene",
    ) -> ImageGenerationResponse:
        """
        Sinh hình ảnh cho một khung cảnh cụ thể

        Args:
            scene_description: Mô tả chi tiết của khung cảnh
            style: Art style
            size: Kích thước hình ảnh
            name: Tên cho hình ảnh (mặc định: "scene")

        Returns:
            ImageGenerationResponse
        """
        if self.provider is None:
            raise ValueError("Chưa cấu hình image provider.")

        request = ImageGenerationRequest(
            prompt=scene_description,
            style=style,
            size=size,
            name=name,
        )
        return self.provider.generate_image(request)

    def generate_npc_image(
        self,
        npc: NPC,
        scene_context: str = "",
        style: str = "fantasy",
    ) -> ImageGenerationResponse:
        """
        Sinh hình ảnh cho một NPC

        Args:
            npc: NPC object chứa thông tin
            scene_context: Bối cảnh/setting mà NPC xuất hiện
            style: Art style

        Returns:
            ImageGenerationResponse
        """
        if self.provider is None:
            raise ValueError("Chưa cấu hình image provider.")

        prompt = self._build_npc_prompt(npc, scene_context)

        request = ImageGenerationRequest(
            prompt=prompt,
            style=style,
            size="1024x1024",
            name=npc.name,
        )
        return self.provider.generate_image(request)

    # ============= HELPER METHODS =============

    def _build_world_prompt(self, world: WorldDefinition) -> str:
        """Build rich prompt for world theme image, including first region description"""
        parts = [
            f"A breathtaking landscape representing {world.name}",
            f"Genre: {world.genre}",
            f"Tone: {world.tone}",
            f"Core theme: {world.core_theme}",
        ]

        # Extract and add first region's detailed description for richer visuals
        if world.notable_regions:
            first_region_description = world.notable_regions[0]
            parts.append(f"Featured location: {first_region_description}")

        # Add danger context to enhance atmosphere
        if world.danger_types:
            parts.append(f"Evoking dangers of {', '.join(world.danger_types[:2])}")

        return ", ".join(parts)

    def _build_story_theme_prompt(self, game_state: GameState) -> str:
        """Build prompt cho story theme image"""
        world = game_state.world_definition
        character = game_state.character_profile
        story = game_state.story_state

        parts = [
            f"{character.name} in {world.name}",
            f"Current situation: {story.current_situation}",
            f"Tension: {story.current_tension}",
            f"Location: {game_state.world.full_location}",
            f"Time of day: {game_state.world.time_of_day}",
            f"Tone: {world.tone}",
        ]

        return ", ".join(parts)

    def _build_npc_prompt(self, npc: NPC, scene_context: str) -> str:
        """Build prompt cho NPC image"""
        parts = [
            f"A portrait of {npc.name}, {npc.role}",
        ]

        if npc.personality.traits:
            parts.append(f"Personality: {', '.join(npc.personality.traits[:3])}")

        if npc.personality.speaking_style:
            parts.append(f"Speaking style: {npc.personality.speaking_style}")

        if scene_context:
            parts.append(f"Scene: {scene_context}")

        parts.append("highly detailed, professional art style")

        return ", ".join(parts)

    def _infer_style_from_genre(self, genre: str) -> str:
        """Infer art style từ genre"""
        genre = genre.lower()

        style_map = {
            "fantasy": "fantasy",
            "cyberpunk": "cyberpunk",
            "steampunk": "oil_painting",
            "horror": "gothic",
            "mystery": "oil_painting",
            "sci-fi": "cyberpunk",
            "romance": "watercolor",
            "adventure": "fantasy",
            "dark": "gothic",
            "anime": "anime",
        }

        for key, style in style_map.items():
            if key in genre:
                return style

        return "fantasy"  # Default style