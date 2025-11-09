document.addEventListener('DOMContentLoaded', () => {
    const encryptModeBtn = document.getElementById('encryptMode');
    const decryptModeBtn = document.getElementById('decryptMode');
    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.getElementById('fileLabel');
    const fileName = document.getElementById('fileName');
    const passwordInput = document.getElementById('password');
    const processBtn = document.getElementById('processBtn');
    const statusDiv = document.getElementById('status');
    const downloadLink = document.getElementById('downloadLink');

    let selectedFile = null;
    let mode = 'encrypt';

    encryptModeBtn.addEventListener('click', () => {
        mode = 'encrypt';
        encryptModeBtn.classList.add('active');
        decryptModeBtn.classList.remove('active');
        fileLabel.textContent = 'choice file for encode';
    });

    decryptModeBtn.addEventListener('click', () => {
        mode = 'decrypt';
        decryptModeBtn.classList.add('active');
        encryptModeBtn.classList.remove('active');
        fileLabel.textContent = 'choice fila for decode';
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            fileName.textContent = selectedFile.name;
        } else {
            selectedFile = null;
            fileName.textContent = 'file not selected';
        }
    });

    processBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            showStatus('Error: file not selected', 'error');
            return;
        }

        const password = passwordInput.value;
        if (!password) {
            showStatus('Error: enter password', 'error');
            return;
        }

        processBtn.disabled = true;
        showStatus('doing fail ...', '');

        try {
            const fileBuffer = await readFileAsArrayBuffer(selectedFile);
            const processedData = processFile(fileBuffer, password);
            const outputExt = mode === 'encrypt' ? '.bin' : getOutputExtension(selectedFile.name);
            const outputFilename = generateOutputFilename(selectedFile.name, outputExt);
            
            downloadFile(processedData, outputFilename);
            showStatus('operation successful end', 'success');
        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
        } finally {
            processBtn.disabled = false;
        }
    });

    function readFileAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Error read file'));
            reader.readAsArrayBuffer(file);
        });
    }

    function processFile(data, password) {
        const dataArray = new Uint8Array(data);
        const passArray = new TextEncoder().encode(password);
        
        if (passArray.length === 0) {
            throw new Error('password must be exist');
        }

        const result = new Uint8Array(dataArray.length);
        for (let i = 0; i < dataArray.length; i++) {
            result[i] = dataArray[i] ^ passArray[i % passArray.length];
        }
        return result;
    }

    function generateOutputFilename(inputName, ext) {
        const baseName = inputName.includes('.') 
            ? inputName.substring(0, inputName.lastIndexOf('.')) 
            : inputName;
        return `${baseName}_${mode === 'encrypt' ? 'encrypted' : 'decrypted'}${ext}`;
    }

    function getOutputExtension(filename) {
        if (mode === 'decrypt' && filename.endsWith('.bin')) {
            return '.decrypted';
        }
        return filename.substring(filename.lastIndexOf('.'));
    }

    function downloadFile(data, filename) {
        const blob = new Blob([data], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);
        
        downloadLink.href = url;
        downloadLink.download = filename;
        downloadLink.hidden = false;
        downloadLink.textContent = `Download ${filename}`;
        downloadLink.click();
    }

    function showStatus(message, className) {
        statusDiv.textContent = message;
        statusDiv.className = '';
        if (className) statusDiv.classList.add(className);
    }
});
