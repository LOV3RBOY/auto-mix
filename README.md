AI Music Production Assistant
Overview
Welcome to the AI Music Production Assistant, a full-stack application designed to generate complete music tracks from natural language prompts. This project leverages a robust microservice architecture to handle distinct stages of the music creation process, from prompt analysis and sound generation to automated quality assurance and final mastering. The entire system is orchestrated with Docker Compose, making it portable, scalable, and easy to deploy.

Services
The application is composed of several containerized services that work together to fulfill a user request. These are all managed by the root docker-compose.yml file.

Service NameContainer NameExposed PortDescription
frontend-reactreact_ui3000The React web interface for user interaction.
job-orchestratororchestrator_api8000The central API that manages the music generation workflow.
workercelery_worker(internal)A Celery worker that executes the asynchronous task pipeline.
prompt-parserprompt_parser_api8001Parses natural language prompts into structured data.
style-analysisstyle_analysis_api8002Analyzes reference audio to extract musical features.
sound-generationsound_generation_api8003Generates audio by calling the Stability AI API.
mixing-masteringmixing_mastering_api8004Mixes audio stems into a final track.
qa-serviceqa_service_api8006Performs automated quality analysis on the final track.
postgrespostgres_db5432Persistent database for storing job information and state.
redisredis_broker6379Message broker and results backend for Celery tasks.
Prerequisites
To run this application, you must have the following software installed on your machine:

Docker
Docker Compose
Quick Start Instructions
Follow these steps to get the entire system running locally.

1. Set Up the Project Directory
Ensure your project is structured correctly. You should have a root directory containing the docker-compose.yml file, the run.sh script, and a services folder. Inside the services folder, place each microservice's code in its own subdirectory.

/ai-music-production-assistant/
├── docker-compose.yml
├── run.sh
└── services/
    ├── frontend-react/
    │   ├── Dockerfile
    │   └── ...
    ├── job-orchestrator/
    │   ├── Dockerfile
    │   └── ...
    ├── prompt-parser/
    │   ├── Dockerfile
    │   └── ...
    └── ... (and so on for all other services)
2. Configure the Sound Generation API Key
The sound-generation service requires a Stability AI API key to function.

Create a new file named .env inside the services/sound-generation/ directory.

Add your API key to this file:

STABILITY_AI_API_KEY="your_stability_ai_key_here"
Important: The docker-compose.yml file must be configured to pass this environment variable to the sound-generation container. Ensure the service definition includes the env_file directive:

  sound-generation:
    # ... other settings
    env_file:
      - ./services/sound-generation/.env
3. Run the Application
Open your terminal in the root directory of the project.
Make the run.sh script executable:
chmod +x run.sh
Execute the script to build the images and start the services:
./run.sh
The script will first build all Docker images and then launch the containers in the background.
Accessing the Application
Once the script completes, the system is ready to use:

Web Interface: Open your browser and navigate to http://localhost:3000.
API Docs: The Job Orchestrator's FastAPI documentation is available at http://localhost:8000/docs.
Usage
Navigate to the web interface at http://localhost:3000.
Enter a detailed text prompt describing the music you want to create (e.g., "A high-energy drum and bass track at 174 bpm with a heavy reese bass").
Click the Generate button.
A new job card will appear in the "Generation Queue". You can monitor its status in real-time as it moves through the pipeline (Parsing, Generating, Mixing, etc.).
Once the job is SUCCESSFUL, download links for the final mix and individual stems will appear.
Stopping the Application
To stop all running services, execute the following command in the root directory of the project:

docker-compose down
To stop the services and also remove the persistent data volumes (e.g., the PostgreSQL database), use the -v flag:

docker-compose down -v