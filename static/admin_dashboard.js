/**
 * Admin Dashboard JavaScript
 * Handles TinyMCE initialization, Word document import, and error suppression
 */

// Don't load the original tinymce.js - we'll initialize manually for tab compatibility
let tinyMCEInitialized = false;

// Global error handler to suppress known TinyMCE errors
window.addEventListener('error', function(e) {
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

// Suppress unhandled promise rejections related to TinyMCE
window.addEventListener('unhandledrejection', function(e) {
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

// Function to check if TinyMCE tab is active
function isTinyMCETabActive() {
    const tinymceTab = document.getElementById('tinymce-tab');
    const tinymceTabPane = document.getElementById('tinymce');
    return (tinymceTab && tinymceTab.classList.contains('active')) || 
           (tinymceTabPane && tinymceTabPane.classList.contains('active', 'show'));
}

// Initialize TinyMCE when the TinyMCE tab is shown
document.addEventListener('DOMContentLoaded', function() {
    const tinymceTab = document.getElementById('tinymce-tab');
    const tinymceTabPane = document.getElementById('tinymce');
    
    // Check if TinyMCE tab is already active on page load
    if (isTinyMCETabActive()) {
        console.log('TinyMCE tab is active on page load, initializing...');
        setTimeout(function() {
            if (!tinyMCEInitialized && document.getElementById('tinyMCEEditor')) {
                initTinyMCE();
                tinyMCEInitialized = true;
            }
        }, 300);
    }
    
    // Also initialize when tab is clicked/shown
    if (tinymceTab) {
        tinymceTab.addEventListener('shown.bs.tab', function (e) {
            console.log('TinyMCE tab shown event triggered');
            // Small delay to ensure the tab content is fully visible
            setTimeout(function() {
                if (!tinyMCEInitialized && document.getElementById('tinyMCEEditor')) {
                    initTinyMCE();
                    tinyMCEInitialized = true;
                }
            }, 200);
        });
        
        // Backup: also try to initialize on click
        tinymceTab.addEventListener('click', function(e) {
            console.log('TinyMCE tab clicked');
            setTimeout(function() {
                if (!tinyMCEInitialized && document.getElementById('tinyMCEEditor')) {
                    console.log('Initializing TinyMCE after tab click');
                    initTinyMCE();
                    tinyMCEInitialized = true;
                }
            }, 500);
        });
    }
    
    // Initialize form submission handler
    const form = document.getElementById('tinyMCEForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (tinyMCEInitialized && tinymce.get('tinyMCEEditor')) {
                tinymce.triggerSave();
            }
        });
    }

    // Bulk DOCX handlers
    const bulkInput = document.getElementById('bulkDocxInput');
    const bulkBtn = document.getElementById('bulkUploadBtn');
    const bulkClearBtn = document.getElementById('bulkClearBtn');
    if (bulkInput && bulkBtn && bulkClearBtn) {
        setupBulkDocxHandlers(bulkInput, bulkBtn, bulkClearBtn);
    }
});

function initTinyMCE() {
    console.log('Attempting to initialize TinyMCE...');
    
    if (!document.getElementById('tinyMCEEditor')) {
        console.error('TinyMCE editor element not found!');
        return;
    }
    
    if (typeof tinymce === 'undefined') {
        console.error('TinyMCE library not loaded!');
        return;
    }
    
    try {
        tinymce.init({
            selector: '#tinyMCEEditor',
            license_key: 'gpl',
            base_url: '/static/tinymce/js/tinymce',
            suffix: '.min',
            height: 500,
            menubar: true,
            promotion: false,
            branding: false,
            statusbar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount', 'paste'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic underline strikethrough | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | forecolor backcolor | link image media | ' +
                'table | code | fullscreen preview help',
            content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; font-size: 16px; line-height: 1.6; }',
            
            images_upload_handler: function (blobInfo, success, failure) {
                try {
                    if (!blobInfo || !blobInfo.blob) {
                        console.warn('Invalid blob info for image upload');
                        if (failure) failure('Invalid image data');
                        return;
                    }
                    
                    const reader = new FileReader();
                    reader.onload = function() {
                        try {
                            if (success) success(reader.result);
                        } catch (error) {
                            console.error('Error in success callback:', error);
                            if (failure) failure('Image processing failed');
                        }
                    };
                    reader.onerror = function() {
                        console.error('FileReader error');
                        if (failure) failure('Failed to read image file');
                    };
                    reader.readAsDataURL(blobInfo.blob());
                } catch (error) {
                    console.error('Error in images_upload_handler:', error);
                    if (failure) failure('Image upload handler error');
                }
            },
            
            table_default_attributes: {
                'border': '1',
                'style': 'border-collapse: collapse; width: 100%;'
            },
            table_default_styles: {
                'border-collapse': 'collapse',
                'width': '100%'
            },

            paste_data_images: true,
            automatic_uploads: false,
            images_reuse_filename: true,
            paste_retain_style_properties: "color font-size font-family background-color",
            paste_remove_styles_if_webkit: false,
            paste_merge_formats: true,
            smart_paste: true,
            paste_word_valid_elements: "b,strong,i,em,h1,h2,h3,h4,h5,h6,p,ol,ul,li,a[href],span,color,font-size,font-color,font-family,mark,table,tr,td,th,tbody,thead,tfoot",
            
            paste_preprocess: function(plugin, args) {
                args.content = args.content.replace(/(&nbsp;\s*){2,}/gi, ' ');
                args.content = args.content.replace(/<p[^>]*>(\s|&nbsp;)*<\/p>/gi, '');
                args.content = args.content.replace(/<span style="[^"]*">\s*<\/span>/gi, '');
                args.content = args.content.replace(/class="Mso[^"]*"/gi, '');
                args.content = args.content.replace(/<img[^>]*src=["']file:\/\/[^"']*["'][^>]*>/gi, 
                    '<p><em>[Image from Word document - please re-insert using the image button above]</em></p>');
                args.content = args.content.replace(/<v:[^>]*>/gi, '');
                args.content = args.content.replace(/<\/v:[^>]*>/gi, '');
                args.content = args.content.replace(/<o:[^>]*>/gi, '');
                args.content = args.content.replace(/<\/o:[^>]*>/gi, '');
            },

            setup: function (editor) {
                editor.on('change', function () {
                    editor.save();
                });
                
                editor.on('init', function() {
                    console.log('TinyMCE initialized successfully!');
                });
                
                // Suppress known TinyMCE image upload errors
                editor.on('ImageUploadError', function(e) {
                    console.warn('TinyMCE ImageUploadError suppressed:', e);
                    e.preventDefault();
                });
                
                // Handle any notification errors related to image processing
                editor.on('BeforeExecCommand', function(e) {
                    if (e.command === 'mceNotification' && e.value && e.value.text && 
                        e.value.text.includes('Cannot read properties of undefined')) {
                        console.warn('Suppressing TinyMCE notification error:', e.value.text);
                        e.preventDefault();
                    }
                });
            }
        });
    } catch (error) {
        console.error('Error initializing TinyMCE:', error);
    }
}

