// Form and state management
const form = document.querySelector('#comic-form');
const submitBtn = document.querySelector('#submit-btn');
const statusElement = document.querySelector('#status');
const resultSection = document.querySelector('#result');
const resultContent = document.querySelector('#result-content');

// Update status message
function setStatus(message, type = 'loading') {
    statusElement.textContent = message;
    statusElement.className = `status-message ${type}`;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// Format dialogue text
function formatDialogue(dialogue) {
    if (!dialogue) return 'No dialogue for this panel';
    return dialogue.replace(/\\"/g, '"');
}

// Render comic result
function renderComic(comic) {
    const panelsHtml = comic.panels.map((panel) => `
        <div class="panel">
            <h3>Panel ${panel.panel_number}: ${escapeHtml(panel.description.split(' - ')[0])}</h3>
            <p><strong>Scene:</strong> ${escapeHtml(panel.description)}</p>
            ${comic.images && comic.images[panel.panel_number] ? 
                `<img src="${comic.images[panel.panel_number]}" alt="Panel ${panel.panel_number}" loading="lazy">` : 
                '<p style="font-style: italic; color: #999;">[Illustration placeholder]</p>'}
            <p><strong>Dialogue:</strong> ${escapeHtml(formatDialogue(comic.dialogues[panel.panel_number]))}</p>
        </div>
    `).join('');

    const pdfUrl = comic.pdf_url || '#';
    resultContent.innerHTML = `
        <h2>${escapeHtml(comic.title)}</h2>
        <div class="panels-grid">
            ${panelsHtml}
        </div>
        <a href="${pdfUrl}" download class="download-link">📥 Download PDF Comic</a>
    `;
    resultSection.hidden = false;
}

// Handle form submission
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // Disable button and show loading state
    submitBtn.disabled = true;
    setStatus('🎬 Generating your comic... This may take a minute.', 'loading');
    resultSection.hidden = true;
    resultContent.innerHTML = '';

    try {
        // Collect form data
        const formData = new FormData(form);
        const payload = {
            title: formData.get('title'),
            description: formData.get('description'),
            style: formData.get('style'),
            tone: formData.get('tone'),
            characters: formData.get('characters') 
                ? formData.get('characters')
                    .split(',')
                    .map(name => name.trim())
                    .filter(Boolean)
                : null
        };

        // Send request to API
        const response = await fetch('/api/v1/comics/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const comic = await response.json();

        // Check for errors
        if (!response.ok) {
            throw new Error(comic.detail || comic.message || 'Comic generation failed');
        }

        // Success! Render the comic
        setStatus(`✅ ${comic.message}`, 'success');
        renderComic(comic);

    } catch (error) {
        console.error('Error:', error);
        setStatus(`❌ ${error.message}`, 'error');
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
    }
});

// Form input validation feedback
const titleInput = document.querySelector('#title');
const descriptionInput = document.querySelector('#description');

descriptionInput.addEventListener('input', (e) => {
    const remaining = 1000 - e.target.value.length;
    const small = e.target.parentElement.querySelector('small');
    small.textContent = `${e.target.value.length}/1000 characters`;
});

titleInput.addEventListener('input', (e) => {
    const remaining = 100 - e.target.value.length;
    const small = e.target.parentElement.querySelector('small');
    small.textContent = `${e.target.value.length}/100 characters`;
});

console.log('ComicCraft UI loaded successfully!');
