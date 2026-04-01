import requests
from config import API_KEY, BASE_URL


def get_apod_data(chosen_date=None):
    params = {"api_key": API_KEY}

    if chosen_date:
        params["date"] = chosen_date

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()