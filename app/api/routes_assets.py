"""
Unified AI Image Asset Generation Routes
Handles generation of images for Themes, NPCs, and Scenes with configurable AI models
"""
from __future__ import annotations

import os
import re
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.api.dependencies import get_image_service
from app.domain.schemas import (
    UnifiedAssetGenerationRequest,
    AssetGenerationResponse,
    BulkAssetGenerationResponse,
)
from app.services.asset_prompt_builders import AssetPromptBuilder
from app.services.world_definitions import WORLD_REGISTRY
from app.services.image_service import ImageService

router = APIRouter(prefix="/assets", tags=["unified-asset-generation"])


# ============= CONFIGURATION CONSTANTS =============
# Default values for the unified asset system
DEFAULT_CONFIG = {
    "summarize_model": "qwen-1.5b",
    "txt2img_model": "sdxl-lightning",
    "steps": 8,
}

# Asset type directories
ASSET_DIRECTORIES = {
    "theme": "generated_imgs/theme_stories",
    "npc": "generated_imgs/npcs",
    "scene": "generated_imgs/scenes",
}


# ============= HELPER FUNCTIONS =============

def sanitize_filename(text: str) -> str:
    """
    Convert text to safe filename while preserving Vietnamese diacritics
    
    Args:
        text: Input text to sanitize
    
    Returns:
        Safe filename without special characters
    """
    text = text.lower().strip()
    text = text.replace(" ", "_")
    # Remove only filesystem-dangerous characters
    text = re.sub(r'[/\\:*?"<>|]', '', text)
    return re.sub(r'_+', '_', text)


def get_asset_directory(asset_type: str) -> Path:
    """
    Get the directory for a specific asset type
    Creates it if it doesn't exist
    
    Args:
        asset_type: "theme", "npc", or "scene"
    
    Returns:
        Path object for asset directory
    """
    if asset_type not in ASSET_DIRECTORIES:
        raise ValueError(f"Unknown asset type: {asset_type}")
    
    dir_path = Path(ASSET_DIRECTORIES[asset_type])
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generate_asset_filename(
    asset_type: str,
    asset_id: str,
    asset_name: str,
) -> str:
    """
    Generate standardized filename for assets
    
    Format: {asset_type}_{asset_id}_{safe_name}.png
    
    Args:
        asset_type: "theme", "npc", or "scene"
        asset_id: world_id, npc_id, or scene_id
        asset_name: Display name
    
    Returns:
        Filename string (without path)
    """
    safe_id = sanitize_filename(asset_id)
    safe_name = sanitize_filename(asset_name)
    return f"{asset_type}_{safe_id}_{safe_name}.png"


