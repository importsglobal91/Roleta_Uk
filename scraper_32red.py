from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
from telegram import Bot

TOKEN = "SEU_TOKEN_AQUI"  # Cole o do @Zanuto_bot
CHAT_ID = "1891963199"  # Seu chat ID do memory
bot = Bot(token=TOKEN)

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Acesse 32Red Live Roulette (login se precisar)
driver.get("https://www.32red.com/casino/live-casino")  # Mude pra mesa específica após login [web:52]
time.sleep(5)

while True:
    try:
        # Procure elemento com último número (ajuste selector após inspecionar)
        numero_elem = driver.find_element(By.CSS_SELECTOR, ".roulette_round_result-position__text")  # Exemplo [web:50]
        numero = numero_elem.text.strip()
        print(f"Número real: {numero}")
        
        # Envie pro Telegram
        bot.send_message(chat_id=CHAT_ID, text=f"🔴 Número 32Red: {numero}")
        
        time.sleep(30)  # Checa a cada 30s
    except:
        print("Aguardando...")
        time.sleep(10)

driver.quit()

