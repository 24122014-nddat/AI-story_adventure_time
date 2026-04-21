# 🧪 Theme Generation Feature - Testing Checklist

## Pre-Flight Checks

### Backend Setup
- [ ] FastAPI server running on port 8000
  ```bash
  python -m uvicorn app.main:app --reload
  ```
- [ ] Kaggle API backend running (ngrok tunnel active)
  ```bash
  ngrok http 8000
  ngrok copy URL to .env as KAGGLE_API_URL
  ```
- [ ] Environment variables configured
  - [ ] `KAGGLE_API_URL` set in `.env`
  - [ ] `generated_imgs/` directory exists
  - [ ] `generated_imgs/theme_stories/` directory exists

### Frontend Setup
- [ ] Browser cache cleared (DevTools → Application → Clear)
- [ ] localStorage cleared (if upgrading from old version)
- [ ] Frontend served from `http://127.0.0.1:8000` (not different port)

---

## Unit Tests

### Backend Endpoints

#### 1. Status Endpoint
```bash
# Expected: Returns list of generated images (may be empty)
curl http://127.0.0.1:8000/theme/generation-status
```
- [ ] Response status: 200 OK
- [ ] Response includes `total_worlds: 7`
- [ ] Response includes empty `images: []` array initially

#### 2. Generation Endpoint
```bash
# Expected: Generates all 7 world theme images
curl -X POST http://127.0.0.1:8000/theme/generate-all-worlds \
  -H "Content-Type: application/json" \
  -d '{
    "summarize_model": "gemini-2.5-flash",
    "txt2img_model": "sdxl-lightning",
    "steps": 4
  }'
```
- [ ] Response status: 200 OK
- [ ] Response includes `success: true`
- [ ] Response includes `generated_count: 7`
- [ ] Each result has `status: "success"`
- [ ] Each result includes `image_url` (e.g., `/theme_images/...`)
- [ ] Each result includes `en_prompt` (descriptive)

#### 3. Image Files
```bash
# Expected: 7 PNG files in the right directory
ls -la generated_imgs/theme_stories/
```
- [ ] 7 files exist: `{world_name}_theme.png`
- [ ] File sizes > 0 (not empty)
- [ ] File permissions readable
- [ ] Files are valid PNG format

---

## Integration Tests

### Frontend UI

#### 1. World Selection Page Load
1. [ ] Navigate to `http://127.0.0.1:8000/`
2. [ ] World selection page loads
3. [ ] ⚙️ "Themes" button visible in top-right (next to 🌙 Mode)
4. [ ] 7 world cards display
5. [ ] World card titles in Vietnamese

#### 2. Settings Modal

**Open Modal**:
1. [ ] Click ⚙️ button
2. [ ] Modal appears with overlay
3. [ ] Modal is centered on screen
4. [ ] Modal has visible close [×] button

**Model Selection**:
1. [ ] "📝 Summarization Model" dropdown shows:
   - [ ] "Gemini 2.5 Flash" option
   - [ ] "Qwen 1.5B" option
2. [ ] "🖼️ Image Generation Model" dropdown shows:
   - [ ] "SDXL Lightning" option
   - [ ] "Gemini Imagen" option
3. [ ] "⚡ SDXL Inference Steps" dropdown shows:
   - [ ] "4 Steps (Fastest)" option
   - [ ] "8 Steps (Balanced)" option
   - [ ] Visible only when SDXL Lightning selected

**Settings Persistence**:
1. [ ] Change model selections
2. [ ] Close modal (click [×])
3. [ ] Open modal again (click ⚙️)
4. [ ] Previous selections are still there
5. [ ] Refresh page (F5)
6. [ ] Open modal again
7. [ ] Selections persist after refresh (localStorage working)

#### 3. Generation Flow

**Start Generation**:
1. [ ] Keep default settings (Gemini + SDXL + 4 steps)
2. [ ] Click "🚀 Generate All Themes" button
3. [ ] Button becomes disabled and shows "⏳ Generating..."
4. [ ] Progress bar appears
5. [ ] Progress log section appears

**Monitor Progress**:
1. [ ] Progress bar shows 0% initially
2. [ ] Progress log shows timestamps for each world
3. [ ] Entries like "✅ Eldoria Tàn Tro: Generated successfully"
4. [ ] Progress bar increments (0% → 14% → 28% → ... → 100%)
5. [ ] Progress counter shows "1/7", "2/7", etc.
6. [ ] Log entries have color coding:
   - [ ] Green (✅) for successes
   - [ ] Red (❌) for errors

**Completion**:
1. [ ] Progress bar reaches 100%
2. [ ] Final log entry: "✅ Theme Generation Complete: 7/7 worlds"
3. [ ] Button shows "✅ Complete! Generate Again"
4. [ ] Button is enabled again

#### 4. Image Display

**After Generation**:
1. [ ] Close modal
2. [ ] Wait 2-3 seconds
3. [ ] Each world card shows a unique image
4. [ ] Images are not generic (each world has distinct style):
   - [ ] Eldoria = dark fantasy
   - [ ] Cửu Châu = wuxia/Asian
   - [ ] Vùng Đất Cuối = post-apocalyptic
   - [ ] Biển Đen = cyberpunk/nautical
   - [ ] Thành Phố Không Ngủ = noir/urban
   - [ ] Miền Đất Linh Hồn = spirit realm
   - [ ] Vùng Cực Bắc = frozen/Norse

