import pytest
import subprocess
import time
import requests
import os

@pytest.fixture(scope="session")
def docker_compose_environment(request):
    """
    A session-scoped fixture to manage the lifecycle of the Docker Compose stack.
    It brings the stack up before the test session and tears it down afterward.
    """
    compose_file = os.path.join(os.path.dirname(__file__), '..', 'docker-compose.yml')
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'stems')
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nBringing up Docker Compose stack...")
    try:
        # Use a detached process to allow the test runner to continue
        compose_up_result = subprocess.run(
            f"docker-compose -f {compose_file} up --build -d",
            shell=True, check=True, capture_output=True, text=True
        )
        print(compose_up_result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during docker-compose up:")
        print(e.stdout)
        print(e.stderr)
        pytest.fail("docker-compose up failed", pytrace=False)

    # Health check: wait for the orchestrator to be responsive
    orchestrator_url = "http://127.0.0.1:8000/"
    retries = 20
    for i in range(retries):
        try:
            response = requests.get(orchestrator_url, timeout=5)
            if response.status_code == 200 and "Job Orchestrator" in response.text:
                print("Orchestrator service is up.")
                break
        except requests.ConnectionError:
            time.sleep(3)
    else:
        pytest.fail("Orchestrator service did not become healthy in time.", pytrace=False)

    # Yield control to the tests
    yield orchestrator_url

    # Teardown: bring the stack down after tests are done
    print("\nTearing down Docker Compose stack...")
    subprocess.run(
        f"docker-compose -f {compose_file} down -v",
        shell=True, check=True
    )
    # Clean up created files
    for item in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, item))
