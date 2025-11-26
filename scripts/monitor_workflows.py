import json
import subprocess
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(REPO_DIR, "workflow_history.jsonl")
POLL_INTERVAL_SECONDS = 60  # Check every minute

def run_gh_command(args: List[str]) -> Any:
    """Run a GitHub CLI command and return the JSON output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from gh command: {result.stdout}")
        return None

def run_gh_command_text(args: List[str]) -> Optional[str]:
    """Run a GitHub CLI command and return the plain text output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout if result.stdout.strip() else None
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"Stderr: {e.stderr}")
        return None

def load_history() -> Dict[str, Any]:
    """Load existing history to avoid duplicates."""
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    history[str(record["databaseId"])] = record
                except json.JSONDecodeError:
                    continue
    return history

def append_to_history(record: Dict[str, Any]):
    """Append a new record to the history file."""
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

def get_failure_details(run_id: str, repo_full_name: str) -> str:
    """Fetch failure annotations for a specific run."""
    # First, try to get the log for failed steps
    print(f"    Fetching logs for run {run_id} from {repo_full_name}...")
    log_output = run_gh_command_text(["run", "view", run_id, "--repo", repo_full_name, "--log-failed"])
    
    if log_output:
        # Look for lines starting with ##[error]
        errors = []
        for line in log_output.splitlines():
            if "##[error]" in line:
                # Clean up the error message
                msg = line.split("##[error]")[1].strip()
                errors.append(msg)
        
        if errors:
            return "; ".join(errors)

    # Fallback to 'gh run view --json jobs' if log fetching fails or finds no explicit errors
    data = run_gh_command(["run", "view", run_id, "--repo", repo_full_name, "--json", "jobs"])
    if not data:
        return "Could not fetch failure details."
    
    failure_messages = []
    for job in data.get("jobs", []):
        if job.get("conclusion") == "failure":
            job_name = job.get("name", "Unknown Job")
            steps = job.get("steps", [])
            failed_steps = [s for s in steps if s.get("conclusion") == "failure"]
            for step in failed_steps:
                step_name = step.get("name", "Unknown Step")
                failure_messages.append(f"Job '{job_name}' failed at step '{step_name}'")
    
    if not failure_messages:
        return "Failed (No specific step failure found in summary)"
    return "; ".join(failure_messages)

def monitor_workflows():
    """Main monitoring loop."""
    print(f"Starting workflow monitor. Polling every {POLL_INTERVAL_SECONDS} seconds...")
    print(f"Saving history to: {HISTORY_FILE}")
    
    known_runs = load_history()
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for updates...")
            
            # Fetch recent runs
            runs = run_gh_command([
                "run", "list", 
                "--limit", "10", 
                "--json", "databaseId,status,conclusion,headBranch,headSha,workflowName,createdAt,url"
            ])
            
            if runs:
                for run in runs:
                    run_id = str(run["databaseId"])
                    status = run["status"]
                    conclusion = run["conclusion"]
                    
                    # We only care about completed runs that we haven't fully processed yet
                    # Or runs that were previously 'in_progress' and are now done
                    
                    is_new = run_id not in known_runs
                    is_update = (run_id in known_runs and 
                                 known_runs[run_id]["status"] != "completed" and 
                                 status == "completed")
                    
                    if is_new or is_update:
                        # If it's completed and failed, get more details
                        failure_msg = ""
                        if status == "completed" and conclusion == "failure":
                            print(f"  -> Run {run_id} ({run['workflowName']}) failed. Fetching details...")
                            # Extract repo from URL (e.g., https://github.com/owner/repo/actions/runs/...)
                            try:
                                repo_part = run['url'].split("github.com/")[1].split("/actions")[0]
                            except IndexError:
                                repo_part = "robandrewford/agentic-parallelism" # Fallback
                            
                            failure_msg = get_failure_details(run_id, repo_part)
                        
                        # Create record
                        record = {
                            "databaseId": run["databaseId"],
                            "workflowName": run["workflowName"],
                            "headBranch": run["headBranch"],
                            "headSha": run["headSha"],
                            "status": status,
                            "conclusion": conclusion,
                            "createdAt": run["createdAt"],
                            "url": run["url"],
                            "failureMessage": failure_msg,
                            "capturedAt": datetime.now().isoformat()
                        }
                        
                        # Update local state
                        known_runs[run_id] = record
                        append_to_history(record)
                        
                        # Notify
                        icon = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⏳"
                        print(f"{icon} Run {run_id}: {run['workflowName']} ({run['headBranch']}) - {status} / {conclusion}")
                        if failure_msg:
                            print(f"    Error: {failure_msg}")

            time.sleep(POLL_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\nStopping monitor.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    monitor_workflows()
