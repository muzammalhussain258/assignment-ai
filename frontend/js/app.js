/**
 * app.js — AI Assignment Generator frontend logic
 * Pure vanilla JS, no frameworks, no build step.
 */

/* =====================================================================
   1. DOM element references
   ===================================================================== */
const formSection     = document.getElementById('form-section');
const loadingSection  = document.getElementById('loading-section');
const resultsSection  = document.getElementById('results-section');
const errorSection    = document.getElementById('error-section');

const assignmentForm  = document.getElementById('assignment-form');
const topicInput      = document.getElementById('topic');
const topicError      = document.getElementById('topic-error');
const educationLevel  = document.getElementById('education-level');
const wordCountSlider = document.getElementById('word-count');
const wordCountDisplay = document.getElementById('word-count-display');

const templateGrid    = document.getElementById('template-grid');
const selectedTemplateInput = document.getElementById('selected-template');

const providerGrid    = document.getElementById('provider-grid');
const selectedProviderInput = document.getElementById('selected-provider');

const apiKeyInput     = document.getElementById('api-key');
const apiKeyError     = document.getElementById('api-key-error');
const toggleApiKey    = document.getElementById('toggle-api-key');
const eyeIcon         = document.getElementById('eye-icon');
const apiKeyLink      = document.getElementById('api-key-link');
const apiKeyLinkText  = document.getElementById('api-key-link-text');

const generateBtn     = document.getElementById('generate-btn');
const btnText         = document.getElementById('btn-text');
const btnSpinner      = document.getElementById('btn-spinner');

const progressBar     = document.getElementById('progress-bar');
const loadingStatus   = document.getElementById('loading-status');

const assignmentIdDisplay = document.getElementById('assignment-id-display');
const downloadDocxBtn = document.getElementById('download-docx');
const downloadPdfBtn  = document.getElementById('download-pdf');
const generateAnotherBtn = document.getElementById('generate-another');

const errorMessage    = document.getElementById('error-message');
const dismissErrorBtn = document.getElementById('dismiss-error');
const tryAgainBtn     = document.getElementById('try-again');

/* =====================================================================
   2. State
   ===================================================================== */
const state = {
  selectedTemplate: 'standard',
  selectedProvider: 'gemini',
  currentAssignmentId: null,
  progressTimer: null,
  progressValue: 0,
};

/* =====================================================================
   3. Provider → API key helper link mapping
   ===================================================================== */
const PROVIDER_LINKS = {
  openai:    'https://platform.openai.com/api-keys',
  gemini:    'https://aistudio.google.com/apikey',
  anthropic: 'https://console.anthropic.com/settings/keys',
  groq:      'https://console.groq.com/keys',
};

/* =====================================================================
   4. Loading status messages
   ===================================================================== */
const STATUS_STEPS = [
  { pct:  0,  msg: '🔍 Analyzing topic…'       },
  { pct: 20,  msg: '📝 Generating outline…'    },
  { pct: 40,  msg: '✍️ Writing content…'       },
  { pct: 70,  msg: '🎨 Formatting document…'   },
  { pct: 85,  msg: '📄 Creating files…'        },
];

/* =====================================================================
   5. Event listeners
   ===================================================================== */

// Word count slider
wordCountSlider.addEventListener('input', () => {
  wordCountDisplay.textContent = Number(wordCountSlider.value).toLocaleString();
});

// Template card selection
templateGrid.addEventListener('click', (e) => {
  const card = e.target.closest('.option-card');
  if (!card) return;

  templateGrid.querySelectorAll('.option-card').forEach(c => {
    c.setAttribute('aria-pressed', 'false');
  });
  card.setAttribute('aria-pressed', 'true');
  state.selectedTemplate = card.dataset.value;
  selectedTemplateInput.value = state.selectedTemplate;
});

// Provider card selection
providerGrid.addEventListener('click', (e) => {
  const card = e.target.closest('.option-card');
  if (!card) return;

  providerGrid.querySelectorAll('.option-card').forEach(c => {
    c.setAttribute('aria-pressed', 'false');
  });
  card.setAttribute('aria-pressed', 'true');
  state.selectedProvider = card.dataset.value;
  selectedProviderInput.value = state.selectedProvider;
  updateApiKeyLink(state.selectedProvider);
});

// API key show/hide toggle
toggleApiKey.addEventListener('click', () => {
  const isPassword = apiKeyInput.type === 'password';
  apiKeyInput.type = isPassword ? 'text' : 'password';
  eyeIcon.textContent = isPassword ? '🙈' : '👁️';
});

// Form submit
assignmentForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!validateForm()) return;
  await generateAssignment();
});

// Results actions
downloadDocxBtn.addEventListener('click', () => downloadDocx(state.currentAssignmentId));
downloadPdfBtn.addEventListener('click',  () => downloadPdf(state.currentAssignmentId));
generateAnotherBtn.addEventListener('click', resetToForm);

// Error actions
dismissErrorBtn.addEventListener('click', hideError);
tryAgainBtn.addEventListener('click', resetToForm);

/* =====================================================================
   6. Form validation
   ===================================================================== */
function validateForm() {
  let valid = true;

  // Topic
  const topic = topicInput.value.trim();
  if (!topic || topic.length < 3) {
    topicError.textContent = 'Topic must be at least 3 characters.';
    topicInput.classList.add('input-error');
    valid = false;
  } else {
    topicError.textContent = '';
    topicInput.classList.remove('input-error');
  }

  // API key
  const apiKey = apiKeyInput.value.trim();
  if (!apiKey) {
    apiKeyError.textContent = 'API key is required.';
    apiKeyInput.classList.add('input-error');
    valid = false;
  } else {
    apiKeyError.textContent = '';
    apiKeyInput.classList.remove('input-error');
  }

  return valid;
}

