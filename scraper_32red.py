
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

print("🚀 Iniciando scraper 32Red...")

options = Options()
# options.add_argument("--headless")  # Descomente depois
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.32red.com/casino/live-casino")
print("✅ Abra login/mesa. Quando pronto, aperte Ctrl+C pra parar.")

try:
    while True:
        time.sleep(5)
        print("🔍 Procurando números...")
        # Testa múltiplos selectors
        selectors = [
            ".roulette_history-item:last-child",
            ".result-item:last-child", 
            ".ball:last-child",
            ".number-result"
        ]
        numero = "Nenhum"
        for sel in selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    texto = elems[-1].text.strip()
                    print(f"Selector {sel}: '{texto}'")
                    if texto.isdigit():
                        numero = texto
            except:
                pass
        print(f"Último número: {numero}\\n")
except KeyboardInterrupt:
    print("⏹️ Parado!")
finally:
    driver.quit()
