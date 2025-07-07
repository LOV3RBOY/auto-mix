# AI Music Production Assistant - Quick Start Guide

This guide provides the necessary steps to build and run all the microservices for the AI Music Production Assistant using Docker Compose.

---

### 1. The `run.sh` Startup Script

This shell script automates the process of building the Docker images for each service and launching the entire application stack in the background.

```sh
#!/bin/bash

# AI Music Production Assistant - Startup Script
# This script builds and starts all necessary services.

# Exit immediately if a command exits with a non-zero status.
set -e

# Inform the user that the process is starting.
echo "[INFO] Building Docker images and starting services..."

# Build the Docker images from the Dockerfiles for each service.
# The '&&' ensures that 'docker-compose up' only runs if the build is successful.
# 'docker-compose up -d' starts all services defined in docker-compose.yml in detached mode.
docker-compose build && docker-compose up -d

# Inform the user that the process is complete.
echo "[SUCCESS] All services have been started. Use 'docker-compose ps' to verify."

```

---

### 2. Execution Steps

Follow these steps in your terminal from the root directory of the project to get the system running.

1.  **Save the Script**
    Create the `run.sh` file using the following command:
    ```sh
    cat << 'EOF' > run.sh
    #!/bin/bash
    
    # AI Music Production Assistant - Startup Script
    # This script builds and starts all necessary services.
    
    set -e
    
    echo "[INFO] Building Docker images and starting services..."
    
    docker-compose build && docker-compose up -d
    
    echo "[SUCCESS] All services have been started. Use 'docker-compose ps' to verify."
    EOF
    ```

2.  **Make the Script Executable**
    ```sh
    chmod +x run.sh
    ```

3.  **Run the Script**
    ```sh
    ./run.sh
    ```

4.  **Verify Services are Running**
    After a minute, check the status of all containers. They should all show a `State` of `Up`.
    ```sh
    docker-compose ps
    ```
    *Expected Output (names and ports may vary slightly):*
    ```
              Name                             Command               State           Ports
    ------------------------------------------------------------------------------------------------
    job-orchestrator-service        uvicorn main:app --host 0. ...   Up      0.0.0.0:8000->8000/tcp
    mixing-mastering-service        uvicorn main:app --host 0. ...   Up      8000/tcp
    orchestrator-worker             celery -A main.celery_app  ...   Up
    prompt-parser-service           uvicorn app.main:app --hos ...   Up      8000/tcp
    redis                           redis-server /usr/local/et ...   Up      0.0.0.0:6379->6379/tcp
    sound-generation-service        uvicorn main:app --host 0. ...   Up      8000/tcp
    style-analysis-service          uvicorn main:app --host 0. ...   Up      8000/tcp
    ```

---

### 3. Testing the System

You can submit a music generation job using the provided Python command-line client.

1.  **Install Client Dependencies**
    First, ensure you have the necessary Python package installed.
    ```sh
    pip install -r cli-client/requirements.txt
    ```

2.  **Submit a Job**
    Run the client with the `create` command and provide a descriptive prompt. The client will show the job's progress in real-time.

    **Example 1: Skrillex-style track**
    ```sh
    python cli-client/client.py create --prompt "Make a track in the style of Skrillex’s ‘Inhale Exhale.’"
    ```

    **Example 2: House beat with dubstep elements**
    ```sh
    python cli-client/client.py create --prompt "Generate a four-on-the-floor house beat with dubstep-style bass."
    ```

---

### 4. Accessing the Output

The `docker-compose.yml` file is configured to map the container's output directory to a local folder on your machine.

-   **Location**: All final, mastered audio files (`.wav`) will be saved in the `output/stems/` directory within your project folder.

---

### 5. Stopping the System

When you are finished, you can stop all running services and remove the containers with a single command.

```sh
docker-compose down
```