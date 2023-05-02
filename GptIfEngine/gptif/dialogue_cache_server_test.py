import requests

if __name__ == "__main__":
    s = requests.Session()
    response = s.post("http://localhost:8000/handle_input", json={"command": "LOOK"})
    print(response)
    print(response.content)
    print(response.cookies)