async def call_kaggle_backend(
    prompt: str,
    asset_name: str,
    summarize_model: str,
    txt2img_model: str,
    steps: int,
    kaggle_api_url: str,
) -> dict:
    """
    Call the Kaggle FastAPI backend for unified asset generation
    
    Args:
        prompt: Visual description for image generation
        asset_name: Name of the asset (for logging)
        summarize_model: "gemini-2.5-flash" or "qwen-1.5b"
        txt2img_model: "sdxl-lightning" or "gemini-imagen"
        steps: Inference steps (4 or 8)
        kaggle_api_url: Backend URL (e.g., https://xxx.ngrok.io)
    
    Returns:
        Response dict with status, image_base64, en_prompt, etc.
    
    Raises:
        Exception: If API call fails
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            payload = {
                "prompt": prompt,
                "world_name": asset_name,  # Reuse field for generic asset name
                "summarize_model": summarize_model,
                "txt2img_model": txt2img_model,
                "step": steps,
            }
            
            response = await client.post(
                f"{kaggle_api_url}/generate-world-theme",
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"Kaggle API returned {response.status_code}: {response.text}"
                )
            
            return response.json()
    
    except Exception as e:
        raise Exception(f"Failed to call Kaggle backend: {str(e)}")


def save_asset_image(
    asset_type: str,
    asset_id: str,
    asset_name: str,
    image_base64: str,
) -> tuple[str, str]:
    """
    Save image to local storage with automatic overwriting
    
    Args:
        asset_type: "theme", "npc", or "scene"
        asset_id: world_id, npc_id, or scene_id
        asset_name: Display name
        image_base64: Base64 encoded image data
    
    Returns:
        Tuple of (file_path, relative_url)
    
    Raises:
        Exception: If image save fails
    """
    try:
        # Get asset directory
        asset_dir = get_asset_directory(asset_type)
        
        # Generate filename
        filename = generate_asset_filename(asset_type, asset_id, asset_name)
        file_path = asset_dir / filename
        
        # Decode and save image (overwrites existing)
        image_data = base64.b64decode(image_base64)
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Return both absolute and relative paths
        relative_url = f"/{ASSET_DIRECTORIES[asset_type]}/{filename}".replace("\\", "/")
        return str(file_path), relative_url
    
    except Exception as e:
        raise Exception(f"Failed to save asset image: {str(e)}")


# ============= MAIN ROUTES =============

@router.post(
    "/generate",
    response_model=AssetGenerationResponse,
    summary="Generate a single asset (Theme, NPC, or Scene)"
)
async def generate_single_asset(
    request: UnifiedAssetGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
) -> AssetGenerationResponse:
    """
    Generate a single image asset with unified configuration
    
    **Supported Asset Types:**
    - `theme`: World theme images (requires world_id)
    - `npc`: NPC character images (requires npc_name, npc_description)
    - `scene`: Scene/event images (requires scene_description)
    
    **Default Configuration:**
    - Summarization: `qwen-1.5b` (lightweight, fast)
    - Image Generation: `sdxl-lightning` (fast, 8-step default)
    - Steps: `8` (balanced quality/speed)
    
    **Usage Examples:**
    ```
    # Generate theme for world
    POST /assets/generate
    {
      "asset_type": "theme",
      "world_id": "dark_fantasy"
    }
    
    # Generate NPC portrait
    POST /assets/generate
    {
      "asset_type": "npc",
      "npc_name": "Eldric",
      "npc_description": "Tall, scarred warrior with red eyes, stern face"
    }
    
    # Generate scene
    POST /assets/generate
    {
      "asset_type": "scene",
      "scene_description": "Ancient temple ruins in moonlight"
    }
    ```
    """
    try:
        asset_type = request.asset_type.lower().strip()
        
        print(f"\n{'='*60}")
        print(f"🎨 Asset Generation Request")
        print(f"{'='*60}")
        print(f"   Type: {asset_type}")
        print(f"   Summarize: {request.summarize_model}")
        print(f"   Image Model: {request.txt2img_model}")
        print(f"   Steps: {request.steps}")
        
        # ===== STEP 1: VALIDATE & BUILD PROMPT =====
        
        prompt = None
        asset_id = None
        asset_name = None
        world_context = None
        
        if asset_type == "theme":
            # Theme: Requires world_id
            if not request.world_id:
                raise ValueError("theme asset type requires 'world_id'")
            
            if request.world_id not in WORLD_REGISTRY:
                raise ValueError(f"Unknown world_id: {request.world_id}")
            
            world_context = WORLD_REGISTRY[request.world_id]
            asset_id = request.world_id
            asset_name = world_context.name
            
            prompt = AssetPromptBuilder.build_theme_prompt(world_context)
            print(f"   World: {asset_name}")
        
        elif asset_type == "npc":
            # NPC: Requires name and description
            if not request.npc_name or not request.npc_description:
                raise ValueError("npc asset type requires 'npc_name' and 'npc_description'")
            
            asset_id = sanitize_filename(request.npc_name)
            asset_name = request.npc_name
            
            # Get world context if provided (for styling consistency)
            if request.world_id and request.world_id in WORLD_REGISTRY:
                world_context = WORLD_REGISTRY[request.world_id]
            
            prompt = AssetPromptBuilder.build_npc_prompt(
                request.npc_name,
                request.npc_description,
                world_context
            )
            print(f"   NPC: {asset_name}")
        
        elif asset_type == "scene":
            # Scene: Requires description
            if not request.scene_description:
                raise ValueError("scene asset type requires 'scene_description'")
            
            asset_id = f"scene_{datetime.now().timestamp()}"
            asset_name = request.scene_description[:50]  # First 50 chars as name
            
            # Get world context if provided (for styling consistency)
            if request.world_id and request.world_id in WORLD_REGISTRY:
                world_context = WORLD_REGISTRY[request.world_id]
            
            prompt = AssetPromptBuilder.build_scene_prompt(
                request.scene_description,
                request.plot_context,
                world_context
            )
            print(f"   Scene: {asset_name}")
        
        else:
            raise ValueError(f"Unsupported asset_type: {asset_type}")
        
        print(f"   Prompt: {prompt[:100]}...")
        
        # ===== STEP 2: CALL KAGGLE BACKEND =====
        
        kaggle_api_url = os.getenv(
            "KAGGLE_API_URL",
            "https://onion-vertical-squash.ngrok-free.dev"
        )
        
        print(f"   Calling Kaggle API...")
        kaggle_response = await call_kaggle_backend(
            prompt=prompt,
            asset_name=asset_name,
            summarize_model=request.summarize_model,
            txt2img_model=request.txt2img_model,
            steps=request.steps,
            kaggle_api_url=kaggle_api_url,
        )
        
        if kaggle_response.get("status") != "success":
            raise Exception(
                f"Kaggle API failed: {kaggle_response.get('error', 'Unknown error')}"
            )
        
        # ===== STEP 3: SAVE IMAGE LOCALLY =====
        
        en_prompt = kaggle_response.get("en_prompt", "")
        image_base64 = kaggle_response.get("image_base64", "")
        
        if not image_base64:
            raise Exception("No image_base64 in Kaggle response")
        
        file_path, relative_url = save_asset_image(
            asset_type,
            asset_id,
            asset_name,
            image_base64
        )
        
        filename = Path(file_path).name
        print(f"   ✅ Saved: {filename}")
        print(f"{'='*60}\n")
        
        # ===== STEP 4: RETURN RESPONSE =====
        
        return AssetGenerationResponse(
            status="success",
            asset_type=asset_type,
            asset_id=asset_id,
            asset_name=asset_name,
            image_url=relative_url,
            image_base64=image_base64,
            en_prompt=en_prompt,
            file_path=file_path,
            file_name=filename,
        )
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print(f"{'='*60}\n")
        return AssetGenerationResponse(
            status="failed",
            asset_type=request.asset_type,
            asset_id="unknown",
            asset_name="unknown",
            error=str(e),
        )


@router.post(
    "/generate-all-themes",
    response_model=BulkAssetGenerationResponse,
    summary="Generate theme images for all 7 worlds"
)
async def generate_all_themes(
    request: UnifiedAssetGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
) -> BulkAssetGenerationResponse:
    """
    Generate theme images for ALL 7 worlds with unified configuration
    
    Uses default configuration if not specified:
    - Summarization: `qwen-1.5b`
    - Image Model: `sdxl-lightning`
    - Steps: `8`
    """
    try:
        print(f"\n{'='*70}")
        print(f"🎨 BULK THEME GENERATION - All 7 Worlds")
        print(f"{'='*70}")
        print(f"   Summarize: {request.summarize_model}")
        print(f"   Image Model: {request.txt2img_model}")
        print(f"   Steps: {request.steps}")
        
        results = []
        generated_count = 0
        
        # Iterate through all 7 worlds
        for world_id, world in WORLD_REGISTRY.items():
            try:
                print(f"\n   🌍 {world.name}...", end=" ")
                
                # Create request for each world
                world_request = UnifiedAssetGenerationRequest(
                    asset_type="theme",
                    world_id=world_id,
                    summarize_model=request.summarize_model,
                    txt2img_model=request.txt2img_model,
                    steps=request.steps,
                )
                
                # Generate asset
                response = await generate_single_asset(world_request, image_service)
                
                if response.status == "success":
                    print("✅")
                    generated_count += 1
                else:
                    print(f"❌ {response.error}")
                
                results.append(response)
            
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results.append(
                    AssetGenerationResponse(
                        status="failed",
                        asset_type="theme",
                        asset_id=world_id,
                        asset_name=world.name,
                        error=str(e),
                    )
                )
        
        print(f"\n{'='*70}")
        print(f"✅ Theme generation completed: {generated_count}/{len(WORLD_REGISTRY)}")
        print(f"{'='*70}\n")
        
        return BulkAssetGenerationResponse(
            success=generated_count > 0,
            asset_type="theme",
            total_count=len(WORLD_REGISTRY),
            generated_count=generated_count,
            results=results,
            timestamp=datetime.now().isoformat(),
        )
    
    except Exception as e:
        print(f"❌ Bulk generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generation-status/{asset_type}", summary="Get asset generation status")
async def get_asset_generation_status(asset_type: str):
    """
    Get status of generated assets for a specific type
    
    **Asset Types:** theme, npc, scene
    """
    try:
        asset_type = asset_type.lower().strip()
        
        asset_dir = get_asset_directory(asset_type)
        images = list(asset_dir.glob("*.png"))
        
        return {
            "asset_type": asset_type,
            "total_generated": len(images),
            "images": [img.name for img in images],
            "directory": str(asset_dir),
            "last_updated": (
                datetime.fromtimestamp(
                    max(img.stat().st_mtime for img in images)
                ).isoformat()
                if images
                else None
            ),
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
