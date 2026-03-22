
import os
import time
import asyncio
from dataclasses import dataclass
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ✅ SEU TOKEN JÁ ESTÁ AQUI
TOKEN = "8792963382:AAF2rxy7oZw0f6cYT2Lg2xP0aznAUTL7JE4"

@dataclass
class Estado:
    ultimo: str = None
    contagem: int = 0
    greens: int = 0
    hora_inicio: str = None

class Bot32RedAuto:
    def __init__(self):
        self.estado = Estado()
        self.driver = None
        self.ativo = False
        self.task = None
        self.context = None
        self.chat_id = None
    
    async def iniciar_navegador(self) -> bool:
        """Abre 32Red no Chrome headless"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            
            # ChromeDriver automático
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            print("[LOG] Chrome iniciado com sucesso")
            
            # Tenta múltiplas URLs da 32Red
            urls = [
                "https://www.32red.com/casino/roulette",
                "https://www.32red.com/live-casino/roulette",
                "https://www.32red.com/play/32red-auto-roulette",
                "https://www.32red.com/live/roulette"
            ]
            
            for url in urls:
                try:
                    print(f"[LOG] Tentando URL: {url}")
                    self.driver.get(url)
                    await asyncio.sleep(5)
                    
                    # Verifica se encontrou a roleta
                    selectors = [
                        ".last-result",
                        ".recent-result",
                        ".roulette-history li:last-child",
                        ".result:last-child",
                        "[class*='history'] li:last-child",
                        "[class*='number']:last-child",
                        ".spin-result",
                        ".last-spin"
                    ]
                    
                    for selector in selectors:
                        try:
                            elemento = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            print(f"[✓] Roleta encontrada em {url}")
                            self.ativo = True
                            self.estado.hora_inicio = datetime.now().strftime("%H:%M:%S")
                            return True
                        except Exception:
                            continue
                except Exception as e:
                    print(f"[✗] Falha em {url}: {e}")
                    continue
            
            print("[✗] Nenhuma roleta encontrada")
            return False
            
        except Exception as e:
            print(f"[✗] Erro ao iniciar navegador: {e}")
            return False
    
    async def ler_numero(self):
        """Extrai último número da roleta"""
        if not self.driver:
            return None
        
        selectors = [
            ".last-result",
            ".recent-result",
            ".roulette-history li:last-child",
            ".result:last-child",
            "[class*='history'] li:last-child",
            "[class*='number']:last-child",
            ".spin-result",
            ".last-spin"
        ]
        
        for selector in selectors:
            try:
                elemento = self.driver.find_element(By.CSS_SELECTOR, selector)
                texto = elemento.text.strip()
                
                if texto.isdigit() and 0 <= int(texto) <= 36:
                    return int(texto)
            except Exception:
                continue
        
        return None
    
    async def loop_analise(self):
        """Loop principal - monitora 24/7"""
        print("[▶️] Bot 32Red AUTO iniciado!")
        
        while self.ativo:
            try:
                numero = await self.ler_numero()
                
                if numero is not None:
                    await self.processar_numero(numero)
                
                # Espera 25 segundos entre leituras
                await asyncio.sleep(25)
                
            except Exception as e:
                print(f"[✗] Erro no loop: {e}")
                await asyncio.sleep(10)
    
    async def processar_numero(self, numero: int):
        """Analisa sequência e gera sinal"""
        numero_str = str(numero)
        
        if self.estado.ultimo != numero_str:
            self.estado.contagem += 1
        else:
            self.estado.contagem = 1
        
        # A CADA 10 NÚMEROS IGUAIS = SINAL
        if self.estado.contagem == 10:
            self.estado.greens += 1
            sinal = (
                f"🟢 **SINAL GREEN!** 🟢\n"
                f"Número: {numero}\n"
                f"Sequência: {self.estado.contagem}x\n"
                f"GREENs no dia: {self.estado.greens}"
            )
            print(f"[🟢] {sinal}")
            
            # Envia para Telegram
            if self.context and self.chat_id:
                await self.enviar_sinal(sinal)
        
        self.estado.ultimo = numero_str
        self.estado.contagem = 1
    
    async def enviar_sinal(self, mensagem: str):
        """Envia sinal para o Telegram"""
        try:
            if self.context and self.chat_id:
                await self.context.bot.send_message(
                    chat_id=self.chat_id,
                    text=mensagem,
                    parse_mode="Markdown"
                )
                print(f"[✓] Sinal enviado para Telegram!")
        except Exception as e:
            print(f"[✗] Erro ao enviar sinal: {e}")
    
    def parar(self):
        """Para o bot"""
        self.ativo = False
        if self.driver:
            self.driver.quit()
        print("[⏹️] Bot parado")

# Instância global
botauto = Bot32RedAuto()

# ==================== COMANDOS TELEGRAM ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    botauto.chat_id = update.effective_chat.id
    botauto.context = context
    
    msg = (
        "🤖 **Bot 32Red AUTOMÁTICO v2.0**\n\n"
        "**Comandos disponíveis:**\n"
        "/iniciar - Liga scraper 24/7\n"
        "/status - Ver status do bot\n"
        "/parar - Desligar bot\n"
        "/greens - Ver GREENs do dia\n\n"
        "⚡ Bot pronto para uso!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    print(f"[✓] Chat autorizado: {botauto.chat_id}")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /iniciar"""
    if botauto.ativo:
        await update.message.reply_text("❌ Bot já está ativo!")
        return
    
    await update.message.reply_text(
        "⏳ Iniciando scraper 32Red...\n"
        "(Isto pode levar até 30 segundos)"
    )
    
    try:
        sucesso = await botauto.iniciar_navegador()
        
        if sucesso:
            botauto.ativo = True
            # Inicia o loop de análise
            asyncio.create_task(botauto.loop_analise())
            
            await update.message.reply_text(
                "✅ **BOT LIGADO!**\n"
                "🔍 Monitorando 32Red 24/7\n"
                f"⏱️ Início: {botauto.estado.hora_inicio}\n\n"
                "Use /status para ver atualizações",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ Não consegui acessar 32Red.\n"
                "Tente novamente em alguns segundos."
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    if botauto.ativo:
        msg = (
            f"✅ **STATUS: ATIVO**\n\n"
            f"Último número: {botauto.estado.ultimo or 'Aguardando...'}\n"
            f"Sequência atual: {botauto.estado.contagem}x\n"
            f"🟢 GREENs hoje: {botauto.estado.greens}\n"
            f"Rodando desde: {botauto.estado.hora_inicio}"
        )
    else:
        msg = "❌ **STATUS: DESLIGADO**\nUse /iniciar para ligar"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def greens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /greens"""
    await update.message.reply_text(
        f"🟢 **GREENs do dia: {botauto.estado.greens}**",
        parse_mode="Markdown"
    )

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /parar"""
    botauto.parar()
    await update.message.reply_text(
        "⏹️ **Bot parado com sucesso**",
        parse_mode="Markdown"
    )

# ==================== MAIN ====================

def main():
    if not TOKEN:
        raise RuntimeError("❌ TOKEN NÃO DEFINIDO!")
    
    print(f"[✓] Token carregado: {TOKEN[:20]}...")
    
    # Cria aplicação
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Adiciona handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iniciar", iniciar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("greens", greens))
    app.add_handler(CommandHandler("parar", parar))
    
    print("[✓] Bot carregado. Aguardando comandos...")
    print("[✓] Telegram conectado e pronto!")
    
    # Inicia polling
    app.run_polling()

if __name__ == "__main__":
    main()
