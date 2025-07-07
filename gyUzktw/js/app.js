const { useState, useEffect, useCallback, useRef } = React;

const API_BASE_URL = 'http://localhost:8000'; 

const api = {
    createTrack: async (prompt, reference_track_url) => {
        const body = { prompt };
        if (reference_track_url) {
            body.reference_track_url = reference_track_url;
        }

        const response = await fetch(`${API_BASE_URL}/create-track`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create track');
        }
        return response.json();
    },
    getJobStatus: async (jobId) => {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get job status');
        }
        return response.json();
    }
};

const statusConfig = {
    PENDING: { icon: 'clock', color: 'yellow-400', pulse: false },
    QUEUED: { icon: 'clock', color: 'yellow-400', pulse: false },
    PROCESSING: { icon: 'loader-2', color: 'blue-400', pulse: true },
    SUCCESS: { icon: 'check-circle', color: 'green-400', pulse: false },
    COMPLETED: { icon: 'check-circle', color: 'green-400', pulse: false },
    FAILURE: { icon: 'x-circle', color: 'red-400', pulse: false },
    FAILED: { icon: 'x-circle', color: 'red-400', pulse: false },
};

function Icon({ name, className = "w-5 h-5" }) {
    const ref = useRef();
    useEffect(() => {
        if (ref.current) {
            lucide.createIcons({
                nodes: [ref.current],
            });
        }
    }, [name]);
    return <i data-lucide={name} ref={ref} className={className}></i>;
}

function StemLinks({ stems }) {
    if (!stems) return null;
    return (
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
            {Object.entries(stems).map(([name, url]) => (
                <a key={name} href={url} download className="flex items-center gap-2 text-sm text-gray-400 hover:text-accent transition-colors">
                    <Icon name="music-2" className="w-4 h-4" />
                    <span className="capitalize">{name}</span>
                </a>
            ))}
        </div>
    );
}

