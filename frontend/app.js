/* ═══════════════════════════════════════════════════════════
   API Gen Platform — Frontend Application
   ═══════════════════════════════════════════════════════════ */

const API_BASE = '';   // Same origin

// ─── State ────────────────────────────────────────────────
let currentPage = 'discover';
let fileContents = { 'main.py': '' };
let activeFile = 'main.py';
let generatorResult = null;

// ─── Navigation ───────────────────────────────────────────
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const page = link.dataset.page;
        switchPage(page);
    });
});

function switchPage(page) {
    currentPage = page;

    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`.nav-link[data-page="${page}"]`)?.classList.add('active');

    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`)?.classList.add('active');

    // Load data for pages
    if (page === 'catalog') loadCatalog();
}

// ─── Discovery ────────────────────────────────────────────
function setIdea(text) {
    document.getElementById('discover-input').value = text;
    discoverAPIs();
}

async function discoverAPIs() {
    const idea = document.getElementById('discover-input').value.trim();
    if (!idea) return showToast('Please enter an application idea', 'error');

    const btn = document.getElementById('btn-discover');
    btn.querySelector('.btn-text').style.display = 'none';
    btn.querySelector('.btn-loader').style.display = 'inline';
    btn.disabled = true;

    try {
        const resp = await fetch(`${API_BASE}/api/discover`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idea }),
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        renderDiscoverResults(data);
    } catch (err) {
        showToast(`Discovery failed: ${err.message}`, 'error');
    } finally {
        btn.querySelector('.btn-text').style.display = 'inline';
        btn.querySelector('.btn-loader').style.display = 'none';
        btn.disabled = false;
    }
}

function renderDiscoverResults(data) {
    const container = document.getElementById('discover-results');
    container.style.display = 'block';

    document.getElementById('results-title').textContent = `APIs for "${data.idea}"`;
    document.getElementById('results-count').textContent = `${data.total_apis} APIs found`;

    const grid = document.getElementById('features-grid');
    grid.innerHTML = '';

    data.features.forEach((feature, idx) => {
        const section = document.createElement('div');
        section.className = 'feature-section';
        section.style.animationDelay = `${idx * 0.1}s`;

        const cardsHtml = feature.apis.map(api => renderAPICard(api)).join('');

        section.innerHTML = `
            <div class="feature-header">
                <span class="feature-icon">${feature.icon}</span>
                <span class="feature-name">${feature.feature}</span>
                <span class="feature-category">${feature.category} · ${feature.apis.length} APIs</span>
            </div>
            <div class="api-cards">${cardsHtml}</div>
        `;

        grid.appendChild(section);
    });

    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderAPICard(api) {
    const scoreClass = api.composite_score >= 85 ? 'score-high' : api.composite_score >= 65 ? 'score-medium' : 'score-low';
    const priceBadge = api.free_tier
        ? '<span class="badge badge-free">Free Tier</span>'
        : '<span class="badge badge-paid">' + api.pricing_model + '</span>';

    const tags = (api.tags || []).slice(0, 3).map(t => `<span class="badge badge-tag">${t}</span>`).join('');
    const sdks = (api.sdk_languages || []).slice(0, 4).join(', ');

    const docsLink = api.documentation_url
        ? `<a href="${api.documentation_url}" target="_blank" class="api-link">📖 Docs</a>`
        : '';
    const githubLink = api.github_url
        ? `<a href="${api.github_url}" target="_blank" class="api-link">🐙 GitHub</a>`
        : '';

    return `
        <div class="api-card">
            <div class="api-card-header">
                <div>
                    <div class="api-name">${api.name}</div>
                    <div class="api-provider">${api.provider}</div>
                </div>
                <span class="api-score ${scoreClass}">${Number(api.composite_score).toFixed(1)}</span>
            </div>
            <div class="api-desc">${api.description}</div>
            <div class="api-badges">
                ${priceBadge}
                <span class="badge badge-auth">${api.auth_type}</span>
                ${tags}
            </div>
            <div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:8px;">
                ${api.request_limit ? '📊 ' + api.request_limit : ''}
                ${sdks ? ' · SDKs: ' + sdks : ''}
            </div>
            <div class="score-bar-container">
                <span class="score-bar-value" title="Score">${Number(api.composite_score).toFixed(1)}</span>
                <div class="score-bar">
                    <div class="score-bar-fill" style="width:${api.composite_score}%;background:var(--gradient-primary)"></div>
                </div>
            </div>
            <div class="api-links">
                ${docsLink}
                ${githubLink}
                ${api.alternatives?.length ? `<span class="api-link" style="cursor:default">🔄 ${api.alternatives.length} alternatives</span>` : ''}
            </div>
        </div>
    `;
}

// ─── Generator ────────────────────────────────────────────
function loadSampleCode() {
    const sampleCode = `"""
Sample machine learning prediction service.
"""
import numpy as np

