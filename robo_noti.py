import time
import os
import pyperclip
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# --- CONFIGURAÇÃO SELENIUM ---
driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
driver.get("https://web.whatsapp.com/")

print("Escaneie o QR code do WhatsApp Web e pressione Enter aqui...")
input()

# --- LER LEGENDA DO ARQUIVO ---
with open("legenda.txt", "r", encoding="utf-8") as f:
    legenda = f.read()

# --- PEGAR LISTA DE NÚMEROS DA API ---
url_api = "https://bolaplaytv.com.br/api/jogo-comprado-usuario/false"
response = requests.get(url_api)
data = response.json()

usuarios = data.get("usuarios", [])
print(f"Total de usuários recebidos: {len(usuarios)}")

# Remover duplicados (usando set)
numeros = []
for u in usuarios:
    numero = u.get("celular", "").strip()
    if numero not in numeros and numero.isdigit():
        numeros.append(numero)

print(f"Números únicos válidos para envio: {len(numeros)}")

# --- IMAGEM A ENVIAR ---
imagem = os.path.join(os.getcwd(), "imagem.jpeg")

# --- LOOP DE ENVIO ---
for telefone in numeros:
    print(f"\n➡️ Enviando para: {telefone}")
    url = f"https://web.whatsapp.com/send?phone={telefone}"
    driver.get(url)
    time.sleep(10)  # espera carregar o chat

    # Verifica se número é inválido
    try:
        erro = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/span[2]/div/span/div/div/div/div/div/div[1]')
        if erro.is_displayed():
            print(f"❌ Número inválido ou não possui WhatsApp: {telefone}")
            # Fecha modal
            botao_ok = driver.find_element(By.XPATH, '//button[.//div[text()="OK"]]')
            botao_ok.click()
            time.sleep(2)
            continue
    except:
        pass  # segue se não achou erro

    try:
        # 1️⃣ Clicar no botão de clipe
        anexar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/button'))
        )
        anexar.click()
        time.sleep(2)

        # 2️⃣ Selecionar input de imagem
        input_file = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
        )
        input_file.send_keys(imagem)
        time.sleep(3)

        # 3️⃣ Inserir legenda
        campo_legenda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@aria-label="Adicione uma legenda" and @contenteditable="true"]')
            )
        )
        pyperclip.copy(legenda)

        actions = ActionChains(driver)
        actions.move_to_element(campo_legenda)
        actions.click()
        time.sleep(2)
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
        actions.send_keys(Keys.ENTER)
        time.sleep(7)
        actions.perform()

        print(f"✅ Mensagem enviada para {telefone}")
        time.sleep(5)

    except Exception as e:
        print(f"⚠️ Falha ao enviar para {telefone}: {e}")

print("\n🚀 Processo finalizado!")
driver.quit()
