import requests
from config import API_KEY, BASE_URL


def get_apod_data(chosen_date=None):
    params = {"api_key": API_KEY}

    if chosen_date:
        params["date"] = chosen_date

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def get_random_apod():
    params = {
        "api_key": API_KEY,
        "count": 1
    }

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, list) and len(data) > 0:
        return data[0]

    raise ValueError("Não foi possível obter uma imagem aleatória.")