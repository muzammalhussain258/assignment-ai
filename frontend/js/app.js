/**
 * AI Assignment Generator — Vanilla JS Frontend
 * All API calls target /api/v1/ endpoints.
 */

'use strict';

/* -------------------------------------------------------
   Constants
------------------------------------------------------- */
const API_BASE = '/api/v1';

const TEMPLATES = [
  { value: 'standard',       label: 'Standard',       icon: '📄' },
  { value: 'research_paper', label: 'Research',        icon: '🔬' },
  { value: 'essay',          label: 'Essay',           icon: '✍️'  },
  { value: 'case_study',     label: 'Case Study',      icon: '📊' },
  { value: 'lab_report',     label: 'Lab Report',      icon: '🧪' },
];

const PROVIDERS = [
  { value: 'openai',    label: 'OpenAI',    icon: '🤖' },
  { value: 'gemini',    label: 'Gemini',    icon: '✨' },
  { value: 'anthropic', label: 'Anthropic', icon: '🧠' },
  { value: 'groq',      label: 'Groq',      icon: '⚡' },
];

const LOADING_MESSAGES = [
  'Initialising AI model…',
  'Analysing topic and requirements…',
  'Crafting assignment structure…',
  'Writing content sections…',
  'Finalising and formatting…',
  'Generating downloadable files…',
];

/* -------------------------------------------------------
   State
------------------------------------------------------- */
let state = {
  template: 'standard',
  provider: 'openai',
  wordCount: 1000,
  loadingMsgIndex: 0,
  loadingInterval: null,
  progressInterval: null,
  progress: 0,
};

/* -------------------------------------------------------
   DOM Helpers
------------------------------------------------------- */
const $ = (sel) => document.querySelector(sel);
const show = (el) => el && el.classList.remove('hidden');
const hide = (el) => el && el.classList.add('hidden');

/* -------------------------------------------------------
   Card Builder
------------------------------------------------------- */
function buildCards(containerId, items, stateKey, initialValue) {
  const container = document.getElementById(containerId);
  if (!container) return;

  items.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'selector-card' + (item.value === initialValue ? ' selected' : '');
    card.dataset.value = item.value;
    card.innerHTML = `
      <div class="card-icon">${item.icon}</div>
      <div class="card-label">${item.label}</div>
    `;
    card.addEventListener('click', () => {
      container.querySelectorAll('.selector-card').forEach((c) => c.classList.remove('selected'));
      card.classList.add('selected');
      state[stateKey] = item.value;
    });
    container.appendChild(card);
  });
}

/* -------------------------------------------------------
   Word Count Slider
------------------------------------------------------- */
function initSlider() {
  const slider = document.getElementById('word-count-slider');
  const display = document.getElementById('word-count-value');
  if (!slider || !display) return;

  const update = () => {
    const v = parseInt(slider.value, 10);
    state.wordCount = v;
    display.querySelector('.count').textContent = v.toLocaleString();

    // Update gradient fill
    const min = parseInt(slider.min, 10);
    const max = parseInt(slider.max, 10);
    const pct = ((v - min) / (max - min)) * 100;
    slider.style.background = `linear-gradient(to right, var(--accent) ${pct}%, var(--bg-card) ${pct}%)`;
  };

  slider.addEventListener('input', update);
  update();
}

/* -------------------------------------------------------
   API Key Toggle
------------------------------------------------------- */
function initApiKeyToggle() {
  const btn = document.getElementById('toggle-api-key');
  const input = document.getElementById('api-key-input');
  if (!btn || !input) return;

  btn.addEventListener('click', () => {
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    btn.textContent = isHidden ? '🙈' : '👁️';
    btn.setAttribute('aria-label', isHidden ? 'Hide API key' : 'Show API key');
  });
}

/* -------------------------------------------------------
   Loading Animation
------------------------------------------------------- */
function startLoading() {
  state.progress = 0;
  state.loadingMsgIndex = 0;

  const bar = document.getElementById('progress-bar');
  const msg = document.getElementById('loading-status');
  if (bar) bar.style.width = '0%';
  if (msg) msg.textContent = LOADING_MESSAGES[0];

  // Progress bar simulation: reaches ~90% over ~25s, final 10% on success
  state.progressInterval = setInterval(() => {
    if (state.progress < 90) {
      state.progress = Math.min(state.progress + 1.5, 90);
      if (bar) bar.style.width = state.progress + '%';
    }
  }, 400);

  // Cycle status messages
  state.loadingMsgIndex = 0;
  state.loadingInterval = setInterval(() => {
    state.loadingMsgIndex = (state.loadingMsgIndex + 1) % LOADING_MESSAGES.length;
    if (msg) msg.textContent = LOADING_MESSAGES[state.loadingMsgIndex];
  }, 4000);
}

