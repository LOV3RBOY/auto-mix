document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    const uploadContainer = document.getElementById('upload-container');
    const dropZone = document.getElementById('file-drop-zone');
    const fileInput = document.getElementById('audio-file-input');
    const fileNameDisplay = document.getElementById('file-name');

    const loadingContainer = document.getElementById('loading-container');
    const resultsContainer = document.getElementById('results-container');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    const API_URL = 'http://127.0.0.1:8000/analyze/';

    function showLoading() {
        uploadContainer.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        loadingContainer.classList.remove('hidden');
    }

    function showResults(data) {
        document.getElementById('result-tempo').textContent = data.tempo.toFixed(2);
        document.getElementById('result-key').textContent = data.key;

        const segmentsContainer = document.getElementById('result-segments');
        segmentsContainer.innerHTML = '';
        data.segments.forEach(segment => {
            const segmentEl = document.createElement('div');
            segmentEl.className = 'bg-slate-800/50 p-3 rounded-lg flex justify-between items-center text-sm';
            
            const labelEl = document.createElement('span');
            labelEl.className = 'font-semibold text-slate-300';
            labelEl.textContent = segment.label;

            const timeEl = document.createElement('span');
            timeEl.className = 'text-slate-400';
            timeEl.textContent = `${formatTime(segment.start_time)} - ${formatTime(segment.end_time)}`;

            segmentEl.appendChild(labelEl);
            segmentEl.appendChild(timeEl);
            segmentsContainer.appendChild(segmentEl);
        });

        loadingContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        resultsContainer.classList.remove('hidden');
        uploadContainer.classList.remove('hidden'); // Show upload for another file
    }
    
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    function showError(message) {
        errorMessage.textContent = message;
        loadingContainer.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        errorContainer.classList.remove('hidden');
        uploadContainer.classList.remove('hidden');
    }

    async function analyzeFile(file) {
        if (!file) {
            showError("No file selected.");
            return;
        }

        showLoading();

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || `Server responded with status: ${response.status}`);
            }

            showResults(result);

        } catch (err) {
            console.error("Analysis error:", err);
            const msg = err.message.includes('Failed to fetch') 
                ? 'Could not connect to the analysis service. Is it running?'
                : err.message;
            showError(msg);
        }
    }

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileNameDisplay.textContent = files[0].name;
            analyzeFile(files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileNameDisplay.textContent = file.name;
            analyzeFile(file);
        }
    });
});
