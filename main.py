import os
import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk

API_KEY = "uKFRrdIfk5xjm1M0SJRFbXORK5mGwARc6ZgkQhGW"
BASE_URL = "https://api.nasa.gov/planetary/apod"


def validar_data(data_str):
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")

        if data.date() > datetime.now().date():
            return False, "Não podes escolher uma data no futuro."

        return True, ""

    except ValueError:
        return False, "Formato inválido. Usa AAAA-MM-DD (ex: 2024-01-15)."


def download_file(url, filename):
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)


def save_text_file(filename, title, date, explanation):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Título: {title}\n")
        file.write(f"Data: {date}\n\n")
        file.write(explanation)


def get_apod_data(chosen_date=None):
    params = {"api_key": API_KEY}

    if chosen_date:
        params["date"] = chosen_date

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


class NasaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA APOD Viewer")
        self.root.geometry("900x700")
        self.root.configure(bg="#101820")

        os.makedirs("downloads", exist_ok=True)

        self.current_image = None

        self.build_ui()

    def build_ui(self):
        title_label = tk.Label(
            self.root,
            text="NASA Astronomy Picture of the Day",
            font=("Arial", 20, "bold"),
            bg="#101820",
            fg="white"
        )
        title_label.pack(pady=10)

        top_frame = tk.Frame(self.root, bg="#101820")
        top_frame.pack(pady=10)

        self.date_entry = tk.Entry(top_frame, font=("Arial", 12), width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        date_hint = tk.Label(
            top_frame,
            text="AAAA-MM-DD",
            font=("Arial", 11),
            bg="#101820",
            fg="lightgray"
        )
        date_hint.pack(side=tk.LEFT, padx=5)

        buttons_frame = tk.Frame(self.root, bg="#101820")
        buttons_frame.pack(pady=10)

        today_button = tk.Button(
            buttons_frame,
            text="Hoje",
            font=("Arial", 12, "bold"),
            command=self.load_today,
            width=15
        )
        today_button.pack(side=tk.LEFT, padx=10)

        date_button = tk.Button(
            buttons_frame,
            text="Escolher data",
            font=("Arial", 12, "bold"),
            command=self.load_selected_date,
            width=15
        )
        date_button.pack(side=tk.LEFT, padx=10)

        exit_button = tk.Button(
            buttons_frame,
            text="Sair",
            font=("Arial", 12, "bold"),
            command=self.root.quit,
            width=15
        )
        exit_button.pack(side=tk.LEFT, padx=10)

        self.info_frame = tk.Frame(self.root, bg="#101820")
        self.info_frame.pack(pady=10, fill="x")

        self.title_value = tk.Label(
            self.info_frame,
            text="Título: ",
            font=("Arial", 14, "bold"),
            bg="#101820",
            fg="white",
            wraplength=850,
            justify="left"
        )
        self.title_value.pack(anchor="w", padx=20, pady=5)

        self.date_value = tk.Label(
            self.info_frame,
            text="Data: ",
            font=("Arial", 12),
            bg="#101820",
            fg="white"
        )
        self.date_value.pack(anchor="w", padx=20, pady=5)

        self.media_value = tk.Label(
            self.info_frame,
            text="Tipo: ",
            font=("Arial", 12),
            bg="#101820",
            fg="white"
        )
        self.media_value.pack(anchor="w", padx=20, pady=5)

        self.image_label = tk.Label(self.root, bg="#101820")
        self.image_label.pack(pady=10)

        description_title = tk.Label(
            self.root,
            text="Descrição",
            font=("Arial", 14, "bold"),
            bg="#101820",
            fg="white"
        )
        description_title.pack(pady=(10, 0))

        self.description_text = tk.Text(
            self.root,
            wrap="word",
            font=("Arial", 11),
            height=12,
            width=95
        )
        self.description_text.pack(padx=20, pady=10)
        self.description_text.config(state="disabled")

    def set_description(self, text):
        self.description_text.config(state="normal")
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state="disabled")

    def show_image(self, image_path):
        image = Image.open(image_path)

        max_width = 700
        max_height = 350

        image.thumbnail((max_width, max_height))

        self.current_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.current_image, text="")

    def clear_image(self, message="Sem imagem para mostrar."):
        self.image_label.config(image="", text=message, fg="white", font=("Arial", 12))
        self.current_image = None

    def process_apod(self, data):
        title = data["title"]
        date = data["date"]
        explanation = data["explanation"]
        media_type = data["media_type"]
        media_url = data["url"]

        self.title_value.config(text=f"Título: {title}")
        self.date_value.config(text=f"Data: {date}")
        self.media_value.config(text=f"Tipo: {media_type}")
        self.set_description(explanation)

        text_path = f"downloads/apod_{date}.txt"
        save_text_file(text_path, title, date, explanation)

        if media_type == "image":
            image_path = f"downloads/apod_{date}.jpg"
            download_file(media_url, image_path)
            self.show_image(image_path)
        else:
            self.clear_image("Nesse dia a NASA publicou um vídeo, não uma imagem.")

    def load_today(self):
        try:
            data = get_apod_data()
            self.process_apod(data)

        except requests.exceptions.HTTPError as error:
            messagebox.showerror("Erro HTTP", str(error))
        except requests.exceptions.RequestException as error:
            messagebox.showerror("Erro de ligação", str(error))
        except KeyError as error:
            messagebox.showerror("Erro nos dados", f"Campo em falta: {error}")
        except Exception as error:
            messagebox.showerror("Erro", str(error))

    def load_selected_date(self):
        chosen_date = self.date_entry.get().strip()

        valid, message = validar_data(chosen_date)
        if not valid:
            messagebox.showwarning("Data inválida", message)
            return

        try:
            data = get_apod_data(chosen_date)
            self.process_apod(data)

        except requests.exceptions.HTTPError as error:
            messagebox.showerror(
                "Erro HTTP",
                f"{error}\nVerifica se a data existe e está correta."
            )
        except requests.exceptions.RequestException as error:
            messagebox.showerror("Erro de ligação", str(error))
        except KeyError as error:
            messagebox.showerror("Erro nos dados", f"Campo em falta: {error}")
        except Exception as error:
            messagebox.showerror("Erro", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = NasaApp(root)
    root.mainloop()