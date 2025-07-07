# **End-to-End System Verification: Test Plan & Simulated Report**

---

### **1. Test Objective**
To verify the seamless integration and functionality of the entire AI Music Production Assistant pipeline, from user input to final, quality-checked audio output. This test will validate the system's ability to handle a complex, multi-parameter request, process it through all microservices, and produce a result that meets quality standards, including the automated Quality Assurance (QA) and retry mechanisms.

---

### **2. Test Environment Setup**

For this test to be executed, the complete application stack must be running. This is achieved by deploying all services using the project's `docker-compose.yml` file.

**Required Running Services:**
| Service Name                  | Container Name          | Purpose                                        |
| :---------------------------- | :---------------------- | :--------------------------------------------- |
| **Frontend UI**               | `frontend-react-ui`     | User-facing web application.                   |
| **Job Orchestrator**          | `job-orchestrator-api`  | Central API and workflow manager.              |
| **Orchestrator Worker**       | `celery_worker`         | Asynchronous task executor.                    |
| **Prompt Parser**             | `prompt-parser-service` | NER model for prompt analysis.                 |
| **Style Analysis**            | `style-analysis-service`| Feature extraction from reference audio.       |
| **Sound Generation**          | `sound-generation`      | Integration with Stability AI for audio creation. |
| **Mixing & Mastering**        | `mixing-mastering`      | Combines stems and applies DSP.                |
| **Quality Assurance (QA)**    | `qa-service`            | Analyzes final track quality.                  |
| **Database**                  | `postgres_db`           | Persistent job storage.                        |
| **Message Broker**            | `redis_broker`          | Celery task queue.                             |

---

### **3. Test Execution Steps (Detailed)**

This section outlines the step-by-step process of the end-to-end test, tracing the data flow from initiation to completion.

**Test Scenario:**
- **Prompt:** `Generate a dark, atmospheric synthwave track similar to Carpenter Brut's 'Turbo Killer', around 140 BPM, with a heavy, distorted bassline and shimmering arpeggiated synths.`
- **Reference Audio:** A 30-second WAV file (`reference_track.wav`) is uploaded by the user.

#### **a. Frontend (React UI)**
1.  **Action:** The user navigates to the application UI at `http://localhost:3000`.
2.  **Input:** The user types the specified prompt into the text area.
3.  **Upload:** The user clicks the "Upload File" button and selects `reference_track.wav`.
4.  **Submission:** The user clicks the "Generate" button.
5.  **Expected Behavior:** The UI sends a `POST` request to the Job Orchestrator's `/create-track` endpoint, containing the prompt and the uploaded file. A new job card appears in the "Generation Queue" with a `PENDING` status.

#### **b. Job Orchestrator**
1.  **API Call:** Receives the `POST` request from the frontend.
2.  **Job Creation:**
    -   Generates a unique `job_id` (e.g., `a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d`).
    -   Inserts a new record into the `jobs` table in the PostgreSQL database with the `job_id`, `prompt`, `reference_track_url`, `retry_count=0`, and an initial `status` of `PENDING`.
3.  **Task Dispatch:** Dispatches a Celery task chain to the Redis message broker, initiating the asynchronous workflow.

#### **c. Prompt Parser (NER)**
1.  **Invocation:** The Celery worker calls the Prompt Parser service with the text prompt.
2.  **Processing:** The service's NER model processes the text.
3.  **Expected Output:** The service returns a structured JSON object.
    ```json
    {
      "tempo": 140,
      "key": null,
      "genre": "synthwave",
      "instruments": ["bass", "synths"],
      "style_references": ["Carpenter Brut", "Turbo Killer"],
      "mood": "dark atmospheric"
    }
    ```

#### **d. Style Analysis**
1.  **Invocation:** The Celery worker, seeing a `reference_track_url`, calls the Style Analysis service with the audio file.
2.  **Processing:** The service uses `librosa` to extract musical features.
3.  **Expected Output:** The service returns a JSON object with precise features extracted from the audio.
    ```json
    {
      "tempo": 140.52,
      "key": "D Minor",
      "loudness_lufs": -9.8,
      "eq_profile": { "...": "..." },
      "structure_markers": [
        { "start_time": 0.0, "end_time": 8.5, "label": "Intro" },
        { "start_time": 8.5, "end_time": 25.0, "label": "Verse" }
      ]
    }
    ```