def predict(image: str, model: str = "default") -> dict:
    """Run prediction on an image."""
    # Simulated ML prediction
    confidence = np.random.uniform(0.85, 0.99)
    return {"prediction": "cat", "confidence": round(confidence, 4)}

def get_models() -> list:
    """List available ML models."""
    return ["default", "resnet50", "vgg16", "efficientnet"]

def train(dataset: str, epochs: int = 10, learning_rate: float = 0.001) -> dict:
    """Train a model on a dataset."""
    return {"status": "completed", "epochs": epochs, "accuracy": 0.94}

class ImageProcessor:
    """Image preprocessing and analysis."""

    def resize(self, image: str, width: int, height: int) -> str:
        """Resize an image to given dimensions."""
        return f"resized_{width}x{height}"

    def analyze(self, image: str) -> dict:
        """Analyze image properties."""
        return {"format": "png", "size": "1024x768", "channels": 3}

    def convert(self, image: str, target_format: str = "png") -> str:
        """Convert image to target format."""
        return f"converted.{target_format}"
`;
    fileContents['main.py'] = sampleCode;
    document.getElementById('code-editor').value = sampleCode;
    showToast('Sample ML project loaded!', 'success');
}

function addFileTab() {
    const modal = document.getElementById('file-modal');
    const input = document.getElementById('new-filename');
    if (modal && input) {
        modal.style.display = 'flex';
        input.value = '.py';
        setTimeout(() => {
            input.focus();
            input.setSelectionRange(0, 0);
        }, 50);
    }
}

function closeFileModal() {
    const modal = document.getElementById('file-modal');
    if (modal) modal.style.display = 'none';
}

function confirmAddFile() {
    const input = document.getElementById('new-filename');
    const name = input ? input.value.trim() : '';

    const validExts = ['.py', '.js', '.java', '.ts', '.go', '.cs'];
    const isValid = validExts.some(ext => name.endsWith(ext));
    if (!isValid) return showToast('Filename unsupported. Valid: .py, .js, .java, .ts, .go, .cs', 'error');
    if (fileContents[name] !== undefined) return showToast('File already exists', 'error');

    fileContents[name] = '';
    const tabsEl = document.getElementById('file-tabs');
    const tab = document.createElement('button');
    tab.className = 'file-tab';
    tab.dataset.filename = name;

    const nameSpan = document.createElement('span');
    nameSpan.textContent = name + ' ';
    const closeBtn = document.createElement('span');
    closeBtn.textContent = '✕';
    closeBtn.className = 'tab-close-btn';
    closeBtn.onclick = (e) => {
        e.stopPropagation();
        closeFileTab(name, tab);
    };

    tab.appendChild(nameSpan);
    tab.appendChild(closeBtn);
    tab.onclick = () => switchFileTab(tab);
    tabsEl.appendChild(tab);

    closeFileModal();
    switchFileTab(tab);
}

function closeFileTab(name, tabEl) {
    if (Object.keys(fileContents).length <= 1) {
        return showToast('Cannot close the last file', 'error');
    }
    delete fileContents[name];
    tabEl.remove();
    if (activeFile === name) {
        const firstTab = document.querySelector('.file-tab');
        if (firstTab) switchFileTab(firstTab);
    }
}

function switchFileTab(tabEl) {
    // Save current file
    fileContents[activeFile] = document.getElementById('code-editor').value;

    // Switch
    document.querySelectorAll('.file-tab').forEach(t => t.classList.remove('active'));
    tabEl.classList.add('active');
    activeFile = tabEl.dataset.filename;
    document.getElementById('code-editor').value = fileContents[activeFile] || '';
}

async function generateAPI() {
    // Save current editor content
    fileContents[activeFile] = document.getElementById('code-editor').value;

    // Filter out empty files
    const files = {};
    for (const [name, code] of Object.entries(fileContents)) {
        if (code.trim()) files[name] = code;
    }

    if (Object.keys(files).length === 0) {
        return showToast('Please enter some Python code first', 'error');
    }

    const projectName = document.getElementById('project-name').value || 'my_project';
    const framework = document.getElementById('framework-select').value || null;

    try {
        showToast('⚡ Generating REST API...', 'info');

        const resp = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_name: projectName, files, framework }),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || `HTTP ${resp.status}`);
        }

        generatorResult = await resp.json();
        renderGeneratorOutput(generatorResult);

        document.getElementById('generator-output').style.display = 'block';
        showToast(`✅ Generated ${generatorResult.endpoints?.length || 0} endpoints!`, 'success');
    } catch (err) {
        showToast(`Generation failed: ${err.message}`, 'error');
    }
}

function renderGeneratorOutput(data) {
    showOutputTab('endpoints');
}

function showOutputTab(tab) {
    if (!generatorResult) return;

    document.querySelectorAll('.output-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.output-tab[onclick="showOutputTab('${tab}')"]`)?.classList.add('active');

    const content = document.getElementById('output-content');

    switch (tab) {
        case 'endpoints':
            const fw = generatorResult.framework || 'unknown';
            const reason = generatorResult.framework_reason || '';
            const analysis = generatorResult.analysis || {};

            let html = `
                <div style="margin-bottom:1rem;padding:1rem;background:var(--bg-primary);border-radius:var(--radius-sm);">
                    <div style="font-weight:700;margin-bottom:8px;">🏗️ Framework: <span style="color:var(--accent-2)">${fw.toUpperCase()}</span></div>
                    <div style="font-size:0.82rem;color:var(--text-muted);line-height:1.6;">${reason}</div>
                    <div style="margin-top:8px;display:flex;gap:12px;font-size:0.8rem;color:var(--text-secondary);">
                        <span>📂 ${analysis.files_scanned || 0} files</span>
                        <span>⚡ ${analysis.functions_found || 0} functions</span>
                        <span>📦 ${analysis.classes_found || 0} classes</span>
                        ${analysis.has_async ? '<span>🔀 Async</span>' : ''}
                        ${analysis.has_ml_models ? '<span>🧠 ML</span>' : ''}
                    </div>
                </div>
                <ul class="endpoint-list">
            `;

            (generatorResult.endpoints || []).forEach(ep => {
                html += `
                    <li class="endpoint-item">
                        <span class="endpoint-method method-${ep.method}">${ep.method}</span>
                        <span class="endpoint-path">${ep.path}</span>
                        <span class="endpoint-func">${ep.function_name}</span>
                    </li>
                `;
            });
            html += '</ul>';
            content.innerHTML = html;
            break;

        case 'code':
            let codeHtml = '';
            const files = generatorResult.generated_files || {};
            for (const [fname, code] of Object.entries(files)) {
                codeHtml += `
                    <div style="margin-bottom:1rem;">
                        <div style="font-weight:600;font-size:0.88rem;padding:6px 0;color:var(--accent-2);">📄 ${fname}</div>
                        <pre>${escapeHtml(code)}</pre>
                    </div>
                `;
            }
            content.innerHTML = codeHtml || '<p style="color:var(--text-muted)">No files generated.</p>';
            break;

        case 'openapi':
            content.innerHTML = `<pre>${escapeHtml(JSON.stringify(generatorResult.openapi_spec || {}, null, 2))}</pre>`;
            break;

        case 'deploy':
            let deployHtml = `
                <div style="margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
                    <h3 style="margin-bottom: 0.5rem; color: var(--text-primary);">🚀 CI/CD Automation</h3>
                    <p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:1rem;">Generate a production-ready CI/CD pipeline for GitHub Actions or GitLab CI.</p>
                    <button class="btn-primary" onclick="openCicdModal()">Setup CI/CD Pipeline</button>
                </div>
            `;
            const configs = generatorResult.deployment_configs || {};
            for (const [fname, code] of Object.entries(configs)) {
                deployHtml += `
                    <div style="margin-bottom:1rem;">
                        <div style="font-weight:600;font-size:0.88rem;padding:6px 0;color:var(--accent-2);">📦 ${fname}</div>
                        <pre>${escapeHtml(code)}</pre>
                    </div>
                `;
            }
            content.innerHTML = deployHtml || '<p style="color:var(--text-muted)">No deployment configs.</p>';
            break;
    }
}

