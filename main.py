import os
import webbrowser
import requests
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from PIL import Image

API_KEY = "DEMO_KEY"
BASE_URL = "https://api.nasa.gov/planetary/apod"
DOWNLOADS_FOLDER = "downloads"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def validar_data(data_str):
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")

        if data.date() > datetime.now().date():
            return False, "Não podes escolher uma data no futuro."

        return True, ""

    except ValueError:
        return False, "Formato inválido. Usa AAAA-MM-DD (ex: 2024-01-15)."


def download_file(url, filename):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)


def save_text_file(filename, title, date, explanation, media_type, media_url, copyright_text):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Título: {title}\n")
        file.write(f"Data: {date}\n")
        file.write(f"Tipo: {media_type}\n")
        file.write(f"URL: {media_url}\n")
        file.write(f"Copyright: {copyright_text}\n\n")
        file.write("Descrição:\n")
        file.write(explanation)


def get_apod_data(chosen_date=None):
    params = {"api_key": API_KEY}

    if chosen_date:
        params["date"] = chosen_date

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


class NasaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NASA APOD Viewer")
        self.geometry("1280x820")
        self.minsize(1100, 720)

        os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

        self.current_media_url = None
        self.current_media_type = None
        self.current_date = None
        self.current_title = None
        self.current_description = None
        self.current_copyright = None
        self.current_ctk_image = None

        self.build_ui()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, corner_radius=20)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="NASA Astronomy Picture of the Day",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Explora imagens astronómicas e vídeos da NASA numa interface mais moderna.",
            font=ctk.CTkFont(size=14),
            text_color="#AAB0C5"
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 10))
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.controls_card = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.controls_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.controls_card.grid_columnconfigure(8, weight=1)

        self.date_label = ctk.CTkLabel(
            self.controls_card,
            text="Data",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.date_label.grid(row=0, column=0, padx=(18, 8), pady=18)

        self.date_entry = ctk.CTkEntry(
            self.controls_card,
            width=150,
            height=40,
            corner_radius=14,
            placeholder_text="AAAA-MM-DD"
        )
        self.date_entry.grid(row=0, column=1, padx=6, pady=18)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.hint_label = ctk.CTkLabel(
            self.controls_card,
            text="Formato: AAAA-MM-DD",
            text_color="#9AA3B2"
        )
        self.hint_label.grid(row=0, column=2, padx=(8, 18), pady=18)

        self.today_button = ctk.CTkButton(
            self.controls_card,
            text="Hoje",
            width=120,
            height=42,
            corner_radius=18,
            command=self.load_today
        )
        self.today_button.grid(row=0, column=3, padx=6, pady=18)

        self.date_button = ctk.CTkButton(
            self.controls_card,
            text="Escolher data",
            width=140,
            height=42,
            corner_radius=18,
            command=self.load_selected_date
        )
        self.date_button.grid(row=0, column=4, padx=6, pady=18)

        self.video_button = ctk.CTkButton(
            self.controls_card,
            text="Abrir vídeo",
            width=130,
            height=42,
            corner_radius=18,
            fg_color="#2E3445",
            hover_color="#3A4156",
            command=self.open_media_in_browser
        )
        self.video_button.grid(row=0, column=5, padx=6, pady=18)

        self.save_button = ctk.CTkButton(
            self.controls_card,
            text="Guardar",
            width=120,
            height=42,
            corner_radius=18,
            fg_color="#2E3445",
            hover_color="#3A4156",
            command=self.save_current_info_again
        )
        self.save_button.grid(row=0, column=6, padx=6, pady=18)

        self.exit_button = ctk.CTkButton(
            self.controls_card,
            text="Sair",
            width=100,
            height=42,
            corner_radius=18,
            fg_color="#8B1E3F",
            hover_color="#A02449",
            command=self.quit
        )
        self.exit_button.grid(row=0, column=7, padx=(6, 18), pady=18)

        self.left_panel = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.right_panel = ctk.CTkFrame(self.main_frame, corner_radius=20)
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.info_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))

        self.apod_title = ctk.CTkLabel(
            self.info_frame,
            text="Título: —",
            justify="left",
            anchor="w",
            wraplength=700,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.apod_title.pack(anchor="w", fill="x", pady=(0, 12))

        self.apod_date = ctk.CTkLabel(
            self.info_frame,
            text="Data: —",
            anchor="w",
            font=ctk.CTkFont(size=14),
            text_color="#B4BCD0"
        )
        self.apod_date.pack(anchor="w", pady=3)

        self.apod_type = ctk.CTkLabel(
            self.info_frame,
            text="Tipo: —",
            anchor="w",
            font=ctk.CTkFont(size=14),
            text_color="#B4BCD0"
        )
        self.apod_type.pack(anchor="w", pady=3)

        self.apod_copyright = ctk.CTkLabel(
            self.info_frame,
            text="Copyright: —",
            justify="left",
            anchor="w",
            wraplength=700,
            font=ctk.CTkFont(size=14),
            text_color="#B4BCD0"
        )
        self.apod_copyright.pack(anchor="w", fill="x", pady=3)

        self.image_frame = ctk.CTkFrame(self.left_panel, corner_radius=18, fg_color="#10131A")
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="Carrega em “Hoje” ou escolhe uma data.",
            font=ctk.CTkFont(size=18),
            text_color="#8C95A8"
        )
        self.image_label.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.desc_title = ctk.CTkLabel(
            self.right_panel,
            text="Descrição",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.desc_title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        self.description_text = ctk.CTkTextbox(
            self.right_panel,
            corner_radius=16,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.description_text.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.description_text.insert("1.0", "A descrição vai aparecer aqui.")
        self.description_text.configure(state="disabled")

        self.status_label = ctk.CTkLabel(
            self,
            text="Pronto.",
            height=32,
            anchor="w",
            text_color="#91D7AE",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))

    def set_status(self, text):
        self.status_label.configure(text=text)

    def set_description(self, text):
        self.description_text.configure(state="normal")
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", text)
        self.description_text.configure(state="disabled")

    def clear_image(self, message):
        self.image_label.configure(image=None, text=message)
        self.current_ctk_image = None

    def show_image(self, image_path):
        image = Image.open(image_path)
        image.thumbnail((760, 460))

        self.current_ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
        self.image_label.configure(image=self.current_ctk_image, text="")

    def update_ui_with_data(self, data):
        title = data["title"]
        date = data["date"]
        explanation = data["explanation"]
        media_type = data["media_type"]
        media_url = data["url"]
        copyright_text = data.get("copyright", "Não disponível")

        self.current_media_url = media_url
        self.current_media_type = media_type
        self.current_date = date
        self.current_title = title
        self.current_description = explanation
        self.current_copyright = copyright_text

        self.apod_title.configure(text=f"Título: {title}")
        self.apod_date.configure(text=f"Data: {date}")
        self.apod_type.configure(text=f"Tipo: {media_type}")
        self.apod_copyright.configure(text=f"Copyright: {copyright_text}")
        self.set_description(explanation)

        text_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{date}.txt")
        save_text_file(
            text_path,
            title,
            date,
            explanation,
            media_type,
            media_url,
            copyright_text
        )

        if media_type == "image":
            image_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{date}.jpg")
            download_file(media_url, image_path)
            self.show_image(image_path)
            self.set_status(f"Imagem e descrição guardadas em '{DOWNLOADS_FOLDER}'.")
        else:
            self.clear_image("Este conteúdo é um vídeo. Usa o botão “Abrir vídeo”.")
            self.set_status(f"Vídeo carregado. Descrição guardada em '{DOWNLOADS_FOLDER}'.")

    def load_today(self):
        try:
            self.set_status("A carregar conteúdo de hoje...")
            self.update_idletasks()

            data = get_apod_data()
            self.update_ui_with_data(data)

        except requests.exceptions.HTTPError as error:
            messagebox.showerror("Erro HTTP", str(error))
            self.set_status("Falha ao carregar os dados.")
        except requests.exceptions.RequestException as error:
            messagebox.showerror("Erro de ligação", str(error))
            self.set_status("Erro de rede.")
        except KeyError as error:
            messagebox.showerror("Erro nos dados", f"Campo em falta: {error}")
            self.set_status("Resposta incompleta da API.")
        except Exception as error:
            messagebox.showerror("Erro", str(error))
            self.set_status("Ocorreu um erro inesperado.")

    def load_selected_date(self):
        chosen_date = self.date_entry.get().strip()

        valid, message = validar_data(chosen_date)
        if not valid:
            messagebox.showwarning("Data inválida", message)
            self.set_status("Data inválida.")
            return

        try:
            self.set_status(f"A carregar conteúdo para {chosen_date}...")
            self.update_idletasks()

            data = get_apod_data(chosen_date)
            self.update_ui_with_data(data)

        except requests.exceptions.HTTPError as error:
            messagebox.showerror("Erro HTTP", f"{error}\nVerifica se a data existe e está correta.")
            self.set_status("Falha ao carregar a data escolhida.")
        except requests.exceptions.RequestException as error:
            messagebox.showerror("Erro de ligação", str(error))
            self.set_status("Erro de rede.")
        except KeyError as error:
            messagebox.showerror("Erro nos dados", f"Campo em falta: {error}")
            self.set_status("Resposta incompleta da API.")
        except Exception as error:
            messagebox.showerror("Erro", str(error))
            self.set_status("Ocorreu um erro inesperado.")

    def open_media_in_browser(self):
        if not self.current_media_url:
            messagebox.showinfo("Sem conteúdo", "Ainda não carregaste nenhum conteúdo.")
            return

        webbrowser.open(self.current_media_url)
        self.set_status("Conteúdo aberto no navegador.")

    def save_current_info_again(self):
        if not self.current_date:
            messagebox.showinfo("Sem conteúdo", "Ainda não carregaste nenhum conteúdo.")
            return

        text_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{self.current_date}.txt")
        save_text_file(
            text_path,
            self.current_title,
            self.current_date,
            self.current_description,
            self.current_media_type,
            self.current_media_url or "",
            self.current_copyright
        )

        if self.current_media_type == "image" and self.current_media_url:
            image_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{self.current_date}.jpg")
            if not os.path.exists(image_path):
                download_file(self.current_media_url, image_path)

        messagebox.showinfo("Guardado", f"Os ficheiros foram guardados em '{DOWNLOADS_FOLDER}'.")
        self.set_status("Conteúdo guardado novamente com sucesso.")


if __name__ == "__main__":
    app = NasaApp()
    app.mainloop()