function clearContent() {
    if (!tinyMCEInitialized || !tinymce.get('tinyMCEEditor')) {
        alert('TinyMCE not initialized yet.');
        return;
    }
    if (confirm('Clear all content? There is no turning back now!')) {
        tinymce.get('tinyMCEEditor').setContent('');
    }
}

function loadSampleContent() {
    if (!tinyMCEInitialized || !tinymce.get('tinyMCEEditor')) {
        alert('TinyMCE not initialized yet.');
        return;
    }
    const sampleContent = `
        <h2>Sample Email Content</h2>
        <p>This is a sample email with various formatting options:</p>
        
        <ul>
            <li><strong>Bold text example</strong></li>
            <li><em>Italic text example</em></li>
            <li><u>Underlined text</u></li>
            <li><span style="color: #e74c3c;">Colored text in red</span></li>
            <li><span style="background-color: #f1c40f;">Highlighted text</span></li>
        </ul>

        <blockquote style="border-left: 4px solid #3498db; padding-left: 20px; margin: 20px 0; font-style: italic;">
            This is a blockquote to test formatting capabilities.
        </blockquote>

        <h3>Code Sample</h3>
        <pre><code>function hello() {
    console.log("Hello from TinyMCE!");
}</code></pre>

        <p><a href="https://www.tinymce.com" target="_blank">Visit TinyMCE Website</a></p>
    `;
    tinymce.get('tinyMCEEditor').setContent(sampleContent);
}