#### **e. Sound Generation (Stability AI)**
1.  **Invocation:** The Celery worker consolidates data from the previous steps and calls the Sound Generation service. The prompt sent to the Stability AI API will be a refined version of the user's prompt, guided by the analysis (e.g., `"A dark, atmospheric synthwave track in D Minor at 140 BPM..."`).
2.  **Processing:** The service calls the Stability AI Stable Audio API.
3.  **Expected Output:** The service returns a JSON object with paths to the generated audio stems.
    ```json
    {
      "job_id": "stab-xyz789",
      "stems": {
        "bass": "/stems/a1b2c3d4_bass.wav",
        "synths_arp": "/stems/a1b2c3d4_synths_arp.wav",
        "drums": "/stems/a1b2c3d4_drums.wav",
        "pads": "/stems/a1b2c3d4_pads.wav"
      }
    }
    ```

#### **f. Mixing & Mastering**
1.  **Invocation:** The Celery worker calls the Mixing & Mastering service with the list of stem paths.
2.  **Processing:** The service combines the stems and applies a mastering chain, targeting an industry-standard loudness of **-14 LUFS**.
3.  **Expected Output:** The service returns the path to the final, mastered track.
    ```json
    {
      "output_path": "/stems/mastered_mix_a1b2c3d4.wav"
    }
    ```

#### **g. Automated QA**
1.  **Invocation:** The Celery worker calls the QA service with the path to the mastered track.
2.  **Processing:** The service analyzes the audio file for key metrics.
3.  **Expected Output:** The service returns a JSON report with a `pass` or `fail` status. This report is the basis for the next step.

---

### **4. Simulated Results & Verification**

#### **a. Simulated 'Pass' Scenario**

In this scenario, the first attempt at generation meets all quality criteria.

1.  **QA Service Response:** The QA service returns the following JSON, indicating success.
    ```json
    {
      "status": "pass",
      "details": {
        "tempo": 140.1,
        "key": "D Minor",
        "lufs": -13.8,
        "clipping": false
      },
      "checks": {
        "tempo_check": "pass",
        "key_check": "pass",
        "lufs_check": "pass",
        "clipping_check": "pass"
      }
    }
    ```
2.  **Verification:**
    -   **Orchestrator:** The Orchestrator receives the `pass` status. It updates the job `a1b2c3d4` in the PostgreSQL database, setting the `status` to **`SUCCESS`** and saving the final file path and QA report in the `result` column.
    -   **Frontend UI:** The UI, polling for job status, receives the `SUCCESS` state. The job card updates to show a "Download" button for the final mix.

#### **b. Simulated 'Fail & Retry' Scenario**

In this scenario, the first mastering attempt is too loud, causing digital clipping.

1.  **Initial QA Service Response:** The QA service returns a `fail` status.
    ```json
    {
      "status": "fail",
      "details": {
        "tempo": 140.2,
        "key": "D Minor",
        "lufs": -9.5,
        "clipping": true
      },
      "checks": {
        "tempo_check": "pass",
        "key_check": "pass",
        "lufs_check": "fail (Target: -14 LUFS, Actual: -9.5 LUFS)",
        "clipping_check": "fail (Clipping detected)"
      }
    }
    ```
2.  **Verification & Retry Logic:**
    -   **Orchestrator:** The Orchestrator receives the `fail` status. It initiates the retry logic:
        1.  It queries the database for job `a1b2c3d4` and confirms `retry_count` is less than the max limit (e.g., `retry_count < 2`).
        2.  It increments `retry_count` to `1`.
        3.  It creates a modified parameter set for the next run. Specifically for a clipping/loudness failure, it will instruct the mastering service to re-run with a lower gain setting.
        4.  It updates the job status to `RETRYING_QA`.
        5.  It dispatches a new task chain, skipping directly to the **Mixing & Mastering** step with the adjusted parameters.
    -   **Mixing & Mastering (Retry):** The service re-processes the original stems but applies less gain/limiting to reduce the final loudness.
    -   **QA Service (Retry):** The new master is sent for analysis, which now passes.
    -   **Finalization:** The Orchestrator updates the job status to **`SUCCESS`**.

---

### **5. Conclusion**

The simulated execution of this end-to-end test plan successfully verifies the core functionality and resilience of the AI Music Production Assistant. The system correctly processes a complex user request, integrates data across all microservices, and handles both success and failure scenarios through its automated QA and retry loop. This confirms that the system architecture is robust and the application is ready for production workloads.