from __future__ import annotations

import os
import re
import base64
import requests
from dataclasses import asdict
from pathlib import Path
from PIL import Image
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import FileResponse

from app.api.dependencies import get_game_service, get_image_service
from app.domain.schemas import ImagesGenerationRequest
from app.services.game_service import GameService
from app.services.image_service import ImageService
from app.services.world_definitions import WORLD_REGISTRY

# Debug endpoints for image generation - v2
router = APIRouter(prefix="/debug", tags=["debug"])


# ============= HELPER FUNCTIONS =============

def sanitize_filename(text: str) -> str:
    """
    Sanitize text to make it safe for file paths while preserving Vietnamese diacritics.
    - Convert to lowercase
    - Replace spaces with underscores
    - Remove only problematic special characters for filenames
    - Remove consecutive underscores
    - Strip leading/trailing underscores
    """
    text = text.lower().strip()
    text = text.replace(" ", "_")
    # Remove only filesystem-dangerous characters
    text = re.sub(r'[/\\:*?"<>|]', '', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip("_")
    return text


def build_world_theme_prompt(world) -> str:
    """
    Dynamically construct a rich prompt from world definition data.
    
    Combines:
    - world.name
    - world.genre
    - world.tone
    - world.core_theme
    - First item from world.notable_regions (if available)
    
    Example output:
    "A dark fantasy landscape for Eldoria Tàn Tro. Tone: u ám, bí ẩn, căng thẳng...
     Theme: suy tàn, bí mật bị chôn vùi...
     Featuring: Thành Phế Tích Vàng Son (thủ đô cũ, nay là mê cung đổ nát...)"
    """
    parts = [
        f"A {world.genre} landscape for {world.name}",
        f"Tone: {world.tone}",
        f"Core theme: {world.core_theme}",
    ]
    
    # Add first region description if available
    if world.notable_regions and len(world.notable_regions) > 0:
        first_region = world.notable_regions[0]
        parts.append(f"Featuring: {first_region}")
    
    return ". ".join(parts)


def call_kaggle_backend_sync(
    prompt: str,
    world_name: str,
    summarize_model: str,
    txt2img_model: str,
    steps: int,
    kaggle_api_url: str,
) -> dict:
    """
    Synchronous call to Kaggle FastAPI backend for world theme generation.
    
    Args:
        prompt: World description/lore
        world_name: Name of the world
        summarize_model: "gemini-2.5-flash" or "Qwen/Qwen2.5-1.5B-Instruct"
        txt2img_model: "SDXL lightning" or "Gemini API banana pro"
        steps: Inference steps (4 or 8)
        kaggle_api_url: Backend base URL (e.g., https://xxx.ngrok.io)
    
    Returns:
        Response dict with status, image_base64, en_prompt, etc.
    """
    try:
        print(f"   📤 Calling Kaggle backend...")
        payload = {
            "prompt": prompt,
            "world_name": world_name,
            "summarize_model": summarize_model,
            "txt2img_model": txt2img_model,
            "step": steps,
        }
        
        endpoint_url = f"{kaggle_api_url}/generate-world-theme"
        print(f"   🔗 Endpoint: {endpoint_url}")
        
        response = requests.post(
            endpoint_url,
            json=payload,
            timeout=600,  # Long timeout for image generation
        )
        
        if response.status_code != 200:
            error_text = response.text
            print(f"   ❌ Kaggle returned {response.status_code}: {error_text}")
            raise Exception(f"Kaggle API error {response.status_code}: {error_text}")
        
        data = response.json()
        print(f"   ✅ Kaggle responded: {data.get('status')}")
        return data
    
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Failed: {error_msg}")
        raise Exception(f"Failed to call Kaggle backend: {error_msg}")



@router.get("/health")
def health_check() -> dict:
    """Simple health check for debug endpoints"""
    return {"status": "ok", "message": "Debug routes are working"}


@router.get("/state/{session_id}")
def debug_get_full_state(
    session_id: str,
    game_service: GameService = Depends(get_game_service),
) -> dict:
    try:
        if not game_service.session_exists(session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy session: {session_id}",
            )

        game_state = game_service.get_game_state(session_id)
        return asdict(game_state)
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= IMAGE GENERATION ENDPOINTS =============


@router.post("/images/world-theme")
def debug_generate_world_theme(
    request: ImagesGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
    game_service: GameService = Depends(get_game_service),
) -> dict:
    """Sinh hình ảnh theme cho một thế giới"""
    try:
        # Nếu không có session_id, generate generic world theme image
        if request.session_id is None:
            # Sinh hình ảnh generic world theme
            response = image_service.generate_scene_image(
                scene_description="A mystical fantasy world with ancient ruins, magical atmosphere, epic landscape",
                style=request.style or "fantasy",
                name="generic_world_theme",
            )
            return {
                "success": True,
                "local_path": response.local_path,
                "image_url": response.image_url,
                "provider": response.provider_name,
            }
        
        if not game_service.session_exists(request.session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy session: {request.session_id}",
            )

        game_state = game_service.get_game_state(request.session_id)
        response = image_service.generate_world_theme_image(
            world=game_state.world_definition,
            style=request.style,
        )

        return {
            "success": True,
            "local_path": response.local_path,
            "image_url": response.image_url,
            "provider": response.provider_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/story-theme")
def debug_generate_story_theme(
    request: ImagesGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
    game_service: GameService = Depends(get_game_service),
) -> dict:
    """Sinh hình ảnh theme cho câu chuyện hiện tại"""
    try:
        # Nếu không có session_id, generate generic story theme
        if request.session_id is None:
            # Sinh hình ảnh generic story theme
            response = image_service.generate_scene_image(
                scene_description="An epic adventure story beginning, hero's journey, dramatic lighting, cinematic atmosphere",
                style=request.style or "fantasy",
                name="generic_story_theme",
            )
            return {
                "success": True,
                "local_path": response.local_path,
                "image_url": response.image_url,
                "provider": response.provider_name,
            }
        
        if not game_service.session_exists(request.session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy session: {request.session_id}",
            )

        game_state = game_service.get_game_state(request.session_id)
        response = image_service.generate_story_theme_image(
            game_state=game_state,
            style=request.style,
        )

        return {
            "success": True,
            "local_path": response.local_path,
            "image_url": response.image_url,
            "provider": response.provider_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/scene")
def debug_generate_scene_image(
    request: ImagesGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
) -> dict:
    """Sinh hình ảnh cho một khung cảnh"""
    try:
        if not request.description:
            raise HTTPException(
                status_code=400,
                detail="description là bắt buộc",
            )

        print(f"🎨 DEBUG: Generating scene image with description: {request.description}")
        print(f"🎨 DEBUG: Style: {request.style}")
        
        response = image_service.generate_scene_image(
            scene_description=request.description,
            style=request.style,
            name="custom_scene",
        )

        print(f"🎨 DEBUG: Response received - local_path: {response.local_path}")
        print(f"🎨 DEBUG: Generated URL: {response.image_url}")

        return {
            "success": True,
            "local_path": response.local_path,
            "image_url": response.image_url,
            "provider": response.provider_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ DEBUG ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= BULK WORLD THEME GENERATION =============


@router.post("/images/generate-all-worlds")
def generate_all_world_themes(
    image_service: ImageService = Depends(get_image_service),
) -> dict:
    """
    Generate theme images for ALL 7 worlds using Kaggle backend (same as /theme/generate-all-worlds).
    
    **Fast Mode:** If images already exist, returns cached URLs immediately (< 100ms).
    **Slow Mode:** If images don't exist, generates them via Kaggle backend (can take 1-5 minutes).
    
    For each world:
    1. Dynamically build a rich prompt from world data (name, genre, tone, core_theme, first_region)
    2. Call Kaggle backend's /generate-world-theme endpoint
    3. Save base64 image to generated_imgs/theme_stories/{safe_name}_theme.png
    4. Return URLs and metadata
    
    Returns:
    - success: True/False
    - total_worlds: Total number of worlds in registry
    - generated: Number of successfully generated/cached images
    - results: List of per-world results with status, URL, filename, image_base64
    - from_cache: Boolean indicating if results are from cache
    
    **Idempotency:** Files are overwritten if they already exist.
    """
    try:
        print("\n" + "="*70)
        print("🌍 DEBUG: Generating ALL 7 world theme images via Kaggle backend...")
        print("="*70)
        
        # Ensure the theme_stories directory exists
        theme_dir = Path("generated_imgs") / "theme_stories"
        theme_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Theme directory ready: {theme_dir}\n")
        
        # Get Kaggle API URL from config
        kaggle_api_url = os.getenv(
            "KAGGLE_API_URL",
            "https://onion-vertical-squash.ngrok-free.dev"
        )
        print(f"🔗 Kaggle Backend: {kaggle_api_url}\n")
        
        # Default model configuration
        summarize_model = "gemini-2.5-flash"
        txt2img_model = "SDXL lightning"
        steps = 4
        
        results = []
        success_count = 0
        
        # ======== FAST MODE: CHECK IF ALL IMAGES ALREADY EXIST ========
        print("📦 Checking for existing cached images...")
        all_exist = True
        existing_results = []
        
        for world_id, world in WORLD_REGISTRY.items():
            safe_name = sanitize_filename(world.name)
            filename = f"{safe_name}_theme.png"
            file_path = theme_dir / filename
            image_url = f"/theme_images/{filename}"
            
            if file_path.exists():
                print(f"   ✅ Cache HIT: {filename}")
                existing_results.append({
                    "world_id": world_id,
                    "world_name": world.name,
                    "status": "success",
                    "image_url": image_url,
                    "filename": filename,
                    "local_path": str(file_path),
                    "from_cache": True,
                })
            else:
                print(f"   ❌ Cache MISS: {filename} - will generate")
                all_exist = False
        
        # If all images exist, return cached results (FAST!)
        if all_exist and len(existing_results) == len(WORLD_REGISTRY):
            print(f"\n✅ All images found in cache! Returning instantly...\n")
            return {
                "success": True,
                "total_worlds": len(WORLD_REGISTRY),
                "generated": len(existing_results),
                "from_cache": True,
                "theme_directory": str(theme_dir),
                "results": existing_results,
            }
        
        # ======== SLOW MODE: GENERATE MISSING IMAGES ========
        print(f"\n⚠️ Cache incomplete. Generating missing images via Kaggle...\n")
        
        # Iterate through all worlds in the registry
        for world_id, world in WORLD_REGISTRY.items():
            try:
                print(f"🎨 Processing: {world.name}")
                
                # 1. Dynamically build prompt from world data
                prompt = build_world_theme_prompt(world)
                print(f"   📝 Prompt: {prompt[:100]}...")
                
                # 2. Call Kaggle Backend via /generate-world-theme endpoint
                kaggle_response = call_kaggle_backend_sync(
                    prompt=prompt,
                    world_name=world.name,
                    summarize_model=summarize_model,
                    txt2img_model=txt2img_model,
                    steps=steps,
                    kaggle_api_url=kaggle_api_url,
                )
                
                # 3. Check response status
                if kaggle_response.get("status") != "success":
                    raise Exception(f"Kaggle backend failed: {kaggle_response.get('error', 'Unknown error')}")
                
                # 4. Decode and save image
                image_base64 = kaggle_response.get("image_base64", "")
                en_prompt = kaggle_response.get("en_prompt", "")
                saved_at = kaggle_response.get("saved_at", "")
                
                if not image_base64:
                    raise Exception("No image_base64 in Kaggle response")
                
                # Decode base64 to image
                image_data = base64.b64decode(image_base64)
                image = Image.open(io.BytesIO(image_data))
                
                # 5. Save image locally
                safe_name = sanitize_filename(world.name)
                filename = f"{safe_name}_theme.png"
                file_path = theme_dir / filename
                image.save(str(file_path))
                
                image_url = f"/theme_images/{filename}"
                print(f"   💾 Saved: {filename}")
                print(f"   📎 URL: {image_url}\n")
                
                results.append({
                    "world_id": world_id,
                    "world_name": world.name,
                    "status": "success",
                    "image_url": image_url,
                    "filename": filename,
                    "local_path": str(file_path),
                    "image_base64": image_base64,
                    "en_prompt": en_prompt,
                    "saved_at": saved_at,
                })
                success_count += 1
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Error: {error_msg}\n")
                results.append({
                    "world_id": world_id,
                    "world_name": world.name,
                    "status": "failed",
                    "error": error_msg,
                })
        
        print("="*70)
        print(f"✅ COMPLETED! Generated {success_count}/{len(WORLD_REGISTRY)} world images")
        print("="*70 + "\n")
        
        return {
            "success": success_count > 0,
            "total_worlds": len(WORLD_REGISTRY),
            "generated": success_count,
            "from_cache": False,
            "theme_directory": str(theme_dir),
            "results": results,
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Bulk generation error: {error_msg}\n")
        raise HTTPException(status_code=500, detail=error_msg)



@router.get("/generation-status")
def get_generation_status():
    """
    Get the current configuration status of theme generation.
    Returns list of generated world theme images.
    
    Frontend calls this to fetch available images after generation.
    """
    try:
        theme_dir = Path("generated_imgs") / "theme_stories"
        
        if not theme_dir.exists():
            return {
                "total_worlds": len(WORLD_REGISTRY),
                "generated_worlds": 0,
                "images": [],
            }
        
        images = list(theme_dir.glob("*.png"))
        
        return {
            "total_worlds": len(WORLD_REGISTRY),
            "generated_worlds": len(images),
            "images": [img.name for img in images],
            "last_updated": datetime.fromtimestamp(max(img.stat().st_mtime for img in images) if images else 0).isoformat(),
        }
    except Exception as e:
        print(f"❌ Error getting generation status: {str(e)}")
        return {
            "total_worlds": len(WORLD_REGISTRY),
            "generated_worlds": 0,
            "images": [],
            "error": str(e),
        }


@router.get("/images/theme/{filename}")
def get_theme_image(filename: str) -> FileResponse:
    """
    Lấy hình ảnh theme đã sinh từ theme_stories folder.
    
    Endpoint này giúp frontend truy cập hình ảnh qua API (có trong docs).
    Ngoài ra, frontend cũng có thể gọi trực tiếp /theme_images/{filename}
    """
    try:
        # Đường dẫn file
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "generated_imgs", "theme_stories")
        file_path = os.path.join(base_dir, filename)
        
        # Security check: Đảm bảo file nằm trong theme_stories folder
        if not os.path.abspath(file_path).startswith(os.path.abspath(base_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Kiểm tra file tồn tại
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Image not found: {filename}"
            )
        
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))