function handleWordUpload(input) {
    if (!tinyMCEInitialized || !tinymce.get('tinyMCEEditor')) {
        alert('TinyMCE not initialized yet. Please click on the TinyMCE tab first.');
        return;
    }
    
    const file = input.files[0];
    if (!file) return;
    
    if (typeof mammoth === 'undefined') {
        alert('Mammoth.js library not loaded! Please check your script includes.');
        return;
    }
    
    const loadingMsg = document.createElement('div');
    loadingMsg.id = 'word-loading';
    loadingMsg.innerHTML = `
        <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                    background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                    border: 2px solid #007bff; z-index: 1000;">
            <div style="text-align: center;">
                <div style="border: 3px solid #f3f3f3; border-top: 3px solid #007bff; border-radius: 50%; 
                           width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 0 auto 10px;"></div>
                <p>Converting Word document: <strong>${file.name}</strong></p>
                <p style="font-size: 12px; color: #666;">Processing images and formatting...</p>
            </div>
        </div>
        <style>
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    `;
    document.body.appendChild(loadingMsg);
    
    const fileReader = new FileReader();
    fileReader.onload = function(e) {
        const arrayBuffer = e.target.result;
        
        mammoth.convertToHtml(
            { arrayBuffer: arrayBuffer },
            {
                convertImage: mammoth.images.imgElement(function(image) {
                    try {
                        // Check if image and its methods exist
                        if (!image || typeof image.read !== 'function') {
                            console.warn('Invalid image object or read method not available');
                            return Promise.resolve({ 
                                src: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
                                alt: '[Image placeholder]'
                            });
                        }
                        
                        const readResult = image.read("base64");
                        
                        // Check if read method returns a Promise
                        if (!readResult || typeof readResult.then !== 'function') {
                            console.warn('Image read method did not return a Promise');
                            return Promise.resolve({ 
                                src: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
                                alt: '[Image placeholder]'
                            });
                        }
                        
                        return readResult.then(function(imageBuffer) {
                            console.log('Image processed successfully');
                            const dataUrl = `data:${image.contentType || 'image/png'};base64,${imageBuffer}`;
                            return { 
                                src: dataUrl,
                                alt: image.altText || 'Imported image',
                                // Add attributes to prevent TinyMCE from treating this as an upload
                                'data-mce-src': dataUrl,
                                'data-mce-selected': '1'
                            };
                        }).catch(function(error) {
                            console.error('Error processing image:', error);
                            return Promise.resolve({ 
                                src: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
                                alt: '[Image processing error]'
                            });
                        });
                    } catch (error) {
                        console.error('Error in convertImage function:', error);
                        return Promise.resolve({ 
                            src: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
                            alt: '[Image conversion error]'
                        });
                    }
                }),
                styleMap: [
                    "p[style-name='Heading 1'] => h1:fresh",
                    "p[style-name='Heading 2'] => h2:fresh",
                    "p[style-name='Heading 3'] => h3:fresh",
                    "p[style-name='Title'] => h1.title:fresh",
                    "p[style-name='Subtitle'] => h2.subtitle:fresh",
                    "r[style-name='Strong'] => strong"
                ]
            }
        )
        .then(function(result) {
            document.body.removeChild(loadingMsg);
            
            if (result.value) {
                let cleanedHtml = result.value;
                cleanedHtml = cleanedHtml.replace(/<p>\s*<\/p>/g, '');
                cleanedHtml = cleanedHtml.replace(/(<\/p>\s*){2,}/g, '</p>');
                
                tinymce.get('tinyMCEEditor').setContent(cleanedHtml);
                
                let message = `✅ Word document imported successfully!\n\nDocument: ${file.name}`;
                
                if (result.messages.length > 0) {
                    message += `\n\n⚠️ Conversion notes:\n`;
                    result.messages.forEach(msg => {
                        message += `• ${msg.message}\n`;
                    });
                }
                
                alert(message);
                console.log('Mammoth conversion messages:', result.messages);
            } else {
                alert('❌ No content could be extracted from the Word document.');
            }
        })
        .catch(function(error) {
            if (document.getElementById('word-loading')) {
                document.body.removeChild(loadingMsg);
            }
            console.error('Error converting Word document:', error);
            
            // Provide more specific error messages
            let errorMessage = '❌ Error converting Word document: ';
            if (error.message && error.message.includes('image')) {
                errorMessage += 'There was an issue processing images in the document. The text content should still be imported correctly.';
            } else if (error.message) {
                errorMessage += error.message;
            } else {
                errorMessage += 'Unknown error occurred during conversion.';
            }
            
            alert(errorMessage);
        });
    };
    
    fileReader.onerror = function() {
        if (document.getElementById('word-loading')) {
            document.body.removeChild(loadingMsg);
        }
        alert('❌ Error reading file. Please try again.');
    };
    
    fileReader.readAsArrayBuffer(file);
    input.value = '';
}

// -------------------- Bulk DOCX Upload --------------------
let parsedBulkMessages = [];

