# 🚀 Theme Generation - Quick Reference Card

## For Developers

### Import & Initialize

**Backend**:
```python
# In app/main.py
from app.api.routes_theme import router as theme_router
app.include_router(theme_router)
```

**Frontend**:
```javascript
// In index.html, before closing </body>
<script src="./settings.js"></script>

// Initialize on page load (automatic)
document.addEventListener('DOMContentLoaded', initThemeGeneration);
```

---

## API Endpoints

### Generate All World Themes
```
POST /theme/generate-all-worlds
Content-Type: application/json

Body:
{
  "summarize_model": "gemini-2.5-flash" | "qwen-1.5b",
  "txt2img_model": "sdxl-lightning" | "gemini-imagen",
  "steps": 4 | 8
}

Response: 200 OK
{
  "success": true,
  "total_worlds": 7,
  "generated_count": 7,
  "results": [{ status, world_id, world_name, image_url, en_prompt, error? }],
  "timestamp": "ISO8601"
}
```

### Check Generation Status
```
GET /theme/generation-status

Response: 200 OK
{
  "total_worlds": 7,
  "generated_worlds": 7,
  "images": ["world_name_theme.png", ...],
  "last_updated": "ISO8601"
}
```

---

## Frontend Functions

### Settings Management
```javascript
// Load from localStorage
themeSettings.load();

// Save to localStorage
themeSettings.save();

// Get current settings
themeSettings.getAll();  // Returns: {summarizeModel, txt2imgModel, steps}

// Update single setting
themeSettings.set('summarizeModel', 'qwen-1.5b');
```

### Modal Control
```javascript
// Open settings modal
openSettingsModal();

// Close settings modal
closeSettingsModal();

// Load current settings into UI
loadSettingsUI();

// Update steps visibility based on model
updateStepsVisibility();
```

### Generation & Progress
```javascript
// Trigger generation
triggerThemeGeneration();

// Handle results (called automatically)
handleThemeGenerationResults(data);

// Add progress log entry
addProgressLog('Message', 'info|success|error');

// Update progress bar
updateProgressBar(current, total);

// Refresh world card images
updateWorldImages();
```

---

## Configuration

### Environment Variables
```bash
# .env file
KAGGLE_API_URL=https://onion-vertical-squash.ngrok-free.dev
```

### Supported Models

**Summarization**:
- `gemini-2.5-flash`: Fast, high-quality
- `qwen-1.5b`: Lightweight local

**Image Generation**:
- `sdxl-lightning`: Fast (4-8 steps)
- `gemini-imagen`: High-quality but slower

**Steps** (SDXL only):
- `4`: Fastest (~30-60s per image)
- `8`: Better quality (~60-120s per image)

---

## File Paths

### Generated Images
```
generated_imgs/
└── theme_stories/
    ├── eldoria_tn_tro_theme.png
    ├── cu_chu_huyn_mng_theme.png
    ├── vng_t_cui_tri_theme.png
    ├── bin_n_v_tn_theme.png
    ├── thnh_ph_khng_ngu_theme.png
    ├── min_t_linh_hn_theme.png
    └── vng_cc_bc_bng_gá_theme.png
```

### API Routes
```
GET  /theme/generation-status
POST /theme/generate-all-worlds
```

### Frontend Files
```
frontend/
├── settings.js           (Settings manager)
├── index.html            (Modal injected here)
└── shared.js             (API_BASE detection)
```

---

## Common Tasks

### Test if Endpoint Works
```bash
curl http://127.0.0.1:8000/theme/generation-status
```

### Check Generated Images
```bash
ls -la generated_imgs/theme_stories/
```

### View Settings in Console
```javascript
console.log(themeSettings.getAll());
```

### Clear Settings (Start Fresh)
```javascript
localStorage.removeItem('themeGenerationSettings');
location.reload();
```

### Get Progress in Console
```javascript
// Open DevTools Console during generation
// Progress logs will show automatically
```

### Access Image URL
```
http://127.0.0.1:8000/theme_images/{world_name}_theme.png
```

---

## Debugging Tips

