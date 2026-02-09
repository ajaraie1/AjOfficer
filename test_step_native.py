import http.client
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYTM0OTg5NS1mMGJkLTRjZjctYjlhMy05ZjI5ZTExNjQ5NjUiLCJlbWFpbCI6InRlc3QyQHRlc3QuY29tIiwiZXhwIjoxNzcwNjQ3NjY5fQ.rseypXSuDRYZro2awR-0s9eRB0A97yhWIMfEjNTR4UI"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

conn = http.client.HTTPConnection("localhost", 8000)

# 1. Create Process
print("Creating Process...")
payload = json.dumps({"name": "Http Test Process", "steps": []})
conn.request("POST", "/api/processes", payload, headers)
res = conn.getresponse()
data = res.read().decode("utf-8")
print(f"Status: {res.status}")
print(f"Data: {data}")

if res.status == 201:
    proc_id = json.loads(data)["id"]
    print(f"Process ID: {proc_id}")
    
    # 2. Add Step
    print("Adding Step...")
    step_payload = json.dumps({
        "name": "First Step",
        "description": "Step Description",
        "quality_criteria": "High Quality",
        "expected_output": "Good Output",
        "estimated_duration_minutes": 30,
        "sequence_order": 0,
        "frequency": "daily"
    })
    conn.request("POST", f"/api/processes/{proc_id}/steps", step_payload, headers)
    step_res = conn.getresponse()
    step_data = step_res.read().decode("utf-8")
    print(f"Step Status: {step_res.status}")
    print(f"Step Data: {step_data}")
else:
    print("Failed to create process")

conn.close()