function setupBulkDocxHandlers(fileInput, uploadBtn, clearBtn) {
    const preview = document.getElementById('bulkPreview');
    parsedBulkMessages = [];
    uploadBtn.disabled = true;

    clearBtn.addEventListener('click', () => {
        fileInput.value = '';
        parsedBulkMessages = [];
        if (preview) preview.innerHTML = '';
        uploadBtn.disabled = true;
    });

    fileInput.addEventListener('change', async () => {
        const files = Array.from(fileInput.files || []);
        if (!files.length) return;
        if (typeof mammoth === 'undefined') {
            alert('Mammoth.js not loaded');
            return;
        }

        parsedBulkMessages = [];
        if (preview) preview.innerHTML = '';

        // Parse each file sequentially to control memory usage
        for (const file of files) {
            const summary = await parseSingleDocx(file).catch(err => ({ error: String(err) }));
            parsedBulkMessages.push(summary);
        }

        // Render preview
        if (preview) {
            preview.innerHTML = parsedBulkMessages.map((m, idx) => {
                if (m && !m.error) {
                    const targets = [m.degree_type_target || 'all', m.location_target || 'all', m.stage_target || 'all'].join(', ');
                    return `
                        <div class="border rounded p-2 mb-2">
                          <div class="fw-bold">${escapeHtml(m.title || '(No title)')}</div>
                          <div class="small text-muted">week: ${m.week_released ?? 'unknown'} — targets: ${targets}</div>
                          <div class="small">from: ${escapeHtml(m.file_name || '')}</div>
                        </div>`;
                } else {
                    return `
                        <div class="border rounded p-2 mb-2 bg-light">
                          <div class="text-danger">Failed to parse ${escapeHtml((m && m.file_name) || 'file')}</div>
                          <div class="small">${escapeHtml((m && m.error) || 'Unknown error')}</div>
                        </div>`;
                }
            }).join('');
        }

        uploadBtn.disabled = parsedBulkMessages.every(m => m.error);
    });

    uploadBtn.addEventListener('click', async () => {
        const valid = parsedBulkMessages.filter(m => m && !m.error);
        if (!valid.length) {
            alert('No valid messages to upload.');
            return;
        }

        try {
            const resp = await fetch('/admin/bulk/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ messages: valid })
            });
            if (!resp.ok) {
                const text = await resp.text();
                throw new Error(text || `HTTP ${resp.status}`);
            }
            const data = await resp.json();
            alert(`Uploaded ${data.saved} messages. ${data.skipped} skipped.`);
            window.location.reload();
        } catch (err) {
            console.error('Bulk upload failed', err);
            alert(`Bulk upload failed: ${err}`);
        }
    });
}

async function parseSingleDocx(file) {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.convertToHtml({ arrayBuffer });
    const html = (result.value || '').trim();

    const text = stripHtml(html).trim();
    const title = inferTitle(file.name, html, text);
    const week = inferWeekNumber(file.name, text);
    const degreeType = inferDegreeType(file.name, text);

    return {
        file_name: file.name,
        title: title || file.name.replace(/\.docx$/i, ''),
        content: html,
        degree_code: 'ALL',
        week_released: week || 1,
        scheduled_at: null,
        degree_type_target: degreeType,
        location_target: null,
        stage_target: null
    };
}

function stripHtml(html) {
    const div = document.createElement('div');
    div.innerHTML = html;
    return (div.textContent || div.innerText || '').replace(/\s+/g, ' ');
}

function inferTitle(fileName, html, text) {
    // Prefer first h1/h2
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    const h = tmp.querySelector('h1, h2, h3');
    if (h && h.textContent) return h.textContent.trim();

    // Fallback: filename before extension and week markers
    let base = fileName.replace(/\.docx$/i, '').replace(/_/g, ' ').trim();
    base = base.replace(/\bweek\s*\d+\b/ig, '').replace(/\bwk\s*\d+\b/ig, '').trim();
    return base || null;
}

function inferWeekNumber(fileName, text) {
    // Try filename: week12 or wk12
    let m = fileName.match(/(?:week|wk)\s*(\d{1,2})/i);
    if (m) return parseInt(m[1], 10);
    // Try text: Week 5, Wk 3
    m = text.match(/\b(?:week|wk)\s*(\d{1,2})\b/i);
    if (m) return parseInt(m[1], 10);
    return null;
}

function inferDegreeType(fileName, text) {
    const s = `${fileName} ${text}`.toLowerCase();
    if (/(masters|master's|coursework)/i.test(s)) return 'masters';
    if (/(phd|doctoral|doctorate|research)/i.test(s)) return 'phd';
    return null;
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"]|'/g, function(c) {
        return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'})[c];
    });
}