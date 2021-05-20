import requests

url = "https://cssminifier.com/raw"
data = {"input": open("static/css/main.css", "rb").read()}
response = requests.post(url, data=data)

with open("static/css/main.min.css", "w") as f:
    f.write(response.text)
