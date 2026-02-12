import http.client
import json
import sys
import random
import string
import datetime

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_smart_generation():
    conn = http.client.HTTPConnection("localhost", 8000)
    headers = {"Content-Type": "application/json"}
    
    # 0. Register and Login
    print("0. Registering and Logging in...")
    email = f"smart_{get_random_string()}@example.com"
    password = "password123"
    
    # Register
    reg_payload = json.dumps({
        "email": email,
        "password": password,
        "full_name": "Smart User"
    })
    conn.request("POST", "/api/auth/register", reg_payload, headers)
    reg_resp = conn.getresponse()
    reg_data = reg_resp.read().decode("utf-8")
    
    if reg_resp.status != 201:
        print(f"Failed to register: {reg_resp.status}")
        print(reg_data)
        sys.exit(1)

    # Login
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
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # 1. Create Goal
    print("1. Creating Goal...")
    goal_payload = json.dumps({
        "title": "Smart Goal",
        "description": "Testing Smart Logic",
        "deadline": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
        "pillar": "Growth",
        "priority": "High",
        "purpose": "To test auto-generation"
    })
    conn.request("POST", "/api/inputs/goals", goal_payload, auth_headers)
    goal_resp = conn.getresponse()
    goal_data = goal_resp.read().decode("utf-8")
    if goal_resp.status != 201:
        print(f"Failed to create goal: {goal_resp.status}")
        print(goal_data)
        sys.exit(1)
    goal_id = json.loads(goal_data)["id"]

    # 2. Create Process
    print("2. Creating Process...")
    proc_payload = json.dumps({
        "name": "Smart Process",
        "steps": [],
        "description": "Process for smart logic",
        "goal_id": goal_id
    })
    conn.request("POST", "/api/processes", proc_payload, auth_headers)
    proc_resp = conn.getresponse()
    proc_data = proc_resp.read().decode("utf-8")
    if proc_resp.status != 201:
        print(f"Failed to create process: {proc_resp.status}")
        print(proc_data)
        sys.exit(1)
    proc_id = json.loads(proc_data)["id"]
    
    # 2.5 Activate Process
    print("2.5 Activating Process...")
    activate_payload = json.dumps({
        "status": "active"
    })
    conn.request("PATCH", f"/api/processes/{proc_id}", activate_payload, auth_headers)
    activate_resp = conn.getresponse()
    activate_data = activate_resp.read().decode("utf-8")
    if activate_resp.status != 200:
        print(f"Failed to activate process: {activate_resp.status}")
        print(activate_data)
        sys.exit(1)
    print("Process activated.")
    
    # 3. Add ACTIVE Step
    print("3. Adding Active Step...")
    step_payload = json.dumps({
        "name": "Daily Habit",
        "description": "This should generate a log",
        "sequence_order": 0,
        "frequency": "daily",
        "is_active": True
    })
    conn.request("POST", f"/api/processes/{proc_id}/steps", step_payload, auth_headers)
    step_resp = conn.getresponse()
    step_data = step_resp.read().decode("utf-8")
    if step_resp.status != 201:
        print(f"Failed to add step: {step_resp.status}")
        print(step_data)
        sys.exit(1)
    print("Step 1 added.")

    # 3.5 Add Second Active Step (to test sequence)
    print("3.5 Adding Second Active Step...")
    step2_payload = json.dumps({
        "name": "Second Task",
        "description": "Should be scheduled after the first one",
        "sequence_order": 1,
        "frequency": "daily",
        "is_active": True,
        "estimated_duration_minutes": 60 
    })
    conn.request("POST", f"/api/processes/{proc_id}/steps", step2_payload, auth_headers)
    step2_resp = conn.getresponse()
    step2_data = step2_resp.read().decode("utf-8")
    if step2_resp.status != 201:
        print(f"Failed to add step 2: {step2_resp.status}")
        print(step2_data)
        sys.exit(1)
    print("Step 2 added.")
    
    # 4. Trigger Smart Generation
    print("4. Fetching Today's Logs (Triggering Generation)...")
    today = datetime.date.today().isoformat()
    conn.request("GET", f"/api/operations/logs?execution_date={today}", headers=auth_headers)
    logs_resp = conn.getresponse()
    logs_data = logs_resp.read().decode("utf-8")
    
    if logs_resp.status != 200:
        print(f"Failed to fetch logs: {logs_resp.status}")
        print(logs_data)
        sys.exit(1)
        
    logs = json.loads(logs_data)
    print(f"Retrieved {len(logs)} logs.")
    
    # 5. Verify
    if len(logs) >= 2:
        print("SUCCESS: Logs generated!")
        # Sort by planned_start to be sure
        logs.sort(key=lambda x: x["planned_start"])
        
        log1 = logs[0]
        log2 = logs[1]
        
        print(f"Log 1 Start: {log1['planned_start']}")
        print(f"Log 2 Start: {log2['planned_start']}")
        
        # Parse times
        # 2026-02-09T08:00:00 or similar
        t1 = datetime.datetime.fromisoformat(log1["planned_start"])
        t2 = datetime.datetime.fromisoformat(log2["planned_start"])
        
        if t1 < t2:
             print("SUCCESS: Time sequence correct (T1 < T2)")
        else:
             print("FAILURE: Time sequence incorrect")
             sys.exit(1)
             
    else:
        print("FAILURE: Not enough logs generated.")
        print(json.dumps(logs, indent=2))
        sys.exit(1)

    conn.close()

if __name__ == "__main__":
    try:
        test_smart_generation()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
