window.tinyMCEInitialized = window.tinyMCEInitialized || false;
if (window.__ADMIN_DASHBOARD_SCRIPT_LOADED__) {
    console.log("admin_dashboard.js already loaded, skipping re-execution.");
    throw new Error("Duplicate load prevented");
}
window.__ADMIN_DASHBOARD_SCRIPT_LOADED__ = true;

// ====== GLOBAL ERROR SUPPRESSION ======
window.addEventListener('error', function (e) {
    if (e.message && (
        e.message.includes('Cannot read properties of undefined (reading \'then\')') ||
        e.message.includes('Cannot read properties of null') ||
        e.message.includes('Failed to upload image')
    )) {
        console.warn('Suppressed known TinyMCE error:', e.message);
        e.preventDefault();
        return false;
    }
});

window.addEventListener('unhandledrejection', function (e) {
    if (e.reason && e.reason.message && (
        e.reason.message.includes('image') ||
        e.reason.message.includes('upload') ||
        e.reason.message.includes('Cannot read properties')
    )) {
        console.warn('Suppressed TinyMCE promise rejection:', e.reason.message);
        e.preventDefault();
        return false;
    }
});

// ====== TAB CHECK HELPER ======
function isTinyMCETabActive() {
    const tab = document.getElementById('tinymce-tab');
    const pane = document.getElementById('tinymce');
    return (tab && tab.classList.contains('active')) ||
           (pane && pane.classList.contains('active', 'show'));
}

// ====== INITIALIZATION ======
document.addEventListener('DOMContentLoaded', function () {
    const tinymceTab = document.getElementById('tinymce-tab');
    const form = document.getElementById('tinyMCEForm');
    const saveBtn = document.getElementById('saveContentBtn');
    const importBtn = document.getElementById('importWordBtn');

    if (saveBtn) saveBtn.disabled = true;
    if (importBtn) importBtn.disabled = true;

    // Initialize when TinyMCE tab is active or clicked
    if (tinymceTab) {
        tinymceTab.addEventListener('shown.bs.tab', tryInitTinyMCE);
        tinymceTab.addEventListener('click', tryInitTinyMCE);
    }

    // Auto-init on page load
    setTimeout(function () {
        if (!tinyMCEInitialized && document.getElementById('tinyMCEEditor')) {
            console.log('Auto-initializing TinyMCE on page load...');
            initTinyMCE(saveBtn, importBtn);
            tinyMCEInitialized = true;
        }
    }, 500);

    // Save content trigger
    if (form) {
        form.addEventListener('submit', function () {
            if (tinyMCEInitialized && tinymce.get('tinyMCEEditor')) {
                tinymce.triggerSave();
            }
        });
    }

    // ====== Dynamic Input Hint ======
    const unitField = document.getElementById("unit_code");
    const degreeField = document.getElementById("degree_type_target");
    const hint = document.getElementById("input-hint");

    function updateHint() {
        if (!hint || !unitField || !degreeField) return;

        const unit = (unitField.value || "").trim().toUpperCase();
        const degree = (degreeField.value || "").trim().toLowerCase();
        const hasUnit = unit && unit !== "ALL" && unit !== "*";
        const hasDegree = degree === "masters" || degree === "phd";

        if (hasUnit && hasDegree) {
            hint.innerHTML = "⚠️ You’ve entered both a unit code and a degree type. Only one is needed.";
            hint.classList.remove("text-muted");
            hint.classList.add("text-warning");
        } else if (hasUnit) {
            hint.innerHTML = "💡 Targeting a specific unit; you can leave degree type blank.";
            hint.classList.remove("text-warning");
            hint.classList.add("text-muted");
        } else if (hasDegree) {
            hint.innerHTML = "💡 Targeting a degree type; you can leave unit code blank.";
            hint.classList.remove("text-warning");
            hint.classList.add("text-muted");
        } else {
            hint.innerHTML = "💡 If you’re using a unit code, leave degree type blank — and vice versa.";
            hint.classList.remove("text-warning");
            hint.classList.add("text-muted");
        }
    }

    if (unitField && degreeField) {
        unitField.addEventListener("input", updateHint);
        degreeField.addEventListener("change", updateHint);
        updateHint();
    }
});

// ====== TinyMCE Initialization ======
function tryInitTinyMCE() {
    setTimeout(function () {
        if (!tinyMCEInitialized && document.getElementById('tinyMCEEditor')) {
            console.log('Initializing TinyMCE (tab event)...');
            initTinyMCE(
                document.getElementById('saveContentBtn'),
                document.getElementById('importWordBtn')
            );
            tinyMCEInitialized = true;
        }
    }, 300);
}

function initTinyMCE(saveBtn, importBtn) {
    console.log('Attempting to initialize TinyMCE...');

    if (!document.getElementById('tinyMCEEditor')) return;
    if (typeof tinymce === 'undefined') return;

    try {
        tinymce.init({
            selector: '#tinyMCEEditor',
            license_key: 'gpl',
            height: 500,
            menubar: true,
            promotion: false,
            branding: false,
            statusbar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar:
                'undo redo | blocks | bold italic underline strikethrough | ' +
                'alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | forecolor backcolor | link image media | table | code | fullscreen preview help',
            content_style:
                'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; font-size: 16px; line-height: 1.6; }',
            automatic_uploads: false,
            setup: function (editor) {
                editor.on('init', function () {
                    console.log('✅ TinyMCE initialized successfully!');
                    tinyMCEInitialized = true;
                    if (saveBtn) saveBtn.disabled = false;
                    if (importBtn) importBtn.disabled = false;
                });
                editor.on('change', () => editor.save());
            }
        });
    } catch (error) {
        console.error('Error initializing TinyMCE:', error);
    }
}