function JobCard({ initialJob, onUpdate }) {
    const [job, setJob] = useState(initialJob);
    const pollingRef = useRef();

    const poll = useCallback(async () => {
        if (job.status === 'SUCCESS' || job.status === 'COMPLETED' || job.status === 'FAILURE' || job.status === 'FAILED') {
            clearInterval(pollingRef.current);
            return;
        }
        try {
            const updatedJob = await api.getJobStatus(job.job_id);
            setJob(updatedJob);
            onUpdate(updatedJob);
        } catch (error) {
            console.error(`Error polling for job ${job.job_id}:`, error);
            const failedJob = { ...job, status: 'FAILURE', result: { ...job.result, error: 'Polling failed' } };
            setJob(failedJob);
            onUpdate(failedJob);
            clearInterval(pollingRef.current);
        }
    }, [job.job_id, job.status, onUpdate]);

    useEffect(() => {
        pollingRef.current = setInterval(poll, 3000);
        return () => clearInterval(pollingRef.current);
    }, [poll]);

    const { status, prompt, result } = job;
    const config = statusConfig[status.toUpperCase()] || statusConfig['PENDING'];
    const progress = result?.progress ?? (result?.step ? 5 : 0) ?? 0;
    const step = result?.step || result?.details || 'Queued';

    const isFinished = status === 'SUCCESS' || status === 'COMPLETED' || status === 'FAILURE' || status === 'FAILED';
    const isSuccess = status === 'SUCCESS' || status === 'COMPLETED';

    const borderColorClass = `border-${config.color}/30`;
    const pulseClass = config.pulse ? 'animate-pulse-slow' : '';

    return (
        <div className={`job-card bg-gray-800/50 border ${borderColorClass} ${pulseClass} rounded-lg p-5 flex flex-col gap-4`}>
            <div className="flex justify-between items-start gap-4">
                <p className="font-medium text-gray-300 flex-1 break-words">"{prompt}"</p>
                <div className={`flex items-center gap-2 text-sm font-semibold text-${config.color}`}>
                    <Icon name={config.icon} className={`w-5 h-5 ${config.pulse ? 'animate-spin' : ''}`} />
                    <span>{status}</span>
                </div>
            </div>

            {!isFinished && (
                <div className="progress-section">
                    <div className="flex justify-between items-center mb-1 text-sm text-gray-400">
                        <span className="step-label">{step}</span>
                        <span className="progress-label">{progress}%</span>
                    </div>
                    <div className="progress-bar-container w-full bg-gray-700">
                        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                    </div>
                </div>
            )}

            {isFinished && (
                <div className="mt-2 pt-4 border-t border-gray-700">
                    {isSuccess ? (
                        <>
                            <h4 className="text-md font-semibold mb-3 text-white">Downloads</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <a href={result.final_track_url} download className="block bg-accent hover:bg-accent-hover text-white font-bold py-2 px-4 rounded-md transition w-full text-center">
                                        <div className="flex items-center justify-center gap-2">
                                            <Icon name="download" className="w-4 h-4" /> Final Mix (.wav)
                                        </div>
                                    </a>
                                </div>
                                <div className="flex flex-col gap-2">
                                    <p className="text-sm font-semibold text-gray-300">Stems:</p>
                                    <StemLinks stems={result.stems} />
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="text-red-400 bg-red-500/10 p-3 rounded-md">
                            <p className="font-semibold flex items-center gap-2"><Icon name="alert-triangle" className="w-4 h-4" />Error:</p>
                            <p className="text-sm">{result?.error || 'An unknown error occurred.'}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function JobDashboard({ jobs, onUpdate }) {
    if (jobs.length === 0) {
        return (
            <div id="empty-queue-message" className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                <Icon name="inbox" className="w-16 h-16 mb-4" />
                <p className="text-lg">Your generated tracks will appear here.</p>
                <p>Get started by entering a prompt above.</p>
            </div>
        );
    }
    return (
        <div className="flex flex-col gap-4">
            {jobs.map(job => (
                <JobCard key={job.job_id} initialJob={job} onUpdate={onUpdate} />
            ))}
        </div>
    );
}

function PromptForm({ onJobCreate, isSubmitting, setIsSubmitting }) {
    const [prompt, setPrompt] = useState('');
    const [referenceUrl, setReferenceUrl] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!prompt.trim() || isSubmitting) return;

        setIsSubmitting(true);
        try {
            const { job_id } = await api.createTrack(prompt.trim(), referenceUrl.trim());
            const initialJobState = await api.getJobStatus(job_id);
            onJobCreate(initialJobState);
            setPrompt('');
            setReferenceUrl('');
        } catch (error) {
            console.error('Failed to create track:', error);
            alert(`Error: ${error.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <section id="prompt-section" className="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg">
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
                <div>
                    <label htmlFor="prompt-input" className="block text-lg font-semibold mb-2 text-white">
                        <Icon name="music-4" className="inline-block w-5 h-5 mr-2 -mt-1" /> Your Prompt
                    </label>
                    <textarea id="prompt-input" rows="4" value={prompt} onChange={(e) => setPrompt(e.target.value)} className="w-full bg-gray-900 border border-gray-600 rounded-lg p-4 focus:ring-2 ring-accent focus:outline-none transition duration-200 placeholder-gray-500" placeholder="e.g., A funky disco track with a powerful bassline, 125 bpm, in the style of Daft Punk..."></textarea>
                </div>
                <div>
                    <label htmlFor="reference-url-input" className="block text-sm font-medium mb-2 text-gray-300">
                        <Icon name="link" className="inline-block w-4 h-4 mr-2 -mt-1" /> Reference Track URL (Optional)
                    </label>
                    <input type="url" id="reference-url-input" value={referenceUrl} onChange={(e) => setReferenceUrl(e.target.value)} className="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 focus:ring-2 ring-accent focus:outline-none transition duration-200 placeholder-gray-500" placeholder="http://.../reference.wav" />
                </div>
                <button type="submit" disabled={isSubmitting || !prompt.trim()} className="w-full md:w-auto md:self-end bg-accent hover:bg-accent-hover text-white font-bold py-3 px-8 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100">
                    {isSubmitting ? (
                        <>
                            <Icon name="loader-2" className="w-5 h-5 animate-spin" />
                            <span>Generating...</span>
                        </>
                    ) : (
                        <>
                            <Icon name="play" className="w-5 h-5" />
                            <span>Generate</span>
                        </>
                    )}
                </button>
            </form>
        </section>
    );
}

function App() {
    const [jobs, setJobs] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        lucide.createIcons();
    }, []);

    const handleJobCreate = (newJob) => {
        setJobs(prevJobs => [newJob, ...prevJobs]);
    };

    const handleJobUpdate = useCallback((updatedJob) => {
        setJobs(prevJobs => prevJobs.map(j => j.job_id === updatedJob.job_id ? updatedJob : j));
    }, []);

    return (
        <div className="min-h-screen container mx-auto p-4 md:p-8 flex flex-col gap-8">
            <header className="text-center">
                <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">AI Music Production Assistant</h1>
                <p className="text-lg text-gray-400 mt-2">Craft your sound with the power of AI</p>
            </header>

            <main className="flex-grow flex flex-col gap-8">
                <PromptForm onJobCreate={handleJobCreate} isSubmitting={isSubmitting} setIsSubmitting={setIsSubmitting} />
                <section id="jobs-section" className="flex-grow flex flex-col bg-gray-800/50 border border-gray-700/50 rounded-xl p-6 shadow-lg backdrop-blur-sm">
                    <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-3">
                        <Icon name="list-music" className="w-7 h-7" />
                        Generation Queue
                    </h2>
                    <div id="job-list-container" className="flex-grow overflow-y-auto pr-2">
                        <JobDashboard jobs={jobs} onUpdate={handleJobUpdate} />
                    </div>
                </section>
            </main>

            <footer className="text-center text-gray-500 text-sm py-4">
                <p>Powered by Neo's Design & Engineering | &copy; 2025</p>
            </footer>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
