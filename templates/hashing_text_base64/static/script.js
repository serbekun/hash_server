const API_BASE_URL = window.location.origin;

async function callBase64Api(endpoint, text) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        return data.result || data.encoded || data.decoded || data.data;
    } catch (error) {
        console.error('API Error:', error);
    
        if (error.message.includes('404')) {
            throw new Error('API endpoint not found. Please check the server configuration.');
        } else if (error.message.includes('network')) {
            throw new Error('Network error. Please check your connection.');
        } else {
            throw new Error(`API request failed: ${error.message}`);
        }
    }
}

async function base64Encode(text) {
    return await callBase64Api('/v0/api/base64/encode', text);
}

async function base64Decode(text) {
    return await callBase64Api('/v0/api/base64/decode', text);
}

const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const convertBtn = document.getElementById('convertBtn');
const copyBtn = document.getElementById('copyBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const modeRadios = document.getElementsByName('mode');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

function hideError() {
    errorMessage.classList.add('hidden');
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

convertBtn.addEventListener('click', async () => {
    const text = inputText.value.trim();
    
    if (!text) {
        showError('Please enter some text to process');
        return;
    }
    
    let mode;
    for (const radio of modeRadios) {
        if (radio.checked) {
            mode = radio.value;
            break;
        }
    }

    hideError();
    
    loadingIndicator.classList.add('show');
    convertBtn.disabled = true;
    
    try {
        let result;
        if (mode === 'encode') {
            result = await base64Encode(text);
        } else {
            result = await base64Decode(text);
        }
        
        outputText.value = result;
        copyBtn.style.opacity = '1';
        
    } catch (error) {
        showError(error.message);
        outputText.value = '';
        copyBtn.style.opacity = '0';
    } finally {
        loadingIndicator.classList.remove('show');
        convertBtn.disabled = false;
    }
});

copyBtn.addEventListener('click', () => {
    if (!outputText.value.trim()) return;
    
    outputText.select();
    outputText.setSelectionRange(0, 99999);
    
    try {
        navigator.clipboard.writeText(outputText.value).then(() => {
            const copyButton = copyBtn.querySelector('button');
            const originalText = copyButton.innerHTML;
            
            copyButton.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Copied!
            `;
            
            setTimeout(() => {
                copyButton.innerHTML = originalText;
            }, 2000);
        });
    } catch (err) {
        document.execCommand('copy');
        
        const copyButton = copyBtn.querySelector('button');
        const originalText = copyButton.innerHTML;
        
        copyButton.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Copied!
        `;
        
        setTimeout(() => {
            copyButton.innerHTML = originalText;
        }, 2000);
    }
});

inputText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        convertBtn.click();
        e.preventDefault();
    }
});

inputText.addEventListener('input', hideError);


document.addEventListener('DOMContentLoaded', () => {

    inputText.value = 'Hello, World!';
    hideError();
});