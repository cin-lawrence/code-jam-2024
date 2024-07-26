import requests

API_URL = "https://opentdb.com/api.php?amount=1"

TOKEN_URL = "https://opentdb.com/api_token.php?command=request"


def get_trivia():
    token_call = requests.post(TOKEN_URL)

    token = token_call.json()["token"]

    response = requests.post(f"{API_URL}&token={token}")

    return response.json()["results"][0]["question"]
