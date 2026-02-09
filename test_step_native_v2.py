import http.client
import json
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

email = f"user_{get_random_string(5)}@test.com"
password = "password123"

conn = http.client.HTTPConnection("localhost", 8000)
headers = {"Content-Type": "application/json"}

print(f"1. Registering user: {email}")
reg_payload = json.dumps({"email": email, "password": password, "full_name": "Test User"})
conn.request("POST", "/api/auth/register", reg_payload, headers)
reg_res = conn.getresponse()
reg_data = reg_res.read().decode("utf-8")
print(f"Register Status: {reg_res.status}")

print("2. Logging in...")
login_payload = json.dumps({"username": email, "password": password}) # API uses OAuth2PasswordRequestForm but usually expects x-www-form-urlencoded, let's check. 
# Wait, FastAPI OAuth2PasswordRequestForm expects form data, not JSON. Service might be different.
# Let's try x-www-form-urlencoded for login path /api/auth/login or /api/auth/token

# Let's check auth router. checking... assuming /api/auth/login takes JSON or Form?
# Most FastAPI implementations use Form. Let's try Form first.
headers_form = {"Content-Type": "application/x-www-form-urlencoded"}
body_form = f"username={email}&password={password}"
conn.request("POST", "/api/auth/login", body_form, headers_form)
login_res = conn.getresponse()
login_data = login_res.read().decode("utf-8")
print(f"Login Status: {login_res.status}")
print(f"Login Data: {login_data}")

if login_res.status == 200:
    token = json.loads(login_data)["access_token"]
    print(f"Token: {token[:10]}...")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # 3. Create Process
    print("3. Creating Process...")
    proc_payload = json.dumps({"name": "Http Test Process", "steps": []})
    conn.request("POST", "/api/processes", proc_payload, auth_headers)
    proc_res = conn.getresponse()
    proc_data = proc_res.read().decode("utf-8")
    print(f"Process Status: {proc_res.status}")
    
    if proc_res.status == 201:
        proc_id = json.loads(proc_data)["id"]
        print(f"Process ID: {proc_id}")
        
        # 4. Add Step
        print("4. Adding Step...")
        step_payload = json.dumps({
            "name": "First Step",
            "quality_criteria": "High Quality",
            "expected_output": "Good Output",
            "estimated_duration_minutes": 30
        })
        conn.request("POST", f"/api/processes/{proc_id}/steps", step_payload, auth_headers)
        step_res = conn.getresponse()
        step_data = step_res.read().decode("utf-8")
        print(f"Step Status: {step_res.status}")
        print(f"Step Data: {step_data}")
    else:
        print(f"Failed to create process: {proc_data}")
else:
    print("Login failed")

conn.close()