// ====== CLEAR CONTENT ======
function clearContent() {
    if (!tinyMCEInitialized || !tinymce.get('tinyMCEEditor')) {
        alert('TinyMCE not initialized yet.');
        return;
    }
    if (confirm('Clear all content? This action cannot be undone.')) {
        tinymce.get('tinyMCEEditor').setContent('');
    }
}

// ====== LOAD SAMPLE CONTENT ======
function loadSampleContent() {
    if (!tinyMCEInitialized || !tinymce.get('tinyMCEEditor')) {
        alert('TinyMCE not initialized yet.');
        return;
    }
    tinymce.get('tinyMCEEditor').setContent(`
        <h2>Sample Email Content</h2>
        <p>This is a sample email with various formatting options:</p>
        <ul>
            <li><strong>Bold text example</strong></li>
            <li><em>Italic text example</em></li>
            <li><u>Underlined text</u></li>
            <li><span style="color: #e74c3c;">Colored text in red</span></li>
            <li><span style="background-color: #f1c40f;">Highlighted text</span></li>
        </ul>
    `);
}

// ====== WORD DOC IMPORT HANDLER ======
function handleWordUpload(input) {
    if (!tinyMCEInitialized || !tinymce.get('tinyMCEEditor')) {
        alert('TinyMCE not initialized yet.');
        return;
    }

    const file = input.files[0];
    if (!file) return;
    if (typeof mammoth === 'undefined') {
        alert('Mammoth.js library not loaded!');
        return;
    }

    const loadingMsg = document.createElement('div');
    loadingMsg.id = 'word-loading';
    loadingMsg.innerHTML = `
        <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background: white; padding: 20px; border-radius: 8px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    border: 2px solid #007bff; z-index: 1000;">
            <p>Converting Word document: <strong>${file.name}</strong></p>
        </div>`;
    document.body.appendChild(loadingMsg);

    const reader = new FileReader();
    reader.onload = function (e) {
        mammoth.convertToHtml({ arrayBuffer: e.target.result })
            .then(result => {
                document.body.removeChild(loadingMsg);
                tinymce.get('tinyMCEEditor').setContent(result.value);
                alert('✅ Word document imported successfully!');
            })
            .catch(error => {
                document.body.removeChild(loadingMsg);
                alert(`❌ Error converting document: ${error.message}`);
            });
    };
    reader.readAsArrayBuffer(file);
    input.value = '';
}

/* ===========================
   HTMX Integration & Flashes
   =========================== */

if (!window.__FLASH_HANDLER_BOUND__) {
  window.__FLASH_HANDLER_BOUND__ = true;

  document.body.addEventListener("htmx:afterOnLoad", (event) => {
    const xhr = event.detail.xhr;
    if (!xhr) return;
    const text = xhr.responseText || "";

    if (text.includes("alert-dismissible")) {
      const flashContainer = document.getElementById("flash-container");
      if (!flashContainer) return;

      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = text;
      const newAlerts = tempDiv.querySelectorAll(".alert");
      if (newAlerts.length > 0) {
        flashContainer.innerHTML = "";
        newAlerts.forEach(a => flashContainer.appendChild(a));
        fadeOutFlashes();
      }
    }
  });

  document.body.addEventListener("refresh-flashes", () => {
    fetch("/admin/_flashes")
      .then(r => r.text())
      .then(html => {
        const fc = document.getElementById("flash-container");
        if (fc) {
          fc.innerHTML = html;
          fadeOutFlashes();
        }
      });
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail.target && event.detail.target.id === "weekly-table-container") {
      console.log("✅ Weekly content table updated successfully!");
    }
  });
}

/* ===========================
   Flash fade-out animation
   =========================== */
function fadeOutFlashes(delay = 5000) {
  const alerts = document.querySelectorAll("#flash-container .alert");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-10px)";
      setTimeout(() => alert.remove(), 600);
    }, delay);
  });
}

/* ===========================
   Info message below fields
   =========================== */
document.addEventListener("DOMContentLoaded", setupInfoMessage);
document.body.addEventListener("htmx:afterSwap", setupInfoMessage);

function setupInfoMessage() {
  const unitField = document.querySelector("#unit_code");
  const degreeSelect = document.querySelector("#degree_type_target");
  if (!unitField || !degreeSelect) return;

  let note = document.getElementById("targeting-note");
  if (!note) {
    note = document.createElement("small");
    note.id = "targeting-note";
    note.className = "form-text text-muted mt-1";
    note.style.display = "block";
    note.style.fontStyle = "italic";
    unitField.insertAdjacentElement("afterend", note);
  }

  const updateHighlight = () => {
    const unitVal = unitField.value.trim();
    const degreeVal = degreeSelect.value.trim().toLowerCase();

    if (unitVal && degreeVal && degreeVal !== "none") {
      note.innerHTML = "⚠️ You’ve entered both a unit code and a degree type. Only one is needed.";
      note.classList.add("text-warning");
    } else if (unitVal) {
      note.innerHTML = "🎯 Targeting a specific <strong>unit</strong>: leave degree type blank.";
      note.classList.remove("text-warning");
    } else if (degreeVal && degreeVal !== "none") {
      note.innerHTML = "🎓 Targeting a <strong>degree type</strong>: leave unit code blank.";
      note.classList.remove("text-warning");
    } else {
      note.innerHTML = `
        💡 Targeting a specific unit: you can leave <strong>degree type</strong> blank.<br>
        💡 Targeting by degree type: you can leave <strong>unit code</strong> blank.
      `;
      note.classList.remove("text-warning");
    }
  };

  updateHighlight();
  unitField.addEventListener("input", updateHighlight);
  degreeSelect.addEventListener("change", updateHighlight);
}