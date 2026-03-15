import requests

url = "http://127.0.0.1:8000/ml/stage4/chat/8/"
data = {
    "question": "Compare this upload with the previous one and explain the change"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())