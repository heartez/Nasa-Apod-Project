import requests

API_KEY = "uKFRrdIfk5xjm1M0SJRFbXORK5mGwARc6ZgkQhGW"
BASE_URL = "https://api.nasa.gov/planetary/apod"

def download_image(image_url, filename):
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

    with open(filename, 'wb') as file:
        file.write(response.content)


params = {
    "api_key": API_KEY
}

response = requests.get(BASE_URL, params=params, timeout=10)
data = response.json()

print("\n--- NASA APOD ---")
print("Título:", data["title"])
print("Data:", data["date"])
print("Descrição:", data["explanation"])
print("URL:", data["url"])
print("Tipo:", data["media_type"])

if data["media_type"] == "image":
    filename = f"apod_{data['date']}.jpg"
    download_image(data["url"], filename)
    print(f"Imagem baixada como: {filename}")
else:
    print("A mídia do dia não é uma imagem.")