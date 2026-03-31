import requests
import os

API_KEY = "uKFRrdIfk5xjm1M0SJRFbXORK5mGwARc6ZgkQhGW"
BASE_URL = "https://api.nasa.gov/planetary/apod"

def download_image(image_url, filename):
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

    with open(filename, 'wb') as file:
        file.write(response.content)

def save_text_file(filename, title, date, explanation):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Título: {title}\n")
        file.write(f"Data: {date}\n\n")
        file.write(explanation)

def main():
    # criar pasta downloads se não existir
    os.makedirs("downloads", exist_ok=True)

    params = {
        "api_key": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

    data = response.json()

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

    # caminho dos ficheiros
    image_path = f"downloads/apod_{date}.jpg"
    text_path = f"downloads/apod_{date}.txt"

    if data["media_type"] == "image":
        download_image(media_url, image_path)
        print(f"Imagem salva em: {image_path}")
    else:
        print("O conteúdo não é uma imagem, não foi possível baixar.")

    # guardar descrição sempre
    save_text_file(text_path, title, date, explanation)
    print(f"Descrição salva em: {text_path}")

if __name__ == "__main__":
    main()


        