import requests
import json
import os


TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSONS_FOLDER = f"{TEST_FOLDER}/jsons/requests/"
SCHEME = "http"
HOST = "127.0.0.1"
PORT = 8000
URL_BASE = f"{SCHEME}://{HOST}:{PORT}/"


def couriers_valid():
    with open(JSONS_FOLDER + "couriers_post_valid.json", 'r') as file:
        url = URL_BASE + "couriers"
        data = json.load(file)
        response = requests.post(url, json = data)
        print(response)
        print(response.json())
        print()


def couriers_not_valid():
    with open(JSONS_FOLDER + "couriers_post_not_valid.json", 'r') as file:
        url = URL_BASE + "couriers"
        data = json.load(file)
        response = requests.post(url, json = data)
        print(response)
        print(response.json())
        print()


def run_tests():
    couriers_valid()
    couriers_not_valid()


run_tests()
