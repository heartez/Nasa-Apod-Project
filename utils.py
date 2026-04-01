from datetime import datetime


def validar_data(data_str):
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")

        if data.date() > datetime.now().date():
            return False, "Não podes escolher uma data no futuro."

        return True, ""

    except ValueError:
        return False, "Formato inválido. Usa AAAA-MM-DD (ex: 2024-01-15)."