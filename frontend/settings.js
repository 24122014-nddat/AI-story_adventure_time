/**
 * Theme Generation Settings Manager
 * Handles configuration, fetching, and progress tracking
 */

// Global Settings Object
const themeSettings = {
  summarizeModel: "gemini-2.5-flash",
  txt2imgModel: "sdxl-lightning",
  steps: 4,
  
  /**
   * Load settings from localStorage
   */
  load() {
    const stored = localStorage.getItem('themeGenerationSettings');
    if (stored) {
      try {
        const loaded = JSON.parse(stored);
        Object.assign(this, loaded);
      } catch (e) {
        console.warn("Failed to load theme settings:", e);
      }
    }
  },
  
  /**
   * Save settings to localStorage
   */
  save() {
    localStorage.setItem('themeGenerationSettings', JSON.stringify({
      summarizeModel: this.summarizeModel,
      txt2imgModel: this.txt2imgModel,
      steps: this.steps,
    }));
  },
  
  /**
   * Update a single setting
   */
  set(key, value) {
    if (this.hasOwnProperty(key)) {
      this[key] = value;
      this.save();
    }
  },
  
  /**
   * Get all settings
   */
  getAll() {
    return {
      summarizeModel: this.summarizeModel,
      txt2imgModel: this.txt2imgModel,
      steps: this.steps,
    };
  }
};

// Load settings on page initialization
themeSettings.load();


// ============= MODAL MANAGEMENT =============

/**
 * Open the Settings Modal
 */
function openSettingsModal() {
  const modal = document.getElementById('settingsModal');
  if (modal) {
    modal.style.display = 'flex';
    loadSettingsUI();
  }
}

/**
 * Close the Settings Modal
 */
function closeSettingsModal() {
  const modal = document.getElementById('settingsModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

/**
 * Load current settings into UI
 */
function loadSettingsUI() {
  const summarizeSelect = document.getElementById('summarizeModel');
  const txt2imgSelect = document.getElementById('txt2imgModel');
  const stepsSelect = document.getElementById('sdxlSteps');
  
  if (summarizeSelect) summarizeSelect.value = themeSettings.summarizeModel;
  if (txt2imgSelect) txt2imgSelect.value = themeSettings.txt2imgModel;
  if (stepsSelect) stepsSelect.value = themeSettings.steps;
  
  // Update steps section visibility
  updateStepsVisibility();
}

/**
 * Update visibility of steps option based on image model
 */
function updateStepsVisibility() {
  const txt2imgSelect = document.getElementById('txt2imgModel');
  const stepsSection = document.getElementById('stepsSection');
  
  if (txt2imgSelect && stepsSection) {
    const isSDXL = txt2imgSelect.value === 'sdxl-lightning';
    stepsSection.style.display = isSDXL ? 'flex' : 'none';
  }
}

/**
 * Save settings from UI
 */
function saveSettingsFromUI() {
  const summarizeSelect = document.getElementById('summarizeModel');
  const txt2imgSelect = document.getElementById('txt2imgModel');
  const stepsSelect = document.getElementById('sdxlSteps');
  
  if (summarizeSelect) themeSettings.set('summarizeModel', summarizeSelect.value);
  if (txt2imgSelect) themeSettings.set('txt2imgModel', txt2imgSelect.value);
  if (stepsSelect) themeSettings.set('steps', parseInt(stepsSelect.value));
  
  console.log('✅ Settings saved:', themeSettings.getAll());
}

// Add event listeners for model selection changes
document.addEventListener('DOMContentLoaded', () => {
  const txt2imgSelect = document.getElementById('txt2imgModel');
  const settingsOverlay = document.getElementById('settingsOverlay');
  
  if (txt2imgSelect) {
    txt2imgSelect.addEventListener('change', updateStepsVisibility);
  }
  
  if (settingsOverlay) {
    settingsOverlay.addEventListener('click', closeSettingsModal);
  }
});


// ============= THEME GENERATION FETCHING =============

/**
 * Trigger theme generation for all 7 worlds
 */
async function triggerThemeGeneration() {
  try {
    // Save current settings
    saveSettingsFromUI();
    
    // Show progress
    const progressSection = document.getElementById('generationProgress');
    if (progressSection) {
      progressSection.style.display = 'block';
    }
    
    // Disable generate button
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
      generateBtn.disabled = true;
      generateBtn.textContent = '⏳ Generating...';
    }
    
    console.log('🚀 Starting theme generation with settings:', themeSettings.getAll());
    
    // Call backend API
    const response = await fetch(`${API_BASE}/theme/generate-all-worlds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(themeSettings.getAll()),
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API returned ${response.status}: ${error}`);
    }
    
    const data = await response.json();
    
    // Process results
    handleThemeGenerationResults(data);
    
    // Re-enable button
    if (generateBtn) {
      generateBtn.disabled = false;
      generateBtn.textContent = '✅ Complete! Generate Again';
    }
  
  } catch (err) {
    console.error('❌ Theme generation failed:', err);
    addProgressLog(`ERROR: ${err.message}`, 'error');
    
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
      generateBtn.disabled = false;
      generateBtn.textContent = '🚀 Generate All Themes';
    }
  }
}

/**
 * Handle theme generation results and update UI
 */
function handleThemeGenerationResults(data) {
  const totalWorlds = data.total_worlds || 7;
  const results = data.results || [];
  let successCount = 0;
  
  console.log('📊 Generation Results:', data);
  
  // Log each result
  results.forEach((result, index) => {
    const progressNum = index + 1;
    
    if (result.status === 'success') {
      addProgressLog(`✅ ${result.world_name}: Generated successfully`, 'success');
      successCount++;
    } else {
      addProgressLog(`❌ ${result.world_name}: ${result.error || 'Unknown error'}`, 'error');
    }
    
    // Update progress bar
    updateProgressBar(progressNum, totalWorlds);
  });
  
  // Final summary
  addProgressLog(`\n✅ Theme Generation Complete: ${successCount}/${totalWorlds} worlds`, 'success');
  
  // Update world images if displayed
  if (typeof updateWorldImages === 'function') {
    console.log('📸 Updating world card images...');
    updateWorldImages();
  }
}

/**
 * Add a log entry to the progress log
 */
function addProgressLog(message, type = 'info') {
  const progressLog = document.getElementById('progressLog');
  if (!progressLog) return;
  
  const entry = document.createElement('div');
  entry.className = `progress-log-entry ${type}`;
  entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  progressLog.appendChild(entry);
  progressLog.scrollTop = progressLog.scrollHeight;
}

/**
 * Update the progress bar
 */
function updateProgressBar(current, total) {
  const progressFill = document.getElementById('progressFill');
  const progressCount = document.getElementById('progressCount');
  
  if (progressFill) {
    const percentage = (current / total) * 100;
    progressFill.style.width = `${percentage}%`;
    progressFill.textContent = `${percentage.toFixed(0)}%`;
  }
  
  if (progressCount) {
    progressCount.textContent = `${current}/${total}`;
  }
}


// ============= WORLD IMAGE UPDATE =============

/**
 * Update world card images after generation
 * This function should be called after successful theme generation
 */
async function updateWorldImages() {
  try {
    // Get all world cards
    const worldCards = document.querySelectorAll('.world-card');
    
    if (!worldCards.length) {
      console.log('ℹ️ No world cards found to update');
      return;
    }
    
    console.log(`🖼️ Updating images for ${worldCards.length} world cards...`);
    
    // Try to get status from backend
    const statusResponse = await fetch(`${API_BASE}/theme/generation-status`);
    const statusData = await statusResponse.json();
    
    const generatedImages = statusData.images || [];
    console.log('📁 Available images:', generatedImages);
    
    // Update each card
    worldCards.forEach((card) => {
      const worldId = card.querySelector('[data-world-id]')?.dataset.worldId;
      const worldName = card.querySelector('h3')?.textContent;
      const coverDiv = card.querySelector('.world-cover');
      
      if (!coverDiv) return;
      
      // Try to find matching image
      const matchingImage = generatedImages.find(img => {
        const safe = sanitizeForFilename(worldName);
        return img.toLowerCase().includes(safe.toLowerCase());
      });
      
      if (matchingImage) {
        const imageUrl = `${API_BASE}/theme_images/${matchingImage}`;
        
        // Create or update image element
        let img = coverDiv.querySelector('img');
        if (!img) {
          img = document.createElement('img');
          img.className = 'world-image';
          img.alt = worldName;
          coverDiv.innerHTML = '';
          coverDiv.appendChild(img);
        }
        
        img.src = imageUrl;
        console.log(`✅ Updated image for ${worldName}: ${matchingImage}`);
      }
    });
    
  } catch (err) {
    console.warn('⚠️ Failed to update world images:', err);
  }
}

/**
 * Sanitize world name for filename matching
 */
function sanitizeForFilename(text) {
  if (!text) return '';
  return text
    .toLowerCase()
    .replace(/\s+/g, '_')
    // Remove only filesystem-dangerous characters
    .replace(/[\/\\:*?"<>|]/g, '')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
}


// ============= INITIALIZATION =============

/**
 * Initialize theme generation UI
 * Call this on page load to set up the settings modal and gear icon
 */
function initThemeGeneration() {
  console.log('🎨 Initializing Theme Generation UI...');
  
  // Create and inject settings modal if not already present
  if (!document.getElementById('settingsModal')) {
    console.warn('⚠️ Settings modal not found in DOM. Please include settings-modal.html');
  }
  
  // Create gear icon button if not already present
  if (!document.querySelector('.gear-icon-btn')) {
    const taskbar = document.querySelector('.hero-actions') || document.body;
    const gearBtn = document.createElement('button');
    gearBtn.className = 'gear-icon-btn';
    gearBtn.title = 'Theme Generation Settings';
    gearBtn.innerHTML = '⚙️';
    gearBtn.addEventListener('click', openSettingsModal);
    
    // Insert after other buttons
    if (taskbar.querySelector('.btn')) {
      taskbar.insertBefore(gearBtn, taskbar.querySelector('.btn').nextSibling);
    } else {
      taskbar.appendChild(gearBtn);
    }
  }
  
  console.log('✅ Theme Generation UI initialized');
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initThemeGeneration);
