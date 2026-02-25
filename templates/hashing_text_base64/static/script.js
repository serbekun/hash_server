const API_BASE_URL = window.location.origin;

async function encryptText(text, key) {
    const response = await fetch(`${API_BASE_URL}/v0/api/aes/encrypt_text`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, key })
    });

    const data = await response.json();
    if (!response.ok || data.error) {
        throw new Error(data.error || `HTTP error: ${response.status}`);
    }

    return data.result;
}

async function generateKey() {
    const response = await fetch(`${API_BASE_URL}/v0/api/aes/generate_key`);
    const data = await response.json();

    if (!response.ok || data.error) {
        throw new Error(data.error || `HTTP error: ${response.status}`);
    }

    return data.key;
}

const inputText = document.getElementById('inputText');
const keyInput = document.getElementById('keyInput');
const outputText = document.getElementById('outputText');
const convertBtn = document.getElementById('convertBtn');
const generateKeyBtn = document.getElementById('generateKeyBtn');
const copyBtn = document.getElementById('copyBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
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
    const text = inputText.value;
    const key = keyInput.value.trim();

    if (!key) {
        showError('Please enter AES key');
        return;
    }

    if (!text) {
        showError('Please enter text to encrypt');
        return;
    }

    hideError();
    loadingIndicator.classList.add('show');
    convertBtn.disabled = true;

    try {
        const result = await encryptText(text, key);
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

generateKeyBtn.addEventListener('click', async () => {
    hideError();
    generateKeyBtn.disabled = true;

    try {
        const newKey = await generateKey();
        keyInput.value = newKey;
    } catch (error) {
        showError(error.message);
    } finally {
        generateKeyBtn.disabled = false;
    }
});

copyBtn.addEventListener('click', async () => {
    if (!outputText.value.trim()) {
        return;
    }

    try {
        await navigator.clipboard.writeText(outputText.value);
    } catch (error) {
        showError('Failed to copy result');
    }
});

inputText.addEventListener('input', hideError);
keyInput.addEventListener('input', hideError);