**Image URLs**:
1. [ ] Right-click image → "Open image in new tab"
2. [ ] URL is: `http://127.0.0.1:8000/theme_images/{world_name}_theme.png`
3. [ ] Image loads correctly in new tab
4. [ ] Image is not a placeholder or error

---

## Performance Tests

### Speed Measurements

**First Generation** (cold cache):
- [ ] Full generation: 2-5 minutes
  - Breakdown: 30-60 sec per image × 7 worlds
  - Document actual time: _________ minutes

**Subsequent Generation** (hot cache, status check only):
- [ ] Status check: < 100ms
  - Run `curl http://127.0.0.1:8000/theme/generation-status`
  - Measure response time: _________ ms

**Model Switching**:
1. [ ] First generation with Gemini SDXL: measure time
2. [ ] Second generation with Qwen Gemini: measure time
3. [ ] Note if there's a significant difference

---

## Error Handling Tests

### Network Issues

1. **Stop Kaggle Backend**:
   - [ ] Stop ngrok tunnel
   - [ ] Click "Generate" in modal
   - [ ] Check for error message in progress log
   - [ ] Error visible to user (not silent fail)
   - [ ] Button becomes enabled again
   - [ ] Can retry after backend restarts

2. **Stop FastAPI Backend**:
   - [ ] Stop server (Ctrl+C in terminal)
   - [ ] Refresh page
   - [ ] Check network errors in console
   - [ ] Gear button still works (doesn't crash page)

3. **Invalid Model Name**:
   - [ ] Modify `settings.js` with invalid model
   - [ ] Try to generate
   - [ ] Backend returns error
   - [ ] Error shown in progress log

### Edge Cases

1. **Double-Click Generate**:
   - [ ] Click "Generate" button
   - [ ] Quickly click again
   - [ ] No duplicate requests (idempotent)
   - [ ] Only one generation runs

2. **Close Modal During Generation**:
   - [ ] Start generation
   - [ ] Click [×] to close modal
   - [ ] Generation continues (not cancelled)
   - [ ] Progress log visible when reopening modal

3. **Browser Back Button**:
   - [ ] Generate themes
   - [ ] Press browser back button
   - [ ] Images persist (not lost)
   - [ ] Settings saved

---

## Cross-Browser Tests

- [ ] Chrome/Edge (Chromium-based)
- [ ] Firefox
- [ ] Safari (if on Mac)

For each:
- [ ] Modal appears correctly
- [ ] All dropdowns work
- [ ] Progress bar animates
- [ ] Images display without distortion
- [ ] localStorage persists

---

## Mobile/Responsive Tests

### Tablet (width: 768px)
- [ ] Modal fits on screen
- [ ] Buttons are clickable (not too small)
- [ ] No horizontal scrolling

### Mobile (width: 375px)
- [ ] Modal is responsive
- [ ] Dropdowns are readable
- [ ] Progress log is scrollable
- [ ] Gear button visible

---

## Data Validation Tests

### Settings Storage

1. [ ] Open DevTools → Application → localStorage
2. [ ] Key should be: `themeGenerationSettings`
3. [ ] Value is JSON:
   ```json
   {
     "summarizeModel": "gemini-2.5-flash",
     "txt2imgModel": "sdxl-lightning",
     "steps": 4
   }
   ```
4. [ ] Change settings and verify JSON updates

### API Response Validation

1. [ ] GET `/theme/generation-status` returns valid JSON
2. [ ] POST `/theme/generate-all-worlds` returns:
   - [ ] `success: boolean`
   - [ ] `total_worlds: 7`
   - [ ] `generated_count: number`
   - [ ] `results: array[ThemeGenerationResponse]`
   - [ ] `timestamp: ISO8601 string`
3. [ ] Each result in results array has:
   - [ ] `status: string` (success/error)
   - [ ] `world_id: string`
   - [ ] `world_name: string`
   - [ ] `image_url: string` (if success)
   - [ ] `en_prompt: string` (if success)

---

## Regression Tests

### Existing Features Still Work

- [ ] World selection and creation still works
- [ ] Game loading from saved files still works
- [ ] No console errors when modal not used
- [ ] Existing API endpoints still respond

---

## Test Report Template

```
Test Date: ___________
Tester: ___________
Build Version: ___________

✅ Passed Tests: ___ / ___
❌ Failed Tests: ___ / ___
⚠️ Warnings: ___ 

Critical Issues:
- 

Non-Critical Issues:
- 

Notes:
-
```

---

## Quick Smoke Test (5 minutes)

If you only have time for a quick test:

1. [ ] Server running on port 8000
2. [ ] Load page: `http://127.0.0.1:8000/`
3. [ ] Click ⚙️ button → modal opens
4. [ ] Click "Generate" → generation starts
5. [ ] Wait for completion (~3-5 minutes)
6. [ ] Close modal
7. [ ] Each world card shows different image
8. [ ] Refresh page
9. [ ] Settings still there (localStorage works)
10. [ ] Status shows all 7 images generated

**Result**: ✅ Pass / ❌ Fail