### Backend Debug
```python
# In routes_theme.py
print(f"🚀 Generating {world.name}...")  # Check stdout
print(f"📝 Prompt: {prompt}")
print(f"🖼️ Response: {response}")
```

### Frontend Debug
```javascript
// In settings.js
console.log('🎨 Settings:', themeSettings.getAll());
console.log('📊 Results:', data);
console.log('🖼️ Images:', generatedImages);
```

### Network Debug
```javascript
// In browser DevTools
// Network tab → Filter 'theme'
// Check request/response headers and body
```

### Storage Debug
```javascript
// In browser DevTools Console
localStorage.getItem('themeGenerationSettings');
// Output: {"summarizeModel":"gemini-2.5-flash",...}
```

---

## Error Messages

### Backend Errors

```
❌ API returned 502
→ Solution: Check if Kaggle backend is running

❌ timeout during image generation
→ Solution: Kaggle API might be slow, wait or restart

❌ No such file or directory: generated_imgs/theme_stories/
→ Solution: mkdir -p generated_imgs/theme_stories/
```

### Frontend Errors

```
❌ Settings modal not found in DOM
→ Solution: Verify settings modal HTML was injected in index.html

❌ Cannot read property 'setItem' of undefined
→ Solution: Check if localStorage is available in browser

❌ Invalid model name: xyz
→ Solution: Only use: gemini-2.5-flash, qwen-1.5b, sdxl-lightning, gemini-imagen
```

---

## Performance Metrics

### Expected Times

| Operation | Time | Notes |
|-----------|------|-------|
| Generate 1 image (SDXL 4 steps) | 30-60s | First time |
| Generate 7 images | 3-7 min | All worlds combined |
| Cache hit (status check) | < 100ms | Subsequent calls |
| Modal open | < 50ms | UI response |
| Settings save | instant | localStorage |
| Progress update | real-time | UI refresh |

### Benchmarks

```javascript
// Measure generation time
const start = Date.now();
await triggerThemeGeneration();
console.log(`⏱️ Generation took ${Date.now() - start}ms`);
```

---

## Testing Snippets

### Test Settings Persistence
```javascript
// Step 1: Open DevTools Console
themeSettings.summarizeModel = 'qwen-1.5b';
themeSettings.save();

// Step 2: Reload page
location.reload();

// Step 3: Check console
console.log(themeSettings.summarizeModel);  // Should be 'qwen-1.5b'
```

### Test Generation with curl
```bash
curl -X POST http://127.0.0.1:8000/theme/generate-all-worlds \
  -H "Content-Type: application/json" \
  -d '{
    "summarize_model": "gemini-2.5-flash",
    "txt2img_model": "sdxl-lightning",
    "steps": 4
  }' \
  | jq '.'
```

### Test Image Loading
```bash
# Check if image is accessible
curl -I http://127.0.0.1:8000/theme_images/eldoria_tn_tro_theme.png
# Should return: HTTP/1.1 200 OK
```

---

## Integration Checklist

- [ ] routes_theme.py created
- [ ] schemas.py updated (3 new models)
- [ ] main.py updated (router registered)
- [ ] settings.js created
- [ ] index.html updated (modal + scripts)
- [ ] Modal CSS included
- [ ] Settings modal opened via gear icon
- [ ] Generation triggered successfully
- [ ] Progress tracked in UI
- [ ] Images saved to filesystem
- [ ] Images displayed on world cards
- [ ] Settings persist after refresh

---

## Rollback Instructions

If issues occur:

1. **Restore main.py**:
   ```python
   # Remove this line:
   from app.api.routes_theme import router as theme_router
   app.include_router(theme_router)
   ```

2. **Restore index.html**:
   ```html
   <!-- Remove: settings modal HTML -->
   <!-- Remove: settings.js script -->
   <!-- Remove: settings styles -->
   ```

3. **Delete new files**:
   ```bash
   rm app/api/routes_theme.py
   rm frontend/settings.js
   ```

4. **Restart server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

---

**Last Updated**: 2026-04-21  
**Status**: ✅ Production Ready  
**Maintained By**: AI Development Team
