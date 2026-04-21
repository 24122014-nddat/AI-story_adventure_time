from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes_debug import router as debug_router
from app.api.routes_game import router as game_router
from app.api.routes_theme import router as theme_router
from app.api.routes_assets import router as assets_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend cho đồ án AI Story Adventure",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router)
app.include_router(debug_router)
app.include_router(theme_router)
app.include_router(assets_router)  # New unified asset generation routes

# Mount static files for generated images
generated_imgs_dir = os.path.join(os.path.dirname(__file__), "..", "generated_imgs")
os.makedirs(generated_imgs_dir, exist_ok=True)
app.mount("/generated_imgs", StaticFiles(directory=generated_imgs_dir), name="generated_imgs")

# Mount theme_stories subfolder directly for easier frontend access
theme_stories_dir = os.path.join(generated_imgs_dir, "theme_stories")
os.makedirs(theme_stories_dir, exist_ok=True)
app.mount("/theme_images", StaticFiles(directory=theme_stories_dir), name="theme_images")


# Mount frontend files at specific path first, then root
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

# Route to serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

# Route to serve create-character.html 
@app.get("/create-character.html")
async def serve_create_character():
    return FileResponse(os.path.join(frontend_dir, "create-character.html"))

# Route to serve game.html
@app.get("/game.html")
async def serve_game():
    return FileResponse(os.path.join(frontend_dir, "game.html"))

# Mount remaining static frontend files
app.mount("", StaticFiles(directory=frontend_dir), name="frontend")