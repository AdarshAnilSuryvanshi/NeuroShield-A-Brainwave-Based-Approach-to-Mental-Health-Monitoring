import requests

url = "http://127.0.0.1:8000/ml/stage5/analyze/9/"
data = {

  "question": "What does this prediction mean for my mental stability and what should I do next?"
}


response = requests.post(url, json=data)
print(response.status_code)
print(response.json())