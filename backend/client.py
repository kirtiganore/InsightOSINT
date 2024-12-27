import requests

url = "http://127.0.0.1:5000/search"
payload = {"query": "Artificial Intelligence"}
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Response from the Flask app:\n")
    print(response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")
