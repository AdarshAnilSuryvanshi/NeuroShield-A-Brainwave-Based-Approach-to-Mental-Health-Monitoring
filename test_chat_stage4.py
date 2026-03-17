import requests

url = "http://127.0.0.1:8000/ml/stage5/chat/3/"
data = {

  "question": "What is the risk level?  Is this case high risk?  Should this case be escalated?  Why is the system marking high risk?"
}


response = requests.post(url, json=data)
print(response.status_code)
print(response.json())