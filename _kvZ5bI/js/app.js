import * as api from './api_service.js';
import * as ui from './ui_manager.js';

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    const generationForm = document.getElementById('generation-form');
    const promptInput = document.getElementById('prompt-input');
    const referenceUrlInput = document.getElementById('reference-url-input');
    const jobListContainer = document.getElementById('job-list-container');
    
    let activeJobs = {};

    generationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a music prompt.');
            return;
        }

        const referenceUrl = referenceUrlInput.value.trim();

        ui.setGenerateButtonLoading(true);

        try {
            const { job_id } = await api.createTrack(prompt, referenceUrl);
            const initialJobState = await api.getJobStatus(job_id);

            if (!document.querySelector(`[data-job-id="${job_id}"]`)) {
                 ui.addJobCard(jobListContainer, initialJobState);
            }
           
            startPollingForJob(job_id);
            
            promptInput.value = '';
            referenceUrlInput.value = '';

        } catch (error) {
            console.error('Failed to create track:', error);
            alert('There was an error starting the generation job.');
        } finally {
            ui.setGenerateButtonLoading(false);
        }
    });

    function startPollingForJob(jobId) {
        if (activeJobs[jobId]) {
            clearInterval(activeJobs[jobId]);
        }

        activeJobs[jobId] = setInterval(async () => {
            try {
                const job = await api.getJobStatus(jobId);
                ui.updateJobCard(job);

                if (job.status === 'SUCCESS' || job.status === 'FAILURE') {
                    clearInterval(activeJobs[jobId]);
                    delete activeJobs[jobId];
                }
            } catch (error) {
                console.error(`Error polling for job ${jobId}:`, error);
                clearInterval(activeJobs[jobId]);
                delete activeJobs[jobId];
            }
        }, 2000);
    }
});