/* =====================================================================
   7. API call
   ===================================================================== */
async function generateAssignment() {
  const payload = {
    topic:           topicInput.value.trim(),
    education_level: educationLevel.value,
    word_count:      Number(wordCountSlider.value),
    template:        state.selectedTemplate,
    llm_provider:    state.selectedProvider,
    api_key:         apiKeyInput.value.trim(),
  };

  showLoading();

  try {
    const response = await fetch('/api/v1/generate-assignment', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || data.error || `Server error ${response.status}`);
    }

    // Expect { assignment_id: '...' } or similar
    const assignmentId =
      data.assignment_id || data.id || data.data?.assignment_id || null;

    stopProgress(100);
    showResults(assignmentId);
  } catch (err) {
    stopProgress(0);
    showError(err.message || 'An unexpected error occurred.');
  }
}

/* =====================================================================
   8. Loading / progress animation
   ===================================================================== */
function showLoading() {
  setGenerateButtonLoading(true);
  formSection.classList.add('hidden');
  loadingSection.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  errorSection.classList.add('hidden');

  state.progressValue = 0;
  updateProgress(0);

  // Advance progress automatically over ~50 s to simulate work
  const TARGET_MS = 50000;
  const TICK_MS   = 400;
  const STEPS = [
    { targetPct: 18,  duration: TARGET_MS * 0.15 },
    { targetPct: 38,  duration: TARGET_MS * 0.15 },
    { targetPct: 68,  duration: TARGET_MS * 0.20 },
    { targetPct: 84,  duration: TARGET_MS * 0.15 },
    { targetPct: 97,  duration: TARGET_MS * 0.30 },
  ];

  let stepIdx = 0;
  let elapsed = 0;

  state.progressTimer = setInterval(() => {
    if (stepIdx >= STEPS.length) return;

    const step = STEPS[stepIdx];
    elapsed += TICK_MS;
    const frac = Math.min(elapsed / step.duration, 1);
    const newPct = (stepIdx === 0 ? 0 : STEPS[stepIdx - 1].targetPct) +
                   frac * (step.targetPct - (stepIdx === 0 ? 0 : STEPS[stepIdx - 1].targetPct));

    updateProgress(Math.min(Math.floor(newPct), 97));

    if (frac >= 1) {
      stepIdx++;
      elapsed = 0;
    }
  }, TICK_MS);
}

function stopProgress(finalPct) {
  if (state.progressTimer) {
    clearInterval(state.progressTimer);
    state.progressTimer = null;
  }
  updateProgress(finalPct);
}

function updateProgress(pct) {
  state.progressValue = pct;
  progressBar.style.width = pct + '%';
  progressBar.setAttribute('aria-valuenow', pct);

  // Pick the appropriate status message
  let msg = STATUS_STEPS[0].msg;
  for (const step of STATUS_STEPS) {
    if (pct >= step.pct) msg = step.msg;
  }
  loadingStatus.textContent = msg;
}

/* =====================================================================
   9. Results display
   ===================================================================== */
function showResults(assignmentId) {
  state.currentAssignmentId = assignmentId;

  setGenerateButtonLoading(false);
  loadingSection.classList.add('hidden');
  resultsSection.classList.remove('hidden');

  if (assignmentId) {
    assignmentIdDisplay.textContent = 'ID: ' + assignmentId;
  } else {
    assignmentIdDisplay.textContent = '';
  }
}

/* =====================================================================
   10. Download handlers
   ===================================================================== */
function downloadDocx(assignmentId) {
  if (!assignmentId) return;
  window.open('/api/v1/download/docx/' + encodeURIComponent(assignmentId));
}

function downloadPdf(assignmentId) {
  if (!assignmentId) return;
  window.open('/api/v1/download/pdf/' + encodeURIComponent(assignmentId));
}

/* =====================================================================
   11. Error display
   ===================================================================== */
function showError(msg) {
  setGenerateButtonLoading(false);
  loadingSection.classList.add('hidden');
  formSection.classList.remove('hidden');
  errorSection.classList.remove('hidden');
  errorMessage.textContent = msg;
}

function hideError() {
  errorSection.classList.add('hidden');
}

/* =====================================================================
   12. Reset / Generate Another
   ===================================================================== */
function resetToForm() {
  stopProgress(0);
  state.currentAssignmentId = null;
  setGenerateButtonLoading(false);

  // Clear outputs
  assignmentIdDisplay.textContent = '';
  errorMessage.textContent = '';

  resultsSection.classList.add('hidden');
  errorSection.classList.add('hidden');
  loadingSection.classList.add('hidden');
  formSection.classList.remove('hidden');

  // Scroll back to top of form
  formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* =====================================================================
   13. UI helpers
   ===================================================================== */
function setGenerateButtonLoading(loading) {
  generateBtn.disabled = loading;
  if (loading) {
    btnText.textContent = 'Generating…';
    btnSpinner.classList.remove('hidden');
  } else {
    btnText.textContent = '🚀 Generate Assignment';
    btnSpinner.classList.add('hidden');
  }
}

function updateApiKeyLink(provider) {
  const url = PROVIDER_LINKS[provider] || '#';
  apiKeyLink.href = url;
  apiKeyLinkText.textContent = url;
}

/* =====================================================================
   14. Initialisation
   ===================================================================== */
(function init() {
  // Sync word count display
  wordCountDisplay.textContent = Number(wordCountSlider.value).toLocaleString();

  // Sync API key helper link with default provider
  updateApiKeyLink(state.selectedProvider);
})();