function stopLoading(success = true) {
  clearInterval(state.progressInterval);
  clearInterval(state.loadingInterval);

  const bar = document.getElementById('progress-bar');
  const msg = document.getElementById('loading-status');

  if (success && bar) {
    bar.style.width = '100%';
    if (msg) msg.textContent = 'Complete!';
  }
}

/* -------------------------------------------------------
   Error Display
------------------------------------------------------- */
function showError(title, detail) {
  const section = document.getElementById('error-section');
  const titleEl = document.getElementById('error-title');
  const detailEl = document.getElementById('error-detail');
  if (!section) return;

  if (titleEl) titleEl.textContent = title;
  if (detailEl) {
    if (Array.isArray(detail)) {
      detailEl.textContent = detail.map((e) => `${e.field}: ${e.message}`).join(' | ');
    } else {
      detailEl.textContent = detail || '';
    }
  }
  show(section);
}

function clearError() {
  hide(document.getElementById('error-section'));
}

/* -------------------------------------------------------
   Result Display
------------------------------------------------------- */
function showResult(data) {
  const section = document.getElementById('result-section');
  if (!section) return;

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('result-topic', data.topic);
  set('result-level', data.education_level.replace(/_/g, ' '));
  set('result-words', data.word_count.toLocaleString());
  set('result-template', data.template.replace(/_/g, ' '));

  const docxBtn = document.getElementById('download-docx');
  const pdfBtn  = document.getElementById('download-pdf');

  if (docxBtn) {
    docxBtn.onclick = () => triggerDownload(data.download_docx, data.assignment_id + '.docx');
  }
  if (pdfBtn) {
    pdfBtn.onclick = () => triggerDownload(data.download_pdf, data.assignment_id + '.pdf');
  }

  show(section);
}

function triggerDownload(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/* -------------------------------------------------------
   Form Submission
------------------------------------------------------- */
async function handleSubmit(e) {
  e.preventDefault();
  clearError();
  hide(document.getElementById('result-section'));

  const topic   = document.getElementById('topic-input').value.trim();
  const level   = document.getElementById('education-level').value;
  const apiKey  = document.getElementById('api-key-input').value.trim();

  // Client-side validation
  if (!topic) {
    showError('Validation Error', 'Please enter a topic.');
    return;
  }
  if (topic.length < 3) {
    showError('Validation Error', 'Topic must be at least 3 characters long.');
    return;
  }
  if (!level) {
    showError('Validation Error', 'Please select an education level.');
    return;
  }

  const payload = {
    topic,
    education_level: level,
    word_count: state.wordCount,
    template: state.template,
    llm_provider: state.provider,
  };

  if (apiKey) payload.api_key = apiKey;

  // Show loading
  const submitBtn = document.getElementById('submit-btn');
  if (submitBtn) submitBtn.disabled = true;
  show(document.getElementById('loading-section'));
  startLoading();

  try {
    const response = await fetch(`${API_BASE}/generate-assignment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': crypto.randomUUID ? crypto.randomUUID() : (Date.now().toString(36) + Math.random().toString(36).slice(2)),
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      const err = new Error(`HTTP ${response.status}`);
      err.status = response.status;
      err.data = data;
      throw err;
    }

    stopLoading(true);
    showResult(data);
  } catch (err) {
    stopLoading(false);

    let title = 'An error occurred';
    let detail = 'Please check your inputs and try again.';

    if (err && err.data) {
      const d = err.data;
      title = d.error || title;
      detail = d.detail || d.message || detail;
    } else if (err instanceof TypeError) {
      title = 'Network Error';
      detail = 'Could not reach the server. Please check your connection.';
    }

    showError(title, detail);
  } finally {
    hide(document.getElementById('loading-section'));
    if (submitBtn) submitBtn.disabled = false;
  }
}

/* -------------------------------------------------------
   Init
------------------------------------------------------- */
function init() {
  buildCards('template-cards', TEMPLATES, 'template', state.template);
  buildCards('provider-cards', PROVIDERS, 'provider', state.provider);
  initSlider();
  initApiKeyToggle();

  const form = document.getElementById('assignment-form');
  if (form) form.addEventListener('submit', handleSubmit);
}

document.addEventListener('DOMContentLoaded', init);
