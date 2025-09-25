/**
 * TinyMCE Test Configuration
 * Free/GPL version with enhanced paste functionality
 */

// TinyMCE Configuration - Free Version Only
tinymce.init({
    selector: '#tinyMCEEditor',
    license_key: 'gpl', // Acknowledge GPL license for free version
    height: 500,
    menubar: true,
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
    
    // Image handling - simple data URL conversion
    images_upload_handler: function (blobInfo, success, failure) {
        // Convert to data URL for testing - in production you'd upload to server
        const reader = new FileReader();
        reader.onload = function() {
            success(reader.result);
        };
        reader.readAsDataURL(blobInfo.blob());
    },
    
    // Table default styles
    table_default_attributes: {
        'border': '1',
        'style': 'border-collapse: collapse; width: 100%;'
    },
    table_default_styles: {
        'border-collapse': 'collapse',
        'width': '100%'
    },

    // Enhanced paste configuration for Word/Google Docs
    paste_data_images: true, // Allow pasting images from clipboard
    paste_retain_style_properties: "color font-size font-family background-color", // Keep basic styling
    paste_remove_styles_if_webkit: false,
    paste_merge_formats: true,
    smart_paste: true,
    paste_word_valid_elements: "b,strong,i,em,h1,h2,h3,h4,h5,h6,p,ol,ul,li,a[href],span,color,font-size,font-color,font-family,mark,table,tr,td,th,tbody,thead,tfoot",
    
    // Handle image uploads from paste
    images_upload_handler: function (blobInfo, success, failure, progress) {
        // Convert to data URL for testing - in production you'd upload to server
        const reader = new FileReader();
        reader.onload = function() {
            success(reader.result);
        };
        reader.onerror = function() {
            failure('Image upload failed');
        };
        reader.readAsDataURL(blobInfo.blob());
    },
    
    // Custom paste preprocessing to clean up content and handle images
    paste_preprocess: function(plugin, args) {
        // Remove excessive whitespace and non-breaking spaces
        args.content = args.content.replace(/(&nbsp;\s*){2,}/gi, ' ');
        // Remove empty paragraphs
        args.content = args.content.replace(/<p[^>]*>(\s|&nbsp;)*<\/p>/gi, '');
        // Clean up span tags with only style attributes
        args.content = args.content.replace(/<span style="[^"]*">\s*<\/span>/gi, '');
        // Remove Word-specific classes
        args.content = args.content.replace(/class="Mso[^"]*"/gi, '');
        
        // Handle problematic Word image references
        args.content = args.content.replace(/<img[^>]*src=["']file:\/\/[^"']*["'][^>]*>/gi, 
            '<p><em>[Image from Word document - please re-insert using the image button above]</em></p>');
        
        // Remove v:shape and other Word-specific elements
        args.content = args.content.replace(/<v:[^>]*>/gi, '');
        args.content = args.content.replace(/<\/v:[^>]*>/gi, '');
        args.content = args.content.replace(/<o:[^>]*>/gi, '');
        args.content = args.content.replace(/<\/o:[^>]*>/gi, '');
    },
    
    // Post-process after paste
    paste_postprocess: function(plugin, args) {
        // Additional cleanup after content is processed
        console.log('Pasted content processed:', args.node);
    },

    // Setup callback
    setup: function (editor) {
        editor.on('change', function () {
            editor.save(); // Save content back to textarea
        });
    }
});

// Helper functions for testing
function getContent() {
    const content = tinymce.get('tinyMCEEditor').getContent();
    document.getElementById('html-output').textContent = content;
    document.getElementById('content-output').style.display = 'block';
    console.log('TinyMCE Content:', content);
}

function clearContent() {
    if (confirm('Clear all content?')) {
        tinymce.get('tinyMCEEditor').setContent('');
    }
}

function loadSampleContent() {
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

// Handle Word document upload with Mammoth.js
function handleWordUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Check if mammoth is available
    if (typeof mammoth === 'undefined') {
        alert('Mammoth.js library not loaded! Please check your script includes.');
        return;
    }
    
    // Show loading indicator
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
    
    // Convert Word document using Mammoth.js
    const fileReader = new FileReader();
    fileReader.onload = function(e) {
        const arrayBuffer = e.target.result;
        
        mammoth.convertToHtml(
            { arrayBuffer: arrayBuffer },
            {
                // Configuration options
                convertImage: mammoth.images.imgElement(function(image) {
                    // Convert images to base64 data URLs
                    return image.read("base64").then(function(imageBuffer) {
                        const dataUrl = `data:${image.contentType};base64,${imageBuffer}`;
                        return { src: dataUrl };
                    });
                }),
                // Style mapping for better conversion
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
            // Remove loading indicator
            document.body.removeChild(loadingMsg);
            
            // Insert converted content into TinyMCE
            if (result.value) {
                // Clean up the HTML a bit
                let cleanedHtml = result.value;
                // Remove empty paragraphs
                cleanedHtml = cleanedHtml.replace(/<p>\s*<\/p>/g, '');
                // Clean up excessive line breaks
                cleanedHtml = cleanedHtml.replace(/(<\/p>\s*){2,}/g, '</p>');
                
                tinymce.get('tinyMCEEditor').setContent(cleanedHtml);
                
                // Show success message with warnings if any
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
            // Remove loading indicator
            if (document.getElementById('word-loading')) {
                document.body.removeChild(loadingMsg);
            }
            
            console.error('Error converting Word document:', error);
            alert(`❌ Error converting Word document: ${error.message}`);
        });
    };
    
    fileReader.onerror = function() {
        // Remove loading indicator
        if (document.getElementById('word-loading')) {
            document.body.removeChild(loadingMsg);
        }
        alert('❌ Error reading file. Please try again.');
    };
    
    // Read the file as ArrayBuffer
    fileReader.readAsArrayBuffer(file);
    
    // Clear the file input so the same file can be selected again
    input.value = '';
}

// Form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tinyMCEForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Ensure TinyMCE content is saved to textarea before submission
            tinymce.triggerSave();
        });
    }
});