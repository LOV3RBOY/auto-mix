document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const parseButton = document.getElementById('parse-button');
    const buttonText = document.getElementById('button-text');
    const buttonSpinner = document.getElementById('button-spinner');
    
    const resultContainer = document.getElementById('result-container');
    const jsonOutput = document.getElementById('json-output');
    
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    const API_URL = '/api/v1/parse';

    const samplePrompt = "A high-energy drum and bass track at 174 bpm in the style of Pendulum, with a heavy reese bass and in F# minor.";
    promptInput.value = samplePrompt;

    const toggleLoading = (isLoading) => {
        if (isLoading) {
            parseButton.disabled = true;
            buttonText.classList.add('hidden');
            buttonSpinner.classList.remove('hidden');
        } else {
            parseButton.disabled = false;
            buttonText.classList.remove('hidden');
            buttonSpinner.classList.add('hidden');
        }
    };
    
    const displayError = (message) => {
        errorMessage.textContent = message;
        errorContainer.classList.remove('hidden');
        resultContainer.classList.add('hidden');
    };
    
    const hideError = () => {
        errorContainer.classList.add('hidden');
    };

    const parsePrompt = async () => {
        const prompt = promptInput.value;
        if (!prompt.trim()) {
            displayError("Prompt cannot be empty.");
            return;
        }

        toggleLoading(true);
        hideError();
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt }),
            });

            const data = await response.json();

            if (!response.ok) {
                const errorDetail = data.detail || `Request failed with status ${response.status}`;
                throw new Error(errorDetail);
            }

            jsonOutput.textContent = JSON.stringify(data, null, 2);
            resultContainer.classList.remove('hidden');

        } catch (error) {
            console.error('Error parsing prompt:', error);
            const message = error.message.includes('Failed to fetch') 
                ? 'Could not connect to the parser service. Is it running?'
                : error.message;
            displayError(message);
        } finally {
            toggleLoading(false);
        }
    };

    parseButton.addEventListener('click', parsePrompt);
    promptInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            parsePrompt();
        }
    });
});
