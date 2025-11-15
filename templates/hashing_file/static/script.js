document.addEventListener('DOMContentLoaded', function() {
    const encryptModeBtn = document.getElementById('encryptMode');
    const decryptModeBtn = document.getElementById('decryptMode');
    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.getElementById('fileLabel');
    const fileName = document.getElementById('fileName');
    const passwordInput = document.getElementById('password');
    const processBtn = document.getElementById('processBtn');
    const statusDiv = document.getElementById('status');
    const downloadLink = document.getElementById('downloadLink');

    let currentMode = 'encrypt';

    // Mode switch handler
    encryptModeBtn.addEventListener('click', function() {
        currentMode = 'encrypt';
        encryptModeBtn.classList.add('active');
        decryptModeBtn.classList.remove('active');
        updateProcessButtonText();
    });

    decryptModeBtn.addEventListener('click', function() {
        currentMode = 'decrypt';
        decryptModeBtn.classList.add('active');
        encryptModeBtn.classList.remove('active');
        updateProcessButtonText();
    });

    // File selection handler
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
        } else {
            fileName.textContent = 'No file selected';
        }
    });

    // Process button handler
    processBtn.addEventListener('click', function() {
        if (!fileInput.files.length) {
            showStatus('Please select a file', 'error');
            return;
        }

        if (!passwordInput.value) {
            showStatus('Please enter a password', 'error');
            return;
        }

        processFile();
    });

    function updateProcessButtonText() {
        processBtn.textContent = currentMode === 'encrypt' ? 'Encrypt File' : 'Decrypt File';
    }

    downloadLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        const filename = this.dataset.filename;
        const token = this.dataset.token;
        
        if (!filename || !token) {
            showStatus('Download data missing', 'error');
            return;
        }

        showStatus('Downloading file...', '');

        fetch('/download/hashing_photo/' + filename, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: token })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Download failed');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showStatus('Download completed!', 'success');
        })
        .catch(error => {
            showStatus('Download error: ' + error, 'error');
        });
    });

    function processFile() {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', passwordInput.value);
        formData.append('mode', currentMode);

        processBtn.disabled = true;
        showStatus('Processing file...', '');

        fetch('/hashing_file/process_file', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('File processed successfully!', 'success');
                downloadLink.dataset.filename = data.output_filename;
                downloadLink.dataset.token = data.download_token;
                downloadLink.textContent = 'Download processed file';
                downloadLink.hidden = false;
            } else {
                showStatus('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showStatus('Network error: ' + error, 'error');
        })
        .finally(() => {
            processBtn.disabled = false;
        });
    }

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = type ? type : '';
    }

    // Initialize button text
    updateProcessButtonText();
});