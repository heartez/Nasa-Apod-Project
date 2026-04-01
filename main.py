import os
import webbrowser
import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk

API_KEY = "DEMO_KEY"
BASE_URL = "https://api.nasa.gov/planetary/apod"
DOWNLOADS_FOLDER = "downloads"


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


class NasaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA APOD Viewer")
        self.root.geometry("1100x820")
        self.root.minsize(980, 720)
        self.root.configure(bg="#0b1020")

        os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

        self.current_image = None
        self.current_media_url = None
        self.current_media_type = None

        self.bg_main = "#0b1020"
        self.bg_card = "#121a30"
        self.bg_input = "#1a2440"
        self.fg_main = "#f3f7ff"
        self.fg_soft = "#b8c4e0"
        self.accent = "#4da3ff"
        self.success = "#74d99f"

        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self.root, bg=self.bg_main)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title_label = tk.Label(
            header,
            text="NASA Astronomy Picture of the Day",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_main,
            fg=self.fg_main
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header,
            text="Explora imagens astronómicas, descrições e vídeos da NASA numa app com interface gráfica.",
            font=("Segoe UI", 10),
            bg=self.bg_main,
            fg=self.fg_soft
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

        control_card = tk.Frame(self.root, bg=self.bg_card, bd=0, highlightthickness=1, highlightbackground="#263252")
        control_card.pack(fill="x", padx=20, pady=10)

        control_top = tk.Frame(control_card, bg=self.bg_card)
        control_top.pack(fill="x", padx=16, pady=16)

        date_label = tk.Label(
            control_top,
            text="Data",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_card,
            fg=self.fg_main
        )
        date_label.pack(side="left", padx=(0, 8))

        self.date_entry = tk.Entry(
            control_top,
            font=("Consolas", 12),
            width=14,
            bg=self.bg_input,
            fg=self.fg_main,
            insertbackground=self.fg_main,
            relief="flat",
            bd=8
        )
        self.date_entry.pack(side="left", padx=(0, 10))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        hint_label = tk.Label(
            control_top,
            text="Formato: AAAA-MM-DD",
            font=("Segoe UI", 10),
            bg=self.bg_card,
            fg=self.fg_soft
        )
        hint_label.pack(side="left", padx=(0, 20))

        self.today_button = self.create_button(control_top, "Hoje", self.load_today, self.accent, "white")
        self.today_button.pack(side="left", padx=6)

        self.date_button = self.create_button(control_top, "Escolher data", self.load_selected_date, self.accent, "white")
        self.date_button.pack(side="left", padx=6)

        self.video_button = self.create_button(control_top, "Abrir vídeo", self.open_media_in_browser, "#2a3556", self.fg_main)
        self.video_button.pack(side="left", padx=6)

        self.save_button = self.create_button(control_top, "Guardar de novo", self.save_current_info_again, "#2a3556", self.fg_main)
        self.save_button.pack(side="left", padx=6)

        self.exit_button = self.create_button(control_top, "Sair", self.root.quit, "#8b2d3b", "white")
        self.exit_button.pack(side="right", padx=6)

        content = tk.Frame(self.root, bg=self.bg_main)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        left_panel = tk.Frame(content, bg=self.bg_main)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_panel = tk.Frame(content, bg=self.bg_main)
        right_panel.pack(side="right", fill="y", padx=(10, 0))

        info_card = tk.Frame(left_panel, bg=self.bg_card, highlightthickness=1, highlightbackground="#263252")
        info_card.pack(fill="x", pady=(0, 10))

        self.title_value = tk.Label(
            info_card,
            text="Título: —",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_card,
            fg=self.fg_main,
            wraplength=700,
            justify="left"
        )
        self.title_value.pack(anchor="w", padx=16, pady=(16, 10))

        meta_frame = tk.Frame(info_card, bg=self.bg_card)
        meta_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.date_value = tk.Label(
            meta_frame,
            text="Data: —",
            font=("Segoe UI", 11),
            bg=self.bg_card,
            fg=self.fg_soft
        )
        self.date_value.pack(anchor="w", pady=2)

        self.media_value = tk.Label(
            meta_frame,
            text="Tipo: —",
            font=("Segoe UI", 11),
            bg=self.bg_card,
            fg=self.fg_soft
        )
        self.media_value.pack(anchor="w", pady=2)

        self.copyright_value = tk.Label(
            meta_frame,
            text="Copyright: —",
            font=("Segoe UI", 11),
            bg=self.bg_card,
            fg=self.fg_soft,
            wraplength=700,
            justify="left"
        )
        self.copyright_value.pack(anchor="w", pady=2)

        image_card = tk.Frame(left_panel, bg=self.bg_card, highlightthickness=1, highlightbackground="#263252")
        image_card.pack(fill="both", expand=True)

        image_header = tk.Label(
            image_card,
            text="Imagem / Media",
            font=("Segoe UI", 13, "bold"),
            bg=self.bg_card,
            fg=self.fg_main
        )
        image_header.pack(anchor="w", padx=16, pady=(16, 10))

        self.image_container = tk.Frame(image_card, bg="#0f1730")
        self.image_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.image_label = tk.Label(
            self.image_container,
            bg="#0f1730",
            fg=self.fg_soft,
            font=("Segoe UI", 12),
            text="Carrega em “Hoje” ou escolhe uma data para começar."
        )
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

        description_card = tk.Frame(right_panel, bg=self.bg_card, highlightthickness=1, highlightbackground="#263252")
        description_card.pack(fill="both", expand=True)

        description_header = tk.Label(
            description_card,
            text="Descrição",
            font=("Segoe UI", 13, "bold"),
            bg=self.bg_card,
            fg=self.fg_main
        )
        description_header.pack(anchor="w", padx=16, pady=(16, 10))

        text_frame = tk.Frame(description_card, bg=self.bg_card)
        text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.description_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 11),
            width=34,
            height=28,
            bg=self.bg_input,
            fg=self.fg_main,
            insertbackground=self.fg_main,
            relief="flat",
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set
        )
        self.description_text.pack(side="left", fill="both", expand=True)
        self.description_text.config(state="disabled")

        scrollbar.config(command=self.description_text.yview)

        self.status_var = tk.StringVar()
        self.status_var.set("Pronto.")

        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            font=("Segoe UI", 10),
            bg="#08101f",
            fg=self.success,
            padx=12,
            pady=8
        )
        status_bar.pack(fill="x", side="bottom")

    def create_button(self, parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )

    def set_status(self, message):
        self.status_var.set(message)

    def set_description(self, text):
        self.description_text.config(state="normal")
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state="disabled")

    def clear_image(self, message="Sem imagem para mostrar."):
        self.image_label.config(image="", text=message)
        self.current_image = None

    def show_image(self, image_path):
        image = Image.open(image_path)

        max_width = 680
        max_height = 420

        image.thumbnail((max_width, max_height))

        self.current_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.current_image, text="")

    def update_ui_with_data(self, data):
        title = data["title"]
        date = data["date"]
        explanation = data["explanation"]
        media_type = data["media_type"]
        media_url = data["url"]
        copyright_text = data.get("copyright", "Não disponível")

        self.current_media_url = media_url
        self.current_media_type = media_type

        self.title_value.config(text=f"Título: {title}")
        self.date_value.config(text=f"Data: {date}")
        self.media_value.config(text=f"Tipo: {media_type}")
        self.copyright_value.config(text=f"Copyright: {copyright_text}")
        self.set_description(explanation)

        text_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{date}.txt")
        save_text_file(text_path, title, date, explanation, media_type, media_url, copyright_text)

        if media_type == "image":
            image_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{date}.jpg")
            download_file(media_url, image_path)
            self.show_image(image_path)
            self.set_status(f"Imagem e descrição guardadas em '{DOWNLOADS_FOLDER}'.")
        else:
            self.clear_image("Este conteúdo é um vídeo. Usa o botão “Abrir vídeo”.")
            self.set_status(f"Vídeo e descrição carregados. Descrição guardada em '{DOWNLOADS_FOLDER}'.")

    def load_today(self):
        try:
            self.set_status("A carregar conteúdo de hoje...")
            self.root.update_idletasks()

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
            self.root.update_idletasks()

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
        if not self.date_value.cget("text").startswith("Data: ") or self.date_value.cget("text") == "Data: —":
            messagebox.showinfo("Sem conteúdo", "Ainda não carregaste nenhum conteúdo.")
            return

        current_date = self.date_value.cget("text").replace("Data: ", "").strip()
        current_title = self.title_value.cget("text").replace("Título: ", "").strip()
        current_media_type = self.media_value.cget("text").replace("Tipo: ", "").strip()
        current_copyright = self.copyright_value.cget("text").replace("Copyright: ", "").strip()
        current_description = self.description_text.get("1.0", tk.END).strip()
        current_url = self.current_media_url or ""

        text_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{current_date}.txt")
        save_text_file(
            text_path,
            current_title,
            current_date,
            current_description,
            current_media_type,
            current_url,
            current_copyright
        )

        if self.current_media_type == "image" and self.current_media_url:
            image_path = os.path.join(DOWNLOADS_FOLDER, f"apod_{current_date}.jpg")
            if not os.path.exists(image_path):
                download_file(self.current_media_url, image_path)

        messagebox.showinfo("Guardado", f"Os ficheiros foram guardados em '{DOWNLOADS_FOLDER}'.")
        self.set_status("Conteúdo guardado novamente com sucesso.")


if __name__ == "__main__":
    root = tk.Tk()
    app = NasaApp(root)
    root.mainloop()