import requests
import json

base_url = "http://localhost:8000/api"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYTM0OTg5NS1mMGJkLTRjZjctYjlhMy05ZjI5ZTExNjQ5NjUiLCJlbWFpbCI6InRlc3QyQHRlc3QuY29tIiwiZXhwIjoxNzcwNjQ3NjY5fQ.rseypXSuDRYZro2awR-0s9eRB0A97yhWIMfEjNTR4UI"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Create Process
print("Creating Process...")
proc_resp = requests.post(f"{base_url}/processes", headers=headers, json={
    "name": "Python Test Process",
    "description": "Testing from Python",
    "steps": []
})
print(f"Process Response: {proc_resp.status_code}")
print(proc_resp.content.decode())

if proc_resp.status_code == 201:
    proc_id = proc_resp.json()["id"]
    print(f"Process ID: {proc_id}")
    
    # 2. Add Step
    print("Adding Step...")
    step_resp = requests.post(f"{base_url}/processes/{proc_id}/steps", headers=headers, json={
        "name": "First Step",
        "description": "Step Description",
        "quality_criteria": "High Quality",
        "expected_output": "Good Output",
        "estimated_duration_minutes": 30,
        "sequence_order": 0,
        "frequency": "daily"
    })
    print(f"Step Response: {step_resp.status_code}")
    print(step_resp.content.decode())
else:
    print("Failed to create process")
