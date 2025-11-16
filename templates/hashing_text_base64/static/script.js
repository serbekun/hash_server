function base64Encode(text) {
    try {
        return btoa(unescape(encodeURIComponent(text)));
    } catch (e) {
        return `Error: ${e.message}`;
    }
}

function base64Decode(text) {
    try {
        return decodeURIComponent(escape(atob(text)));
    } catch (e) {
        return `Error: ${e.message}`;
    }
}

const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const convertBtn = document.getElementById('convertBtn');
const copyBtn = document.getElementById('copyBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const modeRadios = document.getElementsByName('mode');

convertBtn.addEventListener('click', () => {
    const text = inputText.value.trim();
    
    if (!text) {
        alert('Please enter some text to process');
        return;
    }
    
    let mode;
    for (const radio of modeRadios) {
        if (radio.checked) {
            mode = radio.value;
            break;
        }
    }

    loadingIndicator.classList.add('show');

    setTimeout(() => {
        let result;
        if (mode === 'encode') {
            result = base64Encode(text);
        } else {
            result = base64Decode(text);
        }
        
        outputText.value = result;
        
        copyBtn.style.opacity = '1';

        loadingIndicator.classList.remove('show');
    }, 300);
});

copyBtn.addEventListener('click', () => {
    outputText.select();
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
});

inputText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        convertBtn.click();
    }
});