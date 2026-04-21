# AI-story_adventure_time

# 🚀 Getting Started - Theme Generation Feature

## What You Got

A complete **Theme Generation system** that lets users:
- Configure which AI models to use (Gemini/Qwen, SDXL/Gemini)
- Generate unique images for all 7 worlds
- Track progress in real-time
- Persist settings across page reloads

## 3-Step Quick Start

### Step 1: Start the Backend (2 terminals needed)

**Terminal 1** - FastAPI Server:
```bash
cd d:\hcmus\HK4\Tư duy tính toán cho TTNT\AI-story
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2** - Kaggle API Tunnel (ngrok):
```bash
ngrok http 8000
# Copy the HTTPS URL, example: https://onion-vertical-squash.ngrok-free.dev
```

Update `.env` file:
```
KAGGLE_API_URL=https://onion-vertical-squash.ngrok-free.dev
```

### Step 2: Open Browser
```
http://127.0.0.1:8000/
```

You should see:
- World selection page with 7 world cards
- ⚙️ button in top-right (new!)

### Step 3: Test Theme Generation

1. Click ⚙️ button → Settings modal opens
2. Keep default settings or change them
3. Click **"🚀 Generate All Themes"**
4. Watch progress bar fill (takes 2-5 min first time)
5. Close modal → See updated world images!

## What Changed

### New Gear Icon Button
```
┌─────────────────────────────┐
│ [Tiếp tục] [🌙 Chế độ] [⚙️] │ ← NEW!
└─────────────────────────────┘
```

### New Settings Modal
```
┌──────────────────────────────────┐
│ 🎨 Theme Generation Settings [×] │
├──────────────────────────────────┤
│ 📝 Summarization Model:          │
│ [▼ Gemini / Qwen]                │
│                                  │
│ 🖼️ Image Generation Model:       │
│ [▼ SDXL / Gemini Imagen]         │
│                                  │
│ ⚡ Steps: [▼ 4 / 8]              │
│                                  │
│ [Generate] [Close]               │
│                                  │
│ Progress bar will appear here... │
└──────────────────────────────────┘
```

## Expected Results

### First Run (Cold Cache)
- ⏱️ Time: 2-5 minutes
- 📊 Progress: Real-time progress bar
- 🖼️ Result: 7 unique world images generated and displayed

### Subsequent Runs (Hot Cache)
- ⏱️ Time: < 100ms
- 📊 Progress: Instant
- 🖼️ Result: Images already cached, no regeneration needed

## Verify It Works

### Check 1: Gear Button Visible
```
✅ Click ⚙️ button
✅ Modal opens and closes smoothly
```

### Check 2: Settings Save
```
1. Change dropdown values
2. Refresh page (F5)
3. Open modal again
4. Settings should still be there ✅
```

### Check 3: Generation Works
```
1. Click "Generate All Themes"
2. Progress bar should fill
3. Images appear on world cards
4. Check folder: generated_imgs/theme_stories/
```

### Check 4: Images Exist
```bash
# In terminal, check generated files
ls -la generated_imgs/theme_stories/
# Should show: eldoria_tn_tro_theme.png, etc.
```

## Files You Should Know About

### New Code Files
- `app/api/routes_theme.py` - Backend routes
- `frontend/settings.js` - Frontend logic
- Updates in `index.html` - Modal UI

### Documentation
- `DELIVERY_SUMMARY.md` - What was delivered
- `TESTING_CHECKLIST.md` - How to test
- `QUICK_REFERENCE.md` - Code reference
- `THEME_GENERATION_GUIDE.md` - Complete guide

## Common Issues & Fixes

### "⚙️ Button not showing"
```javascript
// In browser console (F12)
console.log(document.querySelector('.gear-icon-btn'));
// Should return the button element, not null
```
**Fix**: Hard refresh (Ctrl+Shift+R)

### "Modal won't open"
```javascript
// In console, try manually
openSettingsModal();
// Should open modal if settings.js loaded correctly
```
**Fix**: Check Network tab to ensure settings.js loaded

### "Generation takes forever"
- First generation is normal: 2-5 minutes
- Check server logs for errors
- Ensure Kaggle API (ngrok tunnel) is running

### "Images not showing"
```bash
# Verify files exist
ls -la generated_imgs/theme_stories/
```
**Fix**: Run generation again, wait for completion

## Next Steps

### To Test Thoroughly
1. Follow **TESTING_CHECKLIST.md** (30 minutes)
2. Test each endpoint with curl
3. Verify all 7 worlds generate

### To Deploy
1. Ensure both servers (FastAPI + Kaggle) are ready
2. Run smoke test (5 minutes)
3. Deploy to production

### To Customize
1. Edit model options in `index.html` modal
2. Change default values in `settings.js`
3. Add new summarization models in backend

## API Endpoints (For Developers)

### Check Status
```bash
curl http://127.0.0.1:8000/theme/generation-status
```

### Generate All Themes
```bash
curl -X POST http://127.0.0.1:8000/theme/generate-all-worlds \
  -H "Content-Type: application/json" \
  -d '{
    "summarize_model": "gemini-2.5-flash",
    "txt2img_model": "sdxl-lightning",
    "steps": 4
  }'
```

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Open DevTools | F12 |
| Hard Refresh | Ctrl+Shift+R |
| Clear Cache | Ctrl+Shift+Delete |
| Browser Console | F12 → Console |
| Network Tab | F12 → Network |

## Support

### Documentation
- **Overview**: DELIVERY_SUMMARY.md
- **Testing**: TESTING_CHECKLIST.md
- **API**: THEME_GENERATION_GUIDE.md
- **Reference**: QUICK_REFERENCE.md

### Debug Info
1. Open browser DevTools (F12)
2. Check Console for errors
3. Check Network tab for failed requests
4. Check server terminal for Python errors

### Quick Troubleshoot
```javascript
// In browser console, check all systems:
console.log('Settings:', themeSettings.getAll());
console.log('API Base:', API_BASE);
console.log('Modal:', !!document.getElementById('settingsModal'));
console.log('Button:', !!document.querySelector('.gear-icon-btn'));
```

## That's It! 🎉

You now have a fully functional Theme Generation system.

**Next**: Run the TESTING_CHECKLIST.md to verify everything works perfectly!
