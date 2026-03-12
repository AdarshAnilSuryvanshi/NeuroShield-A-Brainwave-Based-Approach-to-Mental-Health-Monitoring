import requests

url = "http://127.0.0.1:8000/ml/chat/2/"
data = {
    "question": "Compare with previous upload"
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:")
print(response.json())