const jobs = {};
let jobCounter = 0;

const SIMULATION_STAGES = [
    { step: 'Parsing Prompt', duration: 3000, progress: 20 },
    { step: 'Analyzing Style', duration: 4000, progress: 40 },
    { step: 'Generating Sound', duration: 10000, progress: 80 },
    { step: 'Mixing & Mastering', duration: 5000, progress: 95 },
    { step: 'Finalizing', duration: 2000, progress: 100 },
];

async function _simulateJobProgress(jobId) {
    const job = jobs[jobId];
    if (!job) return;

    job.status = 'PROCESSING';
    
    for (const stage of SIMULATION_STAGES) {
        if (stage.step === 'Analyzing Style' && !job.reference_track_url) {
            continue; 
        }
        await new Promise(resolve => setTimeout(resolve, 100));
        job.result.step = stage.step;
        job.result.progress = stage.progress;
        await new Promise(resolve => setTimeout(resolve, stage.duration));
    }

    job.status = 'SUCCESS';
    job.result.step = 'Completed';
    job.result.final_track_url = `/audio/final_mix_${jobId}.wav`;
    job.result.stems = {
        drums: `/stems/${jobId}_drums.wav`,
        bass: `/stems/${jobId}_bass.wav`,
        synth: `/stems/${jobId}_synth.wav`,
        lead: `/stems/${jobId}_lead.wav`,
    };
    

    if (Math.random() < 0.1) {
        job.status = 'FAILURE';
        job.result.step = 'Failed';
        job.result.error = 'Audio generation failed due to unexpected model error.';
        delete job.result.final_track_url;
        delete job.result.stems;
    }
}

export function createTrack(prompt, reference_track_url) {
    return new Promise((resolve) => {
        jobCounter++;
        const jobId = `job_${jobCounter}${Date.now().toString().slice(-6)}`;
        
        jobs[jobId] = {
            job_id: jobId,
            prompt,
            reference_track_url,
            status: 'PENDING',
            result: {
                step: 'Queued',
                progress: 0,
            }
        };

        setTimeout(() => {
            _simulateJobProgress(jobId);
        }, 1000);

        resolve({ job_id: jobId });
    });
}

export function getJobStatus(jobId) {
    return new Promise((resolve, reject) => {
        const job = jobs[jobId];
        if (job) {
            resolve(JSON.parse(JSON.stringify(job))); // Return a copy
        } else {
            reject(new Error('Job not found'));
        }
    });
}
