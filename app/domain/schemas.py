from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class StartGameRequest(BaseModel):
    world_id: str = Field(..., min_length=1)
    player_name: str = Field(..., min_length=1, max_length=50)

    background: str = Field(..., min_length=1)
    personality_traits: List[str] = []
    virtues: List[str] = []
    flaws: List[str] = []
    fears: List[str] = []
    goals: List[str] = []


class StartGameResponse(BaseModel):
    session_id: str
    message: str


class ActionRequest(BaseModel):
    session_id: str
    action_type: str
    content: str = Field(..., min_length=1)


class TurnResponse(BaseModel):
    narrative: str
    choices: List[str]
    state_changes: List[str]


class GameStateResponse(BaseModel):
    session_id: str
    world_name: str
    player_name: str
    location: str
    current_objective: str
    turn_count: int
    hp: int
    stamina: int
    stress: int


class ImagesGenerationRequest(BaseModel):
    """Request để sinh hình ảnh"""

    session_id: Optional[str] = None  # Để optional vì không cần cho scene generic
    style: Optional[str] = None  # Nếu None sẽ auto-detect
    description: Optional[str] = None  # Cho scene generic


class UnifiedThemeGenerationRequest(BaseModel):
    """Unified request để sinh theme images cho tất cả 7 worlds với configurable models"""
    
    summarize_model: str = Field(
        default="gemini-2.5-flash",
        description="Model dùng để tóm tắt & dịch: 'gemini-2.5-flash' hoặc 'qwen-1.5b'"
    )
    txt2img_model: str = Field(
        default="sdxl-lightning",
        description="Model dùng để sinh ảnh: 'sdxl-lightning' hoặc 'gemini-imagen'"
    )
    steps: int = Field(
        default=4,
        description="Số bước inference cho SDXL: 4 hoặc 8"
    )


class ThemeGenerationResponse(BaseModel):
    """Response từ theme generation"""
    
    status: str  # "success" hoặc "failed"
    world_id: str
    world_name: str
    image_url: Optional[str] = None  # URL hoặc path tới ảnh
    image_base64: Optional[str] = None  # Base64 encoded ảnh
    en_prompt: Optional[str] = None  # English prompt được tạo ra
    error: Optional[str] = None  # Error message nếu failed


class BulkThemeGenerationResponse(BaseModel):
    """Response từ bulk generation cho tất cả 7 worlds"""
    
    success: bool
    total_worlds: int
    generated_count: int
    results: List[ThemeGenerationResponse]
    timestamp: str


# ============= UNIFIED AI IMAGE ASSET SYSTEM =============

class UnifiedAssetGenerationRequest(BaseModel):
    """
    Unified request để sinh hình ảnh cho Themes, NPCs, và Scenes
    
    Asset Types:
    - "theme": World theme images (sử dụng world_id + notable_region)
    - "npc": NPC character images (sử dụng npc_description + world_context)
    - "scene": Scene/event images (sử dụng scene_description + plot_context)
    """
    
    # ===== REQUIRED =====
    asset_type: str = Field(
        ..., 
        description="Asset type: 'theme', 'npc', or 'scene'"
    )
    
    # ===== AI MODEL CONFIGURATION (Global Defaults) =====
    summarize_model: str = Field(
        default="qwen-1.5b",
        description="Summarization model: 'qwen-1.5b' (DEFAULT) or 'gemini-2.5-flash'"
    )
    txt2img_model: str = Field(
        default="sdxl-lightning",
        description="Image generation model: 'sdxl-lightning' (DEFAULT) or 'gemini-imagen'"
    )
    steps: int = Field(
        default=8,
        description="SDXL inference steps (DEFAULT: 8). Options: 4 or 8"
    )
    
    # ===== ASSET-SPECIFIC DATA =====
    
    # For Theme Assets
    world_id: Optional[str] = None
    world_name: Optional[str] = None
    
    # For NPC Assets
    npc_name: Optional[str] = None
    npc_description: Optional[str] = None  # Personality, appearance, role
    
    # For Scene Assets
    scene_description: Optional[str] = None
    plot_context: Optional[str] = None  # Narrative context


class AssetGenerationResponse(BaseModel):
    """Response từ unified asset generation"""
    
    status: str  # "success" hoặc "failed"
    asset_type: str  # "theme", "npc", "scene"
    asset_id: str  # world_id, npc_name, hoặc scene_id
    asset_name: str  # Display name
    
    # ===== SUCCESS DATA =====
    image_url: Optional[str] = None  # URL tới ảnh
    image_base64: Optional[str] = None  # Base64 encoded image
    en_prompt: Optional[str] = None  # English prompt được sử dụng
    
    # ===== METADATA =====
    file_path: Optional[str] = None  # Local file path
    file_name: Optional[str] = None  # Filename generated
    
    # ===== ERROR DATA =====
    error: Optional[str] = None


class BulkAssetGenerationResponse(BaseModel):
    """Response từ bulk asset generation (e.g., all themes, all NPCs)"""
    
    success: bool
    asset_type: str
    total_count: int
    generated_count: int
    results: List[AssetGenerationResponse]
    timestamp: str