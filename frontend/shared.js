// Use relative URL or localStorage override for API base
const API_BASE = (() => {
  const stored = localStorage.getItem('story_api_base');
  if (stored) return stored;
  
  // Auto-detect API base: if frontend is served from root, API is on same host
  // Otherwise, default to localhost:8000
  if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
    return `${window.location.protocol}//${window.location.host}`;
  }
  return 'http://127.0.0.1:8000';
})();

const storage = {
  get selectedWorld() {
    const raw = localStorage.getItem('story_selected_world');
    return raw ? JSON.parse(raw) : null;
  },
  set selectedWorld(value) {
    localStorage.setItem('story_selected_world', JSON.stringify(value));
  },
  get draftCharacter() {
    const raw = localStorage.getItem('story_character_draft');
    return raw ? JSON.parse(raw) : null;
  },
  set draftCharacter(value) {
    localStorage.setItem('story_character_draft', JSON.stringify(value));
  },
  get sessionId() {
    return sessionStorage.getItem('story_session_id') || null;
  },
  set sessionId(value) {
    if (value) sessionStorage.setItem('story_session_id', value);
    else sessionStorage.removeItem('story_session_id');
  },
  get theme() {
    return localStorage.getItem('story_theme') || 'light';
  },
  set theme(value) {
    if (value === 'dark') localStorage.setItem('story_theme', 'dark');
    else localStorage.setItem('story_theme', 'light');
  },
  clearGameSession() {
    sessionStorage.removeItem('story_session_id');
  }
  
};
function applyTheme() {
  document.body.classList.remove('theme-light', 'theme-dark');
  document.body.classList.add(storage.theme === 'dark' ? 'theme-dark' : 'theme-light');
}

function toggleTheme() {
  storage.theme = storage.theme === 'dark' ? 'light' : 'dark';
  applyTheme();
  updateThemeButtons();
}
function updateThemeButtons() {
  qsa('[data-theme-toggle]').forEach(btn => {
    btn.textContent = storage.theme === 'dark' ? '☀ Chế độ sáng' : '🌙 Chế độ tối';
  });
}

function qs(selector, root = document) { return root.querySelector(selector); }
function qsa(selector, root = document) { return [...root.querySelectorAll(selector)]; }
function esc(str) {
  return String(str ?? '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;');
}
function safeFetch(path, options = {}) {
  return fetch(API_BASE + path, options).then(async res => {
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `HTTP ${res.status}`);
    }
    return res.json();
  });
}
function go(url) { window.location.href = url; }
document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  updateThemeButtons();

  qsa('[data-theme-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      toggleTheme();
      updateThemeButtons();
    });
  });
});
function updateThemeButtons() {
  qsa('[data-theme-toggle]').forEach(btn => {
    btn.textContent =
      storage.theme === 'dark'
        ? '☀ Chế độ sáng'
        : '🌙 Chế độ tối';
  });
}

// ============ IMAGE GENERATION FUNCTIONS ============

// Cache global para armazenar imagens geradas
let worldThemeCache = {};

/**
 * Gera imagens theme para TODOS os 7 mundos de uma vez
 * Chamado uma vez quando a página carrega
 */
async function generateAllWorldThemes() {
  try {
    console.log("🌍 Iniciando geração de imagens para todos os 7 mundos...");
    console.log("   API_BASE:", API_BASE);
    
    const url = `${API_BASE}/debug/images/generate-all-worlds`;
    console.log("   Fetching from:", url);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({})
    });
    
    console.log("   Response status:", response.status);
    
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }
    
    const data = await response.json();
    console.log("   Response data:", data);
    
    if (data.success && data.results) {
      console.log(`✅ Geração concluída! ${data.generated}/${data.total_worlds} mundos com sucesso`);
      
      // Armazenar no cache por world_id
      data.results.forEach(result => {
        if (result.status === 'success' && result.image_url) {
          worldThemeCache[result.world_id] = result.image_url;
          console.log(`  ✅ ${result.world_name}: ${result.image_url}`);
        } else {
          console.warn(`  ⚠️ ${result.world_name}: Falha na geração`);
        }
      });
      
      return worldThemeCache;
    }
  } catch (err) {
    console.error(`❌ Erro ao gerar imagens dos mundos:`, err);
    console.error("Erro completo:", err.toString());
  }
  return null;
}

/**
 * Busca a imagem theme para um mundo específico
 * Usa cache se disponível, senão tenta gerar todas
 */
async function generateWorldThemeImage(worldId, worldName) {
  try {
    // Se já está em cache, retorna imediatamente
    if (worldThemeCache[worldId]) {
      console.log(`📦 Usando cache para ${worldName}: ${worldThemeCache[worldId]}`);
      return `${API_BASE}${worldThemeCache[worldId]}`;
    }
    
    // Se cache está vazio, gera todas as imagens
    if (Object.keys(worldThemeCache).length === 0) {
      console.log(`🔄 Cache vazio, gerando todas as imagens dos mundos...`);
      await generateAllWorldThemes();
    }
    
    // Agora tenta usar do cache novamente
    if (worldThemeCache[worldId]) {
      const url = `${API_BASE}${worldThemeCache[worldId]}`;
      console.log(`✅ World theme image (from cache): ${url}`);
      return url;
    }
    
    console.warn(`⚠️ Nenhuma imagem encontrada para mundo: ${worldId}`);
  } catch (err) {
    console.error(`❌ Erro ao obter imagem do mundo ${worldName}:`, err);
  }
  return null;
}

/**
 * Sinh hình ảnh theme cho câu chuyện hiện tại
 */
async function generateStoryThemeImage(sessionId) {
  try {
    const response = await safeFetch('/debug/images/story-theme', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        session_id: sessionId,
        style: null
      })
    });
    
    if (response.success && response.image_url) {
      const fullUrl = API_BASE + response.image_url;
      console.log(`✅ Story theme image generated: ${fullUrl}`);
      return fullUrl;
    }
  } catch (err) {
    console.error(`❌ Failed to generate story theme image:`, err);
  }
  return null;
}

/**
 * Sinh hình ảnh cho một khung cảnh/scene
 */
async function generateSceneImage(description, style = 'fantasy') {
  try {
    const response = await safeFetch('/debug/images/scene', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        description: description,
        style: style
      })
    });
    
    if (response.success && response.image_url) {
      const fullUrl = API_BASE + response.image_url;
      console.log(`✅ Scene image generated: ${fullUrl}`);
      return fullUrl;
    }
  } catch (err) {
    console.error(`❌ Failed to generate scene image:`, err);
  }
  return null;
}