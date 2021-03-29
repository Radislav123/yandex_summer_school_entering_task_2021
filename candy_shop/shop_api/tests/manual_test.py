import requests
import json
import os


TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_REQUESTS_FOLDER = f"{TEST_FOLDER}/jsons/requests/"
SCHEME = "http"
HOST = "178.154.194.95"
PORT = 8080
URL_BASE = f"{SCHEME}://{HOST}:{PORT}/"


def test():
    with open(JSON_REQUESTS_FOLDER + "couriers_post_valid.json", 'r') as file:
        url = URL_BASE + "couriers"
        data = json.load(file)
        response = requests.post(url, json = data)
        print(response)
        print(response.json())
        print()


def run_tests():
    test()


run_tests()
