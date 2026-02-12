import http.client
import json
import sys
import random
import string
import datetime

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_step_retrieval():
    conn = http.client.HTTPConnection("localhost", 8000)
    headers = {"Content-Type": "application/json"}
    
    # 0. Register and Login
    print("0. Registering and Logging in...")
    email = f"test_{get_random_string()}@example.com"
    password = "password123"
    
    # Register
    reg_payload = json.dumps({
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    conn.request("POST", "/api/auth/register", reg_payload, headers)
    reg_resp = conn.getresponse()
    reg_data = reg_resp.read().decode("utf-8")
    
    if reg_resp.status != 201:
        print(f"Failed to register: {reg_resp.status}")
        print(reg_data)
        sys.exit(1)

    # Login (form-urlencoded)
    login_payload = f"username={email}&password={password}"
    login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    conn.request("POST", "/api/auth/login", login_payload, login_headers)
    login_resp = conn.getresponse()
    login_data = login_resp.read().decode("utf-8")
    
    if login_resp.status != 200:
        print(f"Failed to login: {login_resp.status}")
        print(login_data)
        sys.exit(1)
        
    token = json.loads(login_data)["access_token"]
    print(f"Logged in as {email}")
    
    # Update headers with token
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # 0.5 Create a Goal (Required for Process)
    print("0.5 Creating Goal...")
    goal_payload = json.dumps({
        "title": "Test Goal for Process",
        "description": "A dummy goal to link process to",
        "deadline": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
        "pillar": "Growth", # Assuming enum or string
        "priority": "High",
        "purpose": "To verify system functionality"
    })
    # Note: Endpoint might be /api/inputs/goals based on earlier file listing or service usage
    # Step 141 showed `getGoals` calls `/inputs/goals`.
    conn.request("POST", "/api/inputs/goals", goal_payload, auth_headers)
    goal_resp = conn.getresponse()
    goal_data = goal_resp.read().decode("utf-8")
    
    if goal_resp.status != 201:
        print(f"Failed to create goal: {goal_resp.status}")
        print(goal_data)
        # Try finding existing goals if creation fails?
        # But let's assume creation works or we debug that.
        sys.exit(1)
        
    goal_id = json.loads(goal_data)["id"]
    print(f"Goal created: {goal_id}")

    # 1. Create Process
    print("1. Creating Process...")
    payload = json.dumps({
        "name": "Native Retrieval Test Process",
        "steps": [],
        "description": "Testing Step Retrieval with Native Libs",
        "goal_id": goal_id
    })
    conn.request("POST", "/api/processes", payload, auth_headers)
    proc_resp = conn.getresponse()
    proc_data = proc_resp.read().decode("utf-8")
    
    if proc_resp.status != 201:
        print(f"Failed to create process: {proc_resp.status}")
        print(proc_data)
        sys.exit(1)
        
    proc_id = json.loads(proc_data)["id"]
    print(f"Process created: {proc_id}")
    
    # 2. Add Step
    print("2. Adding Step...")
    step_payload = json.dumps({
        "name": "Native Test Step 1",
        "description": "First step",
        "sequence_order": 0,
        "frequency": "daily"
    })
    conn.request("POST", f"/api/processes/{proc_id}/steps", step_payload, auth_headers)
    step_resp = conn.getresponse()
    step_data = step_resp.read().decode("utf-8")
    
    if step_resp.status != 201:
        print(f"Failed to add step: {step_resp.status}")
        print(step_data)
        sys.exit(1)
        
    print("Step added successfully")
    
    # 3. Retrieving Steps
    print("3. Retrieving Steps...")
    conn.request("GET", f"/api/processes/{proc_id}/steps", headers=auth_headers)
    get_resp = conn.getresponse()
    get_data = get_resp.read().decode("utf-8")
    
    if get_resp.status != 200:
        print(f"Failed to retrieve steps: {get_resp.status}")
        print(get_data)
        sys.exit(1)
        
    steps = json.loads(get_data)
    print(f"Retrieved {len(steps)} steps")
    
    if len(steps) == 1 and steps[0]["name"] == "Native Test Step 1":
        print("SUCCESS: Retrieved specific step correctly!")
    else:
        print("FAILURE: Steps data mismatch")
        print(json.dumps(steps, indent=2))
        sys.exit(1)

    conn.close()

if __name__ == "__main__":
    try:
        test_step_retrieval()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
