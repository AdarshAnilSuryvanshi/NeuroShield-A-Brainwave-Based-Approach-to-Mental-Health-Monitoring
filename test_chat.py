import requests

url =  "http://127.0.0.1:8000/ml/chat/7/"
data = {
    "question": "Am I depressed?"
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:")
print(response.json()) 
