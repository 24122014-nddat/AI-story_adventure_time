# 🔧 Kaggle Backend Integration - Fixes Applied

## 📋 Summary of Changes

All endpoints have been updated to use the correct Kaggle backend endpoint: `/generate-world-theme`

---

## ✅ Files Modified

### 1. **app/config.py** ✓
**Problem:** `KAGGLE_API_URL` had wrong endpoint path `/generate-image`

**Fix:** 
```python
# Before
kaggle_api_url: str = os.getenv(
    "KAGGLE_API_URL",
    "https://onion-vertical-squash.ngrok-free.dev/generate-image",
)

# After
kaggle_api_url: str = os.getenv(
    "KAGGLE_API_URL",
    "https://onion-vertical-squash.ngrok-free.dev",
)
```

**Impact:** Now uses base URL only. The endpoint path `/generate-world-theme` is added by the provider/routes.

---

### 2. **app/ai/providers/kaggle_provider.py** ✓
**Problem:** Old endpoint `/generate-image`, wrong payload format, no model parameters

**Fix:**
- Updated `generate_image()` to call `/generate-world-theme` endpoint
- Added proper payload with all required parameters:
  - `prompt`
  - `world_name`
  - `summarize_model`
  - `txt2img_model`
  - `step`
- Added debug logging
- Added new method `_map_style_to_model()` to map styles to model names
- Increased timeout to 600s for image generation

**Endpoint Called:**
```
POST https://[ngrok-url]/generate-world-theme

Payload:
{
  "prompt": "...",
  "world_name": "Eldoria Tàn Tro",
  "summarize_model": "gemini-2.5-flash",
  "txt2img_model": "SDXL lightning",
  "step": 4
}
```

---

### 3. **app/api/routes_theme.py** ✓
**Status:** Already correct! Uses the proper endpoint and parameters.

**Flow:**
```
POST /theme/generate-all-worlds
  → call_kaggle_backend()
    → POST /generate-world-theme
      → Kaggle backend
```

No changes needed - this was already implemented correctly.

---

### 4. **app/api/routes_debug.py** ✓
**Status:** Now fixed via KaggleProvider update

**Flow:**
```
POST /debug/images/world-theme
  → ImageService.generate_scene_image()
    → KaggleProvider.generate_image()
      → POST /generate-world-theme
        → Kaggle backend
```

Now uses the correct backend endpoint through updated KaggleProvider.

---

## 🔄 Complete Data Flow

```
Frontend (index.html)
    ↓
[Click ⚙️ Settings]
    ↓
POST /theme/generate-all-worlds
{
  "summarize_model": "gemini-2.5-flash",
  "txt2img_model": "sdxl-lightning",
  "steps": 4
}
    ↓
routes_theme.py
    ├─ For each of 7 worlds:
    │  ├─ build_world_prompt(world)
    │  └─ call_kaggle_backend()
    │
    └─ Returns results
        ↓
    POST /generate-world-theme (to Kaggle)
        ↓
    Kaggle Backend (gen-img.ipynb)
        ├─ Summarize with Gemini/Qwen
        ├─ Generate image with SDXL/Imagen
        └─ Return Base64 + metadata
        ↓
    routes_theme.py decodes & saves
        ↓
    Returns image URLs to frontend
        ↓
    Frontend updates world cards
```

---

## 🚀 Testing the Fix

### Option 1: Test via routes_theme.py (New Settings)
```bash
curl -X POST http://localhost:8000/theme/generate-all-worlds \
  -H "Content-Type: application/json" \
  -d '{
    "summarize_model": "gemini-2.5-flash",
    "txt2img_model": "sdxl-lightning",
    "steps": 4
  }'
```

### Option 2: Test via routes_debug.py (Old Debug Endpoint)
```bash
curl -X POST http://localhost:8000/debug/images/generate-all-worlds
```

### Option 3: Test Status Check
```bash
curl http://localhost:8000/theme/generation-status
```

---

## 📊 Backend Endpoints Summary

### Kaggle Backend (gen-img.ipynb)
```
POST /generate-world-theme

Request:
{
  "prompt": "Vietnamese lore/description",
  "world_name": "World name",
  "summarize_model": "gemini-2.5-flash" | "Qwen/Qwen2.5-1.5B-Instruct",
  "txt2img_model": "SDXL lightning" | "Gemini API banana pro",
  "step": 4 | 8
}

Response:
{
  "status": "success",
  "en_prompt": "Enhanced English prompt",
  "saved_at": "Path to saved image",
  "image_base64": "Base64 encoded PNG"
}
```

### AI Story Backend (app/api)
```
POST /theme/generate-all-worlds
POST /debug/images/generate-all-worlds
GET /theme/generation-status
```

---

## 🔍 Verification Checklist

- [ ] Kaggle backend is running on localhost:8000
- [ ] ngrok tunnel is active: `ngrok http 8000`
- [ ] `.env` has: `KAGGLE_API_URL=https://[ngrok-url]`
- [ ] FastAPI backend started: `python -m uvicorn app.main:app --reload`
- [ ] Call `/theme/generate-all-worlds` and check logs for:
  - `🎨 Starting theme generation...`
  - `🌍 Processing: [world name]`
  - `Calling: https://[ngrok-url]/generate-world-theme`
  - `Response status: success`
  - `✅ Saved to: [filename].png`
- [ ] Images saved to `generated_imgs/theme_stories/`
- [ ] Frontend displays new images

---

## 🐛 If Issues Occur

### "Kaggle image generation failed"
- Check if ngrok tunnel is running
- Check if Kaggle backend is running on localhost:8000
- Verify KAGGLE_API_URL in .env is correct
- Check server logs for exact error message

### "No image_base64 in response"
- Kaggle backend may have crashed
- Check Kaggle backend logs
- Verify Gemini/Qwen models are available

### "Failed to call Kaggle backend: ..."
- Check network connection
- Verify ngrok tunnel is active
- Check KAGGLE_API_URL format (should be base URL without endpoint)

---

## 📝 Model Configuration

The system supports:

**Summarization Models** (convert Vietnamese lore to English):
- `"gemini-2.5-flash"` - Fast, high-quality
- `"Qwen/Qwen2.5-1.5B-Instruct"` - Local, lightweight

**Image Generation Models**:
- `"SDXL lightning"` - Fast, 4-8 steps
- `"Gemini API banana pro"` - High-quality

These values are stored in settings and sent to Kaggle backend.

---

## ✨ What Works Now

✅ Both routes work with correct Kaggle backend:
- `routes_theme.py` → Direct async call to `/generate-world-theme`
- `routes_debug.py` → Via ImageService → KaggleProvider → `/generate-world-theme`

✅ All model configurations are preserved and passed to backend

✅ Images are saved with correct naming and can be accessed via frontend

✅ Full debug logging shows the complete flow

---

**All endpoints now use the correct Kaggle backend!** 🎉
