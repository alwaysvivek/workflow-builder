import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

def create_test_workflow():
    payload = {
        "name": "Chained Workflow",
        "description": "Testing the chain of 3 steps",
        "steps": [
            {"action": "clean", "params": {}},
            {"action": "summarize", "params": {}},
            {"action": "keypoints", "params": {}}
        ]
    }
    response = requests.post(f"{BASE_URL}/workflows", json=payload)
    if response.status_code == 200:
        workflow = response.json()
        print(f"✅ Created workflow: {workflow['id']}")
        return workflow['id']
    else:
        print(f"❌ Failed to create workflow: {response.text}")
        return None

def run_workflow(workflow_id, input_text):
    print(f"\n--- Running Workflow {workflow_id} ---")
    print(f"Input: '{input_text}'")
    
    payload = {"input_text": input_text}
    response = requests.post(f"{BASE_URL}/workflows/{workflow_id}/run", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Workflow run successful!")
        print(f"Run ID: {result['id']}")
        
        print("\n--- Execution Steps ---")
        for step in result['step_runs']:
            print(f"Step {step['step_order']} ({step['step_type']}):")
            print(f"  Output: {step['output_text']}")
            
        return result
    else:
        print(f"❌ Workflow run failed: {response.text}")
        return None

if __name__ == "__main__":
    try:
        # Check health
        requests.get(f"{BASE_URL}/health")
        
        workflow_id = create_test_workflow()
        if workflow_id:
            input_text = "This is some messy input text that needs cleaning and summarizing."
            run_workflow(workflow_id, input_text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure it is running.")