// ─── Catalog ──────────────────────────────────────────────
let catalogData = [];
let categoriesData = [];

async function loadCatalog() {
    try {
        // Load categories
        const catResp = await fetch(`${API_BASE}/api/categories`);
        if (catResp.ok) {
            categoriesData = await catResp.json();
            const select = document.getElementById('catalog-category');
            select.innerHTML = '<option value="">All Categories</option>';
            categoriesData.forEach(cat => {
                select.innerHTML += `<option value="${cat.name}">${cat.icon} ${cat.display_name} (${cat.api_count})</option>`;
            });
        }

        // Load APIs
        await searchCatalog();
    } catch (err) {
        showToast(`Failed to load catalog: ${err.message}`, 'error');
    }
}

async function searchCatalog() {
    const search = document.getElementById('catalog-search')?.value || '';
    const category = document.getElementById('catalog-category')?.value || '';
    const freeOnly = document.getElementById('catalog-free')?.checked || false;

    let url = `${API_BASE}/api/apis?limit=100`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (category) url += `&category=${category}`;
    if (freeOnly) url += `&free_only=true`;

    try {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();

        const grid = document.getElementById('catalog-grid');
        grid.innerHTML = '';

        if (!data.apis || data.apis.length === 0) {
            grid.innerHTML = '<p style="color:var(--text-muted);grid-column:1/-1;text-align:center;padding:3rem;">No APIs found matching your criteria.</p>';
            return;
        }

        data.apis.forEach(api => {
            const card = document.createElement('div');
            card.className = 'api-card';
            card.innerHTML = renderCatalogCard(api);
            grid.appendChild(card);
        });
    } catch (err) {
        console.error('Catalog search error:', err);
    }
}

