import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_valid_workflow():
    payload = {
        "name": "Test Workflow",
        "description": "A valid workflow",
        "steps": [
            {"action": "clean", "params": {}},
            {"action": "summarize", "params": {}}
        ]
    }
    response = client.post("/workflows", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert len(data["steps"]) == 2

def test_create_invalid_workflow():
    payload = {
        "name": "Invalid Workflow",
        "description": "Contains consecutive duplicates",
        "steps": [
            {"action": "clean", "params": {}},
            {"action": "clean", "params": {}}
        ]
    }
    response = client.post("/workflows", json=payload)
    assert response.status_code == 422

def test_create_workflow_invalid_action():
    payload = {
        "name": "Invalid Action Workflow",
        "description": "Contains invalid action type",
        "steps": [
            {"action": "dance", "params": {}},  # 'dance' is not a valid action
            {"action": "clean", "params": {}}
        ]
    }
    response = client.post("/workflows", json=payload)
    assert response.status_code == 422
