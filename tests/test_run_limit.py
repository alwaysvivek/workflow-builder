import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_run_limit():
    print("--- Testing Workflow Run Limit (Max 5) ---")

    # 1. Create a Workflow
    wf_payload = {
        "name": "Limit Test Workflow",
        "steps": [{"action": "clean"}] 
    }
    response = client.post("/workflows", json=wf_payload)
    assert response.status_code == 200
    workflow_id = response.json()["id"]

    # 2. Run it 7 times
    # Note: Using a loop with TestClient is synchronous and fast
    for i in range(7):
        run_payload = {"input_text": f"Test run {i+1}"}
        resp = client.post(f"/workflows/{workflow_id}/run", json=run_payload)
        # Note: If run is successful, it returns 200. 
        # If queue is full or other logic, handle asserting that.
        # Assuming run is successful:
        assert resp.status_code == 200

    # 3. Check /runs endpoint
    resp = client.get("/runs")
    assert resp.status_code == 200
    runs = resp.json()
    count = len(runs)
    
    # Assert limit
    assert count <= 5
    if len(runs) > 0:
        # Latest should be first
        assert runs[0]["input_text"] == "Test run 7"
