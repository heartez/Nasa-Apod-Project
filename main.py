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


class NasaPremiumApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NASA APOD Premium")
        self.geometry("1450x860")
        self.minsize(1200, 760)

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
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#0E1118")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🚀 NASA APOD",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=24, pady=(28, 8), sticky="w")

        self.logo_subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Visualizador premium\nde imagens astronómicas",
            justify="left",
            text_color="#8F98AA",
            font=ctk.CTkFont(size=13)
        )
        self.logo_subtitle.grid(row=1, column=0, padx=24, pady=(0, 28), sticky="w")

        self.sidebar_section = ctk.CTkLabel(
            self.sidebar,
            text="Ações",
            text_color="#6F7A90",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.sidebar_section.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="w")

        self.today_btn = ctk.CTkButton(
            self.sidebar,
            text="Hoje",
            height=46,
            corner_radius=16,
            command=self.load_today,
            anchor="w"
        )
        self.today_btn.grid(row=3, column=0, padx=20, pady=6, sticky="ew")

        self.load_date_btn = ctk.CTkButton(
            self.sidebar,
            text="Escolher data",
            height=46,
            corner_radius=16,
            command=self.load_selected_date,
            anchor="w"
        )
        self.load_date_btn.grid(row=4, column=0, padx=20, pady=6, sticky="ew")

        self.video_btn = ctk.CTkButton(
            self.sidebar,
            text="Abrir vídeo",
            height=46,
            corner_radius=16,
            fg_color="#252B38",
            hover_color="#31384A",
            command=self.open_media_in_browser,
            anchor="w"
        )
        self.video_btn.grid(row=5, column=0, padx=20, pady=6, sticky="ew")

        self.save_btn = ctk.CTkButton(
            self.sidebar,
            text="Guardar ficheiros",
            height=46,
            corner_radius=16,
            fg_color="#252B38",
            hover_color="#31384A",
            command=self.save_current_info_again,
            anchor="w"
        )
        self.save_btn.grid(row=6, column=0, padx=20, pady=6, sticky="ew")

        self.exit_btn = ctk.CTkButton(
            self.sidebar,
            text="Sair",
            height=46,
            corner_radius=16,
            fg_color="#8B1E3F",
            hover_color="#A02449",
            command=self.quit,
            anchor="w"
        )
        self.exit_btn.grid(row=7, column=0, padx=20, pady=6, sticky="ew")

        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="#141925", corner_radius=18)
        self.sidebar_footer.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        self.footer_title = ctk.CTkLabel(
            self.sidebar_footer,
            text="Dica",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.footer_title.pack(anchor="w", padx=16, pady=(14, 6))

        self.footer_text = ctk.CTkLabel(
            self.sidebar_footer,
            text="Usa datas antigas para explorar imagens históricas da NASA.",
            justify="left",
            wraplength=190,
            text_color="#A7B0C0",
            font=ctk.CTkFont(size=12)
        )
        self.footer_text.pack(anchor="w", padx=16, pady=(0, 14))

        # MAIN AREA
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="#090C12")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(2, weight=1)

        # TOPBAR
        self.topbar = ctk.CTkFrame(self.main_area, height=90, corner_radius=0, fg_color="#090C12")
        self.topbar.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 10))
        self.topbar.grid_columnconfigure(3, weight=1)

        self.page_title = ctk.CTkLabel(
            self.topbar,
            text="Astronomy Picture of the Day",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.page_title.grid(row=0, column=0, padx=(0, 20), pady=(8, 2), sticky="w")

        self.page_subtitle = ctk.CTkLabel(
            self.topbar,
            text="Escolhe uma data e vê a imagem, vídeo e descrição da NASA numa interface moderna.",
            text_color="#95A0B5",
            font=ctk.CTkFont(size=14)
        )
        self.page_subtitle.grid(row=1, column=0, columnspan=2, sticky="w")

        self.date_entry = ctk.CTkEntry(
            self.topbar,
            width=160,
            height=42,
            corner_radius=16,
            placeholder_text="AAAA-MM-DD"
        )
        self.date_entry.grid(row=0, column=2, rowspan=2, padx=(10, 10), sticky="e")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.quick_load_btn = ctk.CTkButton(
            self.topbar,
            text="Carregar",
            width=120,
            height=42,
            corner_radius=16,
            command=self.load_selected_date
        )
        self.quick_load_btn.grid(row=0, column=3, rowspan=2, sticky="e")

        # INFO CARDS
        self.info_cards = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.info_cards.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        self.info_cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_date = self.create_stat_card(self.info_cards, "Data", "—")
        self.card_date.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_type = self.create_stat_card(self.info_cards, "Tipo", "—")
        self.card_type.grid(row=0, column=1, padx=8, sticky="ew")

        self.card_copyright = self.create_stat_card(self.info_cards, "Copyright", "—")
        self.card_copyright.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # CONTENT GRID
        self.content = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.content.grid_columnconfigure(0, weight=3)
        self.content.grid_columnconfigure(1, weight=2)
        self.content.grid_rowconfigure(0, weight=1)

        # LEFT: IMAGE PANEL
        self.image_panel = ctk.CTkFrame(self.content, corner_radius=24, fg_color="#11151F")
        self.image_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.image_title = ctk.CTkLabel(
            self.image_panel,
            text="Título: —",
            anchor="w",
            justify="left",
            wraplength=760,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.image_title.pack(fill="x", padx=20, pady=(20, 10))

        self.image_container = ctk.CTkFrame(
            self.image_panel,
            corner_radius=20,
            fg_color="#0B0F18"
        )
        self.image_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.image_label = ctk.CTkLabel(
            self.image_container,
            text="Carrega o conteúdo para começar.",
            text_color="#7F8A9E",
            font=ctk.CTkFont(size=18)
        )
        self.image_label.pack(fill="both", expand=True, padx=12, pady=12)

        # RIGHT: DESCRIPTION PANEL
        self.desc_panel = ctk.CTkFrame(self.content, corner_radius=24, fg_color="#11151F")
        self.desc_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.desc_panel.grid_rowconfigure(1, weight=1)
        self.desc_panel.grid_columnconfigure(0, weight=1)

        self.desc_title = ctk.CTkLabel(
            self.desc_panel,
            text="Descrição",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.desc_title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        self.description_text = ctk.CTkTextbox(
            self.desc_panel,
            corner_radius=18,
            font=ctk.CTkFont(size=14),
            wrap="word",
            fg_color="#0B0F18"
        )
        self.description_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.description_text.insert("1.0", "A descrição aparece aqui.")
        self.description_text.configure(state="disabled")

        # STATUS
        self.status_frame = ctk.CTkFrame(self.main_area, height=48, corner_radius=18, fg_color="#101521")
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Pronto.",
            text_color="#8FDCB0",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.pack(anchor="w", padx=16, pady=12)

    def create_stat_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color="#11151F")

        title_label = ctk.CTkLabel(
            card,
            text=title,
            text_color="#7F8A9E",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(anchor="w", padx=16, pady=(14, 4))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            anchor="w",
            justify="left",
            wraplength=280,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        value_label.pack(anchor="w", padx=16, pady=(0, 14))

        card.value_label = value_label
        return card

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
        image.thumbnail((820, 520))

        self.current_ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )
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

        self.image_title.configure(text=f"Título: {title}")
        self.card_date.value_label.configure(text=date)
        self.card_type.value_label.configure(text=media_type)
        self.card_copyright.value_label.configure(text=copyright_text)
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
            self.clear_image("Este conteúdo é um vídeo. Usa “Abrir vídeo”.")
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
    app = NasaPremiumApp()
    app.mainloop()