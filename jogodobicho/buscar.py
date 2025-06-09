import requests, re, csv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Data inicial
base_data = datetime.strptime("2025-06-07", "%Y-%m-%d")

with open("bicho.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["data", "bicho_id"])  # Cabeçalho

    dia_atual = base_data
    while True:
        data_str = dia_atual.strftime("%Y-%m-%d")
        url = f"https://www.meujogodobicho.com.br/paginas/quadrante/acao/refresh/id_pagina/14/id_jogo/23/data/{data_str}/link/rj/"

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            elemento = soup.select_one("div.resultados ul li div.bicho > p")
            
            if elemento is None or not elemento.text.strip():
                print(f"{data_str}: sem registro, parando.")
                break  # Para porque não tem registro

            texto = elemento.text
            bicho_id = re.search(r"\((\d+)\)", texto)
            
            if not bicho_id:
                print(f"{data_str}: padrão não encontrado, parando.")
                break

            bicho_id = bicho_id.group(1)
            writer.writerow([data_str, int(bicho_id)])
            print(f"{data_str}: {bicho_id}")
        except Exception as e:
            print(f"{data_str}: erro - {e}")
            break

        dia_atual -= timedelta(days=1)
