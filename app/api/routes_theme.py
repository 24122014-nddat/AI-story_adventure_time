"""
Theme Generation Routes - Advanced Configuration for World Theme Images
Supports configurable summarization & image generation models
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.api.dependencies import get_image_service
from app.domain.schemas import (
    UnifiedThemeGenerationRequest,
    ThemeGenerationResponse,
    BulkThemeGenerationResponse,
)
from app.services.image_service import ImageService
from app.services.world_definitions import WORLD_REGISTRY

router = APIRouter(prefix="/theme", tags=["theme-generation"])


# ============= HELPER FUNCTIONS =============

def sanitize_filename(text: str) -> str:
    """Convert text to safe filename while preserving Vietnamese diacritics"""
    text = text.lower().strip()
    text = text.replace(" ", "_")
    # Remove only filesystem-dangerous characters
    text = re.sub(r'[/\\:*?"<>|]', '', text)
    return re.sub(r'_+', '_', text)


def build_world_prompt(world) -> str:
    """Dynamically build a rich prompt from world definition data"""
    parts = [
        f"A {world.genre} landscape for {world.name}",
        f"Tone: {world.tone}",
        f"Core theme: {world.core_theme}",
    ]
    
    if world.notable_regions and len(world.notable_regions) > 0:
        first_region = world.notable_regions[0]
        parts.append(f"Featuring: {first_region}")
    
    return ". ".join(parts)


async def call_kaggle_backend(
    prompt: str,
    world_name: str,
    summarize_model: str,
    txt2img_model: str,
    steps: int,
    kaggle_api_url: str,
) -> dict:
    """
    Call the Kaggle FastAPI backend for unified theme generation
    
    Args:
        prompt: World lore/description
        world_name: Name of the world
        summarize_model: "gemini-2.5-flash" or "qwen-1.5b"
        txt2img_model: "sdxl-lightning" or "gemini-imagen"
        steps: Inference steps (4 or 8)
        kaggle_api_url: Backend URL (e.g., https://xxx.ngrok.io)
    
    Returns:
        Response dict with status, image_base64, en_prompt, etc.
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            payload = {
                "prompt": prompt,
                "world_name": world_name,
                "summarize_model": summarize_model,
                "txt2img_model": txt2img_model,
                "step": steps,
            }
            
            response = await client.post(
                f"{kaggle_api_url}/generate-world-theme",
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(f"Kaggle API returned {response.status_code}: {response.text}")
            
            return response.json()
    
    except Exception as e:
        raise Exception(f"Failed to call Kaggle backend: {str(e)}")


# ============= MAIN ROUTES =============

@router.post("/generate-all-worlds", response_model=BulkThemeGenerationResponse)
async def generate_all_world_themes(
    request: UnifiedThemeGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
) -> BulkThemeGenerationResponse:
    """
    Generate theme images for ALL 7 worlds with configurable models
    
    **Supported Models:**
    - Summarization: "gemini-2.5-flash", "qwen-1.5b"
    - Image Generation: "sdxl-lightning", "gemini-imagen"
    - Steps: 4 or 8 (SDXL Lightning only)
    
    **Process:**
    1. For each world, build a dynamic prompt from world data
    2. Send to Kaggle Backend for summarization & image generation
    3. Save image locally to generated_imgs/theme_stories/
    4. Return URLs and Base64 encoded images
    
    **Idempotency:** Existing files are overwritten
    """
    try:
        print(f"🎨 Starting theme generation for all 7 worlds...")
        print(f"   Summarize Model: {request.summarize_model}")
        print(f"   Image Model: {request.txt2img_model}")
        print(f"   Steps: {request.steps}")
        
        # Create output directory
        theme_dir = Path("generated_imgs") / "theme_stories"
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        # Get Kaggle API URL from environment or config
        kaggle_api_url = os.getenv(
            "KAGGLE_API_URL",
            "https://onion-vertical-squash.ngrok-free.dev"
        )
        
        results = []
        generated_count = 0
        
        # Iterate through all 7 worlds
        for world_id, world in WORLD_REGISTRY.items():
            try:
                print(f"\n🌍 Processing: {world.name}")
                
                # Step 1: Build dynamic prompt
                prompt = build_world_prompt(world)
                print(f"   Prompt: {prompt[:100]}...")
                
                # Step 2: Call Kaggle Backend
                print(f"   Calling Kaggle API...")
                kaggle_response = await call_kaggle_backend(
                    prompt=prompt,
                    world_name=world.name,
                    summarize_model=request.summarize_model,
                    txt2img_model=request.txt2img_model,
                    steps=request.steps,
                    kaggle_api_url=kaggle_api_url,
                )
                
                if kaggle_response.get("status") != "success":
                    raise Exception(f"Kaggle API failed: {kaggle_response.get('error', 'Unknown error')}")
                
                # Step 3: Save image locally
                en_prompt = kaggle_response.get("en_prompt", "")
                image_base64 = kaggle_response.get("image_base64", "")
                
                if image_base64:
                    import base64
                    image_data = base64.b64decode(image_base64)
                    
                    safe_name = sanitize_filename(world.name)
                    filename = f"{safe_name}_theme.png"
                    file_path = theme_dir / filename
                    
                    with open(file_path, "wb") as f:
                        f.write(image_data)
                    
                    image_url = f"/theme_images/{filename}"
                    
                    print(f"   ✅ Saved: {filename}")
                    
                    results.append(ThemeGenerationResponse(
                        status="success",
                        world_id=world_id,
                        world_name=world.name,
                        image_url=image_url,
                        image_base64=image_base64,
                        en_prompt=en_prompt,
                    ))
                    generated_count += 1
                else:
                    raise Exception("No image_base64 in Kaggle response")
            
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results.append(ThemeGenerationResponse(
                    status="failed",
                    world_id=world_id,
                    world_name=world.name,
                    error=str(e),
                ))
        
        print(f"\n✅ Theme generation completed: {generated_count}/{len(WORLD_REGISTRY)} worlds")
        
        return BulkThemeGenerationResponse(
            success=generated_count > 0,
            total_worlds=len(WORLD_REGISTRY),
            generated_count=generated_count,
            results=results,
            timestamp=datetime.now().isoformat(),
        )
    
    except Exception as e:
        print(f"❌ Bulk theme generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generation-status")
async def get_generation_status():
    """Get the current configuration status of theme generation"""
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
