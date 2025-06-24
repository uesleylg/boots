import telebot
import requests, re
from bs4 import BeautifulSoup
from datetime import datetime

def identificar_bicho(numero):
    tabela_bichos = {
        1: "Avestruz",
        2: "Águia",
        3: "Burro",
        4: "Borboleta",
        5: "Cachorro",
        6: "Cabra",
        7: "Carneiro",
        8: "Camelo",
        9: "Cobra",
        10: "Coelho",
        11: "Cavalo",
        12: "Elefante",
        13: "Galo",
        14: "Gato",
        15: "Jacaré",
        16: "Leão",
        17: "Macaco",
        18: "Porco",
        19: "Pavão",
        20: "Peru",
        21: "Touro",
        22: "Tigre",
        23: "Urso",
        24: "Veado",
        25: "Vaca"
    }
    return tabela_bichos.get(numero, "Número inválido")

def buscar_bicho_data_atual():
    # Data atual
    data_atual = datetime.now()

    # Usando a data de hoje
    data_str = data_atual.strftime("%Y-%m-%d")
    url = f"https://www.meujogodobicho.com.br/paginas/quadrante/acao/refresh/id_pagina/14/id_jogo/23/data/{data_str}/link/rj/"

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        elemento = soup.select_one("div.resultados ul li div.bicho > p")
        
        if elemento is None or not elemento.text.strip():
            return f"{data_str}: sem registro."
        else:
            texto = elemento.text
            bicho_id = re.search(r"\((\d+)\)", texto)
            
            if not bicho_id:
                return f"{data_str}: padrão não encontrado."
            else:
                bicho_id = bicho_id.group(1)
                return f" {bicho_id}"

    except Exception as e:
        return f"{data_str}: erro - {e}"

# Chamada da função e captura do retorno
resultado = buscar_bicho_data_atual()






bot_token = '7751775989:AAFsa5CfnoVayQE8PCtqDrIGqTwiVGY1eUQ'
bot = telebot.TeleBot(bot_token)

# Enviar uma mensagem para o grupo com o chat_id fornecido
chat_id = -1002503777550  # Substitua pelo seu chat_id

# Envia a mensagem para o grupo
bot.send_message(chat_id, f" 📍 RIO DE JANEIRO\n📆 30/12/2024\n\n📌 RJ-21:20\n1º - Bicho hoje: {identificar_bicho(int(resultado))} ")

# Iniciar o polling para que o bot continue ativo
bot.polling()
