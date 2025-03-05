import requests
import json
import sys

def test_flow_api(task, debug=False):
    """Test the flow API endpoint."""
    base_url = "http://localhost:8000"
    
    if debug:
        endpoint = f"{base_url}/flow/debug"
        data = {
            "task": task,
            "model_name": "gpt-4o",
            "temperature": 0.7
        }
        response = requests.post(endpoint, json=data)
    else:
        endpoint = f"{base_url}/flow/create"
        params = {
            "task": task,
            "model_name": "gpt-4o",
            "temperature": 0.7
        }
        response = requests.post(endpoint, params=params)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print("Error:")
        print(response.text)
        return None

if __name__ == "__main__":
    task = "Build a customer service chatbot that can handle product inquiries and returns"
    if len(sys.argv) > 1:
        task = sys.argv[1]
    
    debug_mode = False
    if len(sys.argv) > 2 and sys.argv[2].lower() == "debug":
        debug_mode = True
    
    print(f"Testing API with task: {task}")
    print(f"Debug mode: {debug_mode}")
    test_flow_api(task, debug_mode)