import requests
import os
from datetime import datetime

API_KEY = "uKFRrdIfk5xjm1M0SJRFbXORK5mGwARc6ZgkQhGW"
BASE_URL = "https://api.nasa.gov/planetary/apod"


def validar_data(data_str):
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")

        if data > datetime.now():
            print("Erro: não podes escolher uma data no futuro.")
            return False

        return True

    except ValueError:
        print("Erro: formato inválido. Usa AAAA-MM-DD (ex: 2024-01-15).")
        return False


def download_image(image_url, filename):
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)


def save_text_file(filename, title, date, explanation):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Título: {title}\n")
        file.write(f"Data: {date}\n\n")
        file.write(explanation)


def get_apod_data(chosen_date):
    params = {
        "api_key": API_KEY,
        "date": chosen_date
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def main():
    os.makedirs("downloads", exist_ok=True)

    while True:
        chosen_date = input("Escreve uma data (AAAA-MM-DD): ")

        if validar_data(chosen_date):
            break

    try:
        data = get_apod_data(chosen_date)

        title = data["title"]
        date = data["date"]
        explanation = data["explanation"]
        media_type = data["media_type"]
        media_url = data["url"]

        print("\n--- NASA APOD ---")
        print("Título:", title)
        print("Data:", date)
        print("Tipo:", media_type)
        print("URL:", media_url)

        image_path = f"downloads/apod_{date}.jpg"
        text_path = f"downloads/apod_{date}.txt"

        if media_type == "image":
            download_image(media_url, image_path)
            print(f"Imagem guardada em: {image_path}")
        else:
            print("Nesse dia a NASA publicou um vídeo, não uma imagem.")

        save_text_file(text_path, title, date, explanation)
        print(f"Descrição guardada em: {text_path}")

    except requests.exceptions.HTTPError as error:
        print("Erro HTTP:", error)
        print("Verifica se a data existe e está no formato correto.")
    except requests.exceptions.RequestException as error:
        print("Erro de ligação:", error)
    except KeyError as error:
        print("Falta um campo esperado na resposta:", error)


if __name__ == "__main__":
    main()