"""
Unified Asset Prompt Builder
Constructs rich prompts for Themes, NPCs, and Scenes based on world context
"""
from __future__ import annotations

from app.domain.models import WorldDefinition


class AssetPromptBuilder:
    """Factory for building prompts based on asset type"""
    
    @staticmethod
    def build_theme_prompt(world: WorldDefinition) -> str:
        """
        Build a rich visual prompt for world theme images
        
        Uses:
        - World name, genre, tone
        - Core theme
        - First notable_region for specificity
        
        Returns English-ready prompt for image generation
        """
        parts = []
        
        # Scene-setting header
        parts.append(f"A {world.genre} landscape")
        
        # World identity
        parts.append(f"for the world of {world.name}")
        
        # Atmospheric tone
        if world.tone:
            parts.append(f"with {world.tone} atmosphere")
        
        # Core theme emphasis
        if world.core_theme:
            parts.append(f"embodying {world.core_theme}")
        
        # Specific location from notable regions
        if world.notable_regions and len(world.notable_regions) > 0:
            first_region = world.notable_regions[0]
            parts.append(f"featuring {first_region}")
        
        # Visual style hint
        parts.append("detailed, atmospheric, cinematic lighting")
        
        return ". ".join(parts)
    
    @staticmethod
    def build_npc_prompt(
        npc_name: str,
        npc_description: str,
        world: WorldDefinition | None = None,
    ) -> str:
        """
        Build a visual prompt for NPC character images
        
        Uses:
        - NPC name and description (personality, appearance, role)
        - Optional world context for consistency
        
        Args:
            npc_name: Character name
            npc_description: Description (appearance, personality, role)
            world: Optional world context for styling consistency
        
        Returns English-ready prompt for image generation
        """
        parts = []
        
        # Character identity
        parts.append(f"Portrait of {npc_name}")
        
        # Description
        if npc_description:
            parts.append(npc_description)
        
        # World-specific styling if provided
        if world:
            if world.genre:
                parts.append(f"in {world.genre} style")
            if world.tone:
                parts.append(f"with {world.tone} aesthetic")
        
        # Visual quality hints
        parts.append("detailed face, expressive eyes, character sheet art, high quality")
        
        return ". ".join(parts)
    
    @staticmethod
    def build_scene_prompt(
        scene_description: str,
        plot_context: str | None = None,
        world: WorldDefinition | None = None,
    ) -> str:
        """
        Build a visual prompt for scene/event images
        
        Uses:
        - Scene description
        - Optional plot/narrative context
        - Optional world styling
        
        Args:
            scene_description: What's happening in the scene
            plot_context: Narrative context or mood
            world: Optional world context for consistency
        
        Returns English-ready prompt for image generation
        """
        parts = []
        
        # Main scene description
        if scene_description:
            parts.append(scene_description)
        
        # Narrative context
        if plot_context:
            parts.append(plot_context)
        
        # World-specific styling if provided
        if world:
            if world.genre:
                parts.append(f"in the style of {world.genre}")
            if world.tone:
                parts.append(f"{world.tone} mood")
        
        # Visual quality hints
        parts.append("cinematic composition, dramatic lighting, concept art, high detail")
        
        return ". ".join(parts)
    
    @staticmethod
    def build_prompt(
        asset_type: str,
        world: WorldDefinition | None = None,
        npc_name: str | None = None,
        npc_description: str | None = None,
        scene_description: str | None = None,
        plot_context: str | None = None,
    ) -> str:
        """
        Unified prompt builder dispatcher
        
        Args:
            asset_type: "theme", "npc", or "scene"
            world: World context (required for theme, optional for others)
            npc_name: NPC name (required for npc)
            npc_description: NPC description (required for npc)
            scene_description: Scene description (required for scene)
            plot_context: Plot context (optional for scene)
        
        Returns:
            English-ready prompt for image generation
        
        Raises:
            ValueError: If required parameters are missing
        """
        asset_type = asset_type.lower().strip()
        
        if asset_type == "theme":
            if not world:
                raise ValueError("World context is required for theme prompt building")
            return AssetPromptBuilder.build_theme_prompt(world)
        
        elif asset_type == "npc":
            if not npc_name or not npc_description:
                raise ValueError("NPC name and description are required for npc prompt building")
            return AssetPromptBuilder.build_npc_prompt(npc_name, npc_description, world)
        
        elif asset_type == "scene":
            if not scene_description:
                raise ValueError("Scene description is required for scene prompt building")
            return AssetPromptBuilder.build_scene_prompt(scene_description, plot_context, world)
        
        else:
            raise ValueError(f"Unsupported asset_type: {asset_type}")
