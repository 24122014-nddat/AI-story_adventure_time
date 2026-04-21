"""
Example script để test ImageService integration

Cách sử dụng:
1. Set environment variables trong .env:
   - IMAGE_PROVIDER=kaggle
   - KAGGLE_API_URL=https://your-ngrok-url/generate

2. Chạy script này để test:
   python test_image_service.py
"""

from app.ai.providers.kaggle_provider import KaggleProvider
from app.services.image_service import ImageService
from app.domain.models import (
    CharacterProfile,
    GameState,
    NPC,
    NPCMemory,
    NPCPersonality,
    StoryState,
    WorldDefinition,
    WorldState,
    StoryMemory,
)


def test_image_service():
    """Test tất cả chức năng của ImageService"""

    # Tạo KaggleProvider
    provider = KaggleProvider(
        api_url="https://onion-vertical-squash.ngrok-free.dev/generate"
    )
    service = ImageService(provider=provider)

    # ============ TEST 1: Tạo world theme image ============
    print("🎨 Test 1: Generating world theme image...")
    world = WorldDefinition(
        world_id="world_1",
        name="The Dark Woods",
        genre="fantasy",
        tone="mysterious",
        core_theme="survival in hostile environment",
        world_lore="An ancient forest cursed by dark magic",
        notable_regions=["The Whispering Forest", "The Raven Mountains", "The Mist Valleys"],
        danger_types=["undead creatures", "cursed magic", "wild beasts"],
    )

    try:
        response = service.generate_world_theme_image(world)
        print(f"✅ World theme image saved: {response.local_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ============ TEST 2: Tạo scene image ============
    print("\n🎨 Test 2: Generating scene image...")
    scene_description = "A medieval tavern with a warm fireplace, wooden beams, and mysterious travelers"

    try:
        response = service.generate_scene_image(
            scene_description=scene_description,
            style="fantasy",
        )
        print(f"✅ Scene image saved: {response.local_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ============ TEST 3: Tạo NPC image ============
    print("\n🎨 Test 3: Generating NPC image...")
    npc = NPC(
        npc_id="npc_1",
        name="Aldric the Ranger",
        role="skilled tracker and guide",
        personality=NPCPersonality(
            traits=["brave", "mysterious", "intelligent"],
            speaking_style="cryptic and poetic",
            moral_alignment="neutral good",
        ),
        memory=NPCMemory(
            short_term=["met a stranger in the forest"],
            long_term_facts=["lost family in the curse"],
        ),
    )

    try:
        response = service.generate_npc_image(
            npc=npc,
            scene_context="in a dark forest with ancient trees",
            style="fantasy",
        )
        print(f"✅ NPC image saved: {response.local_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # ============ TEST 4: Tạo story theme image ============
    print("\n🎨 Test 4: Generating story theme image...")

    game_state = GameState(
        session_id="test_session",
        world_definition=world,
        character_profile=CharacterProfile(
            name="Kael",
            background="a young adventurer seeking redemption",
            personality_traits=["determined", "compassionate"],
            virtues=["honor", "courage"],
        ),
        story_state=StoryState(
            current_situation="trapped in a cursed forest",
            current_tension="mysterious shadows closing in",
            current_objective="find the ancient ritual site",
            current_location_hint="deep in the forest",
        ),
        world=WorldState(location="The Whispering Forest"),
        story_memory=StoryMemory(),
    )

    try:
        response = service.generate_story_theme_image(game_state)
        print(f"✅ Story theme image saved: {response.local_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n✨ All tests completed!")


if __name__ == "__main__":
    test_image_service()
