import argparse
import os
import sys
import time
import requests

# --- Configuration ---
# The URL for the Job Orchestrator Service.
# It can be overridden by setting the ORCHESTRATOR_URL environment variable.
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:8000")

# --- Helper Functions ---

def print_status(message, a_color_code):
    """Prints a colored status message to the console."""
    print(f"\033[{a_color_code}m[*] {message}\033[0m")

def print_error(message):
    """Prints an error message to the console and exits."""
    print(f"\033[91m[!] ERROR: {message}\033[0m", file=sys.stderr)
    sys.exit(1)

def print_success(message):
    """Prints a success message to the console."""
    print(f"\033[92m[+] SUCCESS: {message}\033[0m")

def create_job(prompt: str):
    """
    Sends a request to the orchestrator to create a new music generation job.
    """
    create_url = f"{ORCHESTRATOR_URL}/create-track"
    payload = {"prompt": prompt}
    
    print_status(f"Submitting job to {create_url}...", "94") # Blue
    
    try:
        response = requests.post(create_url, json=payload, timeout=10)
        response.raise_for_status()
        
        job_data = response.json()
        job_id = job_data.get("job_id")
        
        if not job_id:
            print_error("API did not return a job_id.")
            
        print_success(f"Job created successfully. Job ID: {job_id}")
        return job_id
        
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to the orchestrator service: {e}")
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")

def poll_job_status(job_id: str):
    """
    Periodically polls the job status endpoint until the job is completed or fails.
    """
    status_url = f"{ORCHESTRATOR_URL}/jobs/{job_id}"
    last_status = None
    
    print_status(f"Polling job status at {status_url}", "94") # Blue

    while True:
        try:
            response = requests.get(status_url, timeout=10)
            
            if response.status_code == 404:
                print_error(f"Job with ID '{job_id}' not found.")
            
            response.raise_for_status()
            
            status_data = response.json()
            current_status = status_data.get("status")
            result = status_data.get("result")

            if current_status != last_status:
                print_status(f"Job status changed to: {current_status}", "93") # Yellow
                last_status = current_status

            if current_status == "SUCCESS":
                print_success("Job completed!")
                if result and result.get("final_track_url"):
                    print(f"  -> Final Track Location: {result['final_track_url']}")
                else:
                    print("  -> No output URL provided in the result.")
                break
                
            elif current_status == "FAILURE":
                error_message = "No specific error details provided."
                if result and result.get("error"):
                    error_message = result["error"]
                print_error(f"Job failed. Reason: {error_message}")
                break

            # Wait before the next poll
            time.sleep(5)

        except requests.exceptions.RequestException as e:
            print_error(f"Failed to poll job status: {e}")
        except Exception as e:
            print_error(f"An unexpected error occurred during polling: {e}")


def main():
    """
    Main function to parse arguments and orchestrate the CLI commands.
    """
    parser = argparse.ArgumentParser(
        description="CLI client for the AI Music Production Assistant."
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # --- Create command ---
    create_parser = subparsers.add_parser(
        "create", 
        help="Create a new music track from a prompt."
    )
    create_parser.add_argument(
        "--prompt", 
        type=str, 
        required=True, 
        help="A natural language prompt describing the music to generate."
    )

    args = parser.parse_args()

    if args.command == "create":
        job_id = create_job(args.prompt)
        if job_id:
            poll_job_status(job_id)

if __name__ == "__main__":
    main()
