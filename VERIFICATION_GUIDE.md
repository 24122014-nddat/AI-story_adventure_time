# ✅ Quick Verification Guide

## Step 1: Start Kaggle Backend
```bash
# In notebook or terminal running gen-img.ipynb
# Make sure it's running on localhost:8000
```

## Step 2: Start ngrok Tunnel
```bash
ngrok http 8000
# Copy the HTTPS URL, e.g.: https://abc123.ngrok-free.dev
```

## Step 3: Update .env
```bash
# In your project root .env file
KAGGLE_API_URL=https://abc123.ngrok-free.dev
```

## Step 4: Start FastAPI Server
```bash
cd d:\hcmus\HK4\Tư duy tính toán cho TTNT\AI-story
python -m uvicorn app.main:app --reload
```

## Step 5: Test Image Generation

### Option A: Via Settings (routes_theme.py)
Open browser: `http://localhost:8000/`
1. Click ⚙️ button (top-right)
2. Settings modal opens
3. Click "🚀 Generate All Themes"
4. Watch progress bar
5. Close modal to see images

### Option B: Via curl (routes_theme.py)
```bash
curl -X POST http://localhost:8000/theme/generate-all-worlds \
  -H "Content-Type: application/json" \
  -d '{
    "summarize_model": "gemini-2.5-flash",
    "txt2img_model": "SDXL lightning",
    "steps": 4
  }'
```

### Option C: Via Debug Endpoint (routes_debug.py)
```bash
curl -X POST http://localhost:8000/debug/images/generate-all-worlds
```

### Option D: Check Status
```bash
curl http://localhost:8000/theme/generation-status
```

---

## Expected Output

### Server Logs Should Show:
```
🎨 Starting theme generation for all 7 worlds...
   Summarize Model: gemini-2.5-flash (stored for UI)
   Image Model: SDXL lightning (stored for UI)
   Steps: 4 (stored for UI)
   Using provider: KaggleProvider

🌍 Processing: Eldoria Tàn Tro
   Prompt: A dark fantasy landscape for Eldoria Tàn Tro...
   Style: gothic
   Calling image provider...
🎨 KaggleProvider.generate_image()
   Prompt: A dark fantasy landscape...
   Style: gothic
   Name: Eldoria Tàn Tro
   Calling: https://abc123.ngrok-free.dev/generate-world-theme
   Response status: success
   ✅ Saved to: eldoria_tn_tro_gothic.png

✅ Completed! Generated 7/7 world images
```

### Files Created:
```
generated_imgs/
└── theme_stories/
    ├── eldoria_tn_tro_gothic.png
    ├── cu_chu_huyn_mng_fantasy.png
    ├── vng_t_cui_tri_cyberpunk.png
    ├── bin_n_v_tn_cyberpunk.png
    ├── thnh_ph_khng_ngu_cyberpunk.png
    ├── min_t_linh_hn_fantasy.png
    └── vng_cc_bc_bng_gá_fantasy.png
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | Start Kaggle backend and ngrok |
| `Kaggle image generation failed` | Check ngrok URL is correct |
| `No image_base64 in response` | Kaggle backend may have crashed |
| `Failed to call Kaggle backend` | Check KAGGLE_API_URL in .env |
| `No such file` | `mkdir -p generated_imgs/theme_stories` |

---

## Key Changes Made

1. ✅ **config.py**: Changed KAGGLE_API_URL to base URL (removed `/generate-image`)
2. ✅ **kaggle_provider.py**: Now calls `/generate-world-theme` with correct parameters
3. ✅ **routes_theme.py**: Already correct, no changes needed
4. ✅ **routes_debug.py**: Now works through updated KaggleProvider

**Result**: Both `/theme/generate-all-worlds` and `/debug/images/generate-all-worlds` now work with the correct Kaggle backend endpoint.
