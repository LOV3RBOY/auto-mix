import pytest
import requests
import time
import os

def test_successful_end_to_end_run(docker_compose_environment):
    """
    Tests a full, successful job run from submission to file creation.
    
    Args:
        docker_compose_environment: The fixture that provides the running stack's URL.
    """
    orchestrator_url = docker_compose_environment
    prompt = "A successful test run generating a chill synthwave track at 100 bpm."
    
    # 1. Submit the job
    create_url = f"{orchestrator_url}/create-track"
    response = requests.post(create_url, json={"prompt": prompt})
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert job_id is not None

    # 2. Poll for status until completion
    status_url = f"{orchestrator_url}/jobs/{job_id}"
    timeout = 120  # 2 minutes timeout
    start_time = time.time()
    final_status = None
    final_result = None

    while time.time() - start_time < timeout:
        time.sleep(5)
        poll_response = requests.get(status_url)
        if poll_response.status_code == 200:
            data = poll_response.json()
            current_status = data.get("status")
            print(f"Job {job_id} status: {current_status}")
            if current_status in ["SUCCESS", "FAILURE"]:
                final_status = current_status
                final_result = data.get("result")
                break
    
    # 3. Assert the final status and result
    assert final_status == "SUCCESS", f"Job failed with status {final_status} and result {final_result}"
    assert final_result is not None
    assert "final_track_url" in final_result
    
    output_path = final_result["final_track_url"]
    
    # 4. Verify the output file was created in the shared volume
    # The docker-compose maps the container's /stems to ./output/stems on the host
    host_path = os.path.join(
        os.path.dirname(__file__), '..', 'output', os.path.basename(output_path)
    )
    
    assert os.path.exists(host_path), f"Output file not found at {host_path}"
    assert os.path.getsize(host_path) > 0 # Check that the file is not empty
