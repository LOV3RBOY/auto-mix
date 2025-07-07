const statusIcons = {
    PENDING: '<i data-lucide="clock" class="w-5 h-5 text-yellow-400"></i>',
    PROCESSING: '<i data-lucide="loader-2" class="w-5 h-5 text-blue-400 animate-spin"></i>',
    SUCCESS: '<i data-lucide="check-circle" class="w-5 h-5 text-green-400"></i>',
    FAILURE: '<i data-lucide="x-circle" class="w-5 h-5 text-red-400"></i>',
};

const statusColors = {
    PENDING: 'border-yellow-400/30',
    PROCESSING: 'border-blue-400/30 animate-pulse-slow',
    SUCCESS: 'border-green-400/30',
    FAILURE: 'border-red-400/30',
};

function createStemLinks(stems) {
    if (!stems) return '';
    return Object.entries(stems).map(([name, url]) => `
        <a href="${url}" download class="flex items-center gap-2 text-sm text-gray-400 hover:text-accent transition-colors">
            <i data-lucide="music-2" class="w-4 h-4"></i>
            <span class="capitalize">${name}</span>
        </a>
    `).join('');
}

function createJobCardHTML(job) {
    const { job_id, status, prompt, result } = job;
    const progress = result?.progress || 0;
    const step = result?.step || 'Initializing...';

    const colorClass = statusColors[status] || 'border-gray-700';

    return `
        <div id="job-${job_id}" data-job-id="${job_id}" class="job-card bg-gray-800/50 border ${colorClass} rounded-lg p-5 flex flex-col gap-4">
            <div class="flex justify-between items-start gap-4">
                <p class="font-medium text-gray-300 flex-1 break-words">"${prompt}"</p>
                <div class="flex items-center gap-2 text-sm font-semibold status-indicator">
                    ${statusIcons[status]}
                    <span>${status}</span>
                </div>
            </div>
            
            <div class="progress-section">
                <div class="flex justify-between items-center mb-1 text-sm text-gray-400">
                    <span class="step-label">${step}</span>
                    <span class="progress-label">${progress}%</span>
                </div>
                <div class="progress-bar-container w-full bg-gray-700">
                    <div class="progress-bar bg-accent" style="width: ${progress}%;"></div>
                </div>
            </div>

            <div class="results-section hidden">
                <!-- Results will be populated here -->
            </div>
        </div>
    `;
}

function updateResultsSection(cardElement, job) {
    const resultsContainer = cardElement.querySelector('.results-section');
    if (!resultsContainer) return;

    let content = '';
    if (job.status === 'SUCCESS') {
        resultsContainer.classList.remove('hidden');
        content = `
            <div class="mt-2 pt-4 border-t border-gray-700">
                <h4 class="text-md font-semibold mb-3 text-white">Downloads</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                     <div>
                        <a href="${job.result.final_track_url}" download class="block bg-accent hover:bg-accent-hover text-white font-bold py-2 px-4 rounded-md transition w-full text-center">
                            <i data-lucide="download" class="inline w-4 h-4 mr-2"></i>Final Mix (.wav)
                        </a>
                     </div>
                     <div class="flex flex-col gap-2">
                        <p class="text-sm font-semibold text-gray-300">Stems:</p>
                        <div class="grid grid-cols-2 gap-x-4 gap-y-1">
                            ${createStemLinks(job.result.stems)}
                        </div>
                     </div>
                </div>
            </div>
        `;
    } else if (job.status === 'FAILURE') {
        resultsContainer.classList.remove('hidden');
        content = `
             <div class="mt-2 pt-4 border-t border-gray-700 text-red-400 bg-red-500/10 p-3 rounded-md">
                <p class="font-semibold flex items-center gap-2"><i data-lucide="alert-triangle" class="w-4 h-4"></i>Error:</p>
                <p class="text-sm">${job.result.error}</p>
             </div>
        `;
    }

    if (content) {
        resultsContainer.innerHTML = content;
        lucide.createIcons({
            nodes: [resultsContainer]
        });
    }
}


export function addJobCard(container, job) {
    const emptyMessage = document.getElementById('empty-queue-message');
    if (emptyMessage) {
        emptyMessage.classList.add('hidden');
    }
    const cardHTML = createJobCardHTML(job);
    container.insertAdjacentHTML('afterbegin', cardHTML);
    const newCard = container.firstChild;
    lucide.createIcons({
        nodes: [newCard.querySelector('.status-indicator')]
    });
}

export function updateJobCard(job) {
    const card = document.getElementById(`job-${job.job_id}`);
    if (!card) {
        addJobCard(document.getElementById('job-list-container'), job);
        return;
    }
    

    const statusIndicator = card.querySelector('.status-indicator');
    const newStatusIcon = statusIcons[job.status] || '';
    if (statusIndicator.innerHTML !== newStatusIcon) {
        statusIndicator.innerHTML = `
            ${newStatusIcon}
            <span>${job.status}</span>
        `;
        lucide.createIcons({ nodes: [statusIndicator] });
    }
    
    card.className = 'job-card bg-gray-800/50 border rounded-lg p-5 flex flex-col gap-4';
    card.classList.add(statusColors[job.status] || 'border-gray-700');



    const stepLabel = card.querySelector('.step-label');
    const progressLabel = card.querySelector('.progress-label');
    const progressBar = card.querySelector('.progress-bar');
    const progressSection = card.querySelector('.progress-section');
    
    if (job.status === 'SUCCESS' || job.status === 'FAILURE') {
        if(progressSection) progressSection.classList.add('hidden');
        updateResultsSection(card, job);
    } else {
        if(progressSection) progressSection.classList.remove('hidden');
        if (stepLabel) stepLabel.textContent = job.result.step;
        if (progressLabel) progressLabel.textContent = `${job.result.progress}%`;
        if (progressBar) progressBar.style.width = `${job.result.progress}%`;
    }
}

export function setGenerateButtonLoading(isLoading) {
    const button = document.getElementById('generate-button');
    const buttonText = button.querySelector('span');
    const buttonIcon = button.querySelector('i');
    const spinner = document.getElementById('generate-spinner');

    if (isLoading) {
        button.disabled = true;
        buttonText.textContent = 'Generating...';
        buttonIcon.classList.add('hidden');
        spinner.classList.remove('hidden');
    } else {
        button.disabled = false;
        buttonText.textContent = 'Generate';
        buttonIcon.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}
