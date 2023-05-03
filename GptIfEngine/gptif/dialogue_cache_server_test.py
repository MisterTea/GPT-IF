import requests

from gptif.console import DEBUG_INPUT

if __name__ == "__main__":
    s = requests.Session()
    response = s.post("http://localhost:8000/api/begin_game")
    print(response)
    print(response.content)
    print(response.cookies)
    for command in DEBUG_INPUT:
        response = s.post(
            "http://localhost:8000/api/handle_input", json={"command": command}
        )
        print(response)
        print(response.content)
        print(s.cookies["session_cookie"])