function renderCatalogCard(api) {
    const scoreClass = api.composite_score >= 85 ? 'score-high' : api.composite_score >= 65 ? 'score-medium' : 'score-low';
    const priceBadge = api.free_tier
        ? '<span class="badge badge-free">Free</span>'
        : '<span class="badge badge-paid">' + api.pricing_model + '</span>';

    const tags = (api.tags || []).slice(0, 4).map(t => `<span class="badge badge-tag">${t}</span>`).join('');

    return `
        <div class="api-card-header">
            <div>
                <div class="api-name">${api.name}</div>
                <div class="api-provider">${api.provider} · ${api.category}</div>
            </div>
            <span class="api-score ${scoreClass}">${Number(api.composite_score).toFixed(1)}</span>
        </div>
        <div class="api-desc">${api.description || ''}</div>
        <div class="api-badges">${priceBadge} ${tags}</div>
        <div class="score-bar-container">
            <span class="score-bar-value">${Number(api.composite_score).toFixed(1)}</span>
            <div class="score-bar">
                <div class="score-bar-fill" style="width:${api.composite_score}%;background:var(--gradient-primary)"></div>
            </div>
        </div>
    `;
}



// ─── Utilities ────────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ─── Keyboard shortcut ───────────────────────────────────
document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        if (currentPage === 'discover') discoverAPIs();
        else if (currentPage === 'generator') generateAPI();
    }
});

// ─── Init ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Focus search on discover page
    document.getElementById('discover-input')?.focus();
});
