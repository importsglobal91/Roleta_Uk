cat > Roleta_Uk.py << 'EOF'
import os
import time
import asyncio
from dataclasses import dataclass
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes
)
import requests
import random

# 🔑 SEU TOKEN
TOKEN = "8792963382:AAF2rxy7oZw0f6cYT2Lg2xP0aznAUTL7JE4"

@dataclass
class Estado:
    ultimo: str = None
    contagem: int = 0
    greens: int = 0
    hora_inicio: str = None
    rodadas: int = 0

class Bot32RedAuto:
    def __init__(self):
        self.estado = Estado()
        self.ativo = False
        self.context = None
        self.chat_id = None
        self.loop_task = None
    
    async def iniciar_monitoramento(self) -> bool:
        """Inicia monitoramento simulado"""
        try:
            print("[LOG] Iniciando monitoramento...")
            self.estado.hora_inicio = datetime.now().strftime("%H:%M:%S")
            print(f"[✓] Monitoramento iniciado às {self.estado.hora_inicio}")
            self.ativo = True
            return True
        except Exception as e:
            print(f"[✗] Erro: {e}")
            return False
    
    async def gerar_numero(self):
        """Simula números da roleta (0-36)"""
        numero = random.randint(0, 36)
        return numero
    
    async def loop_analise(self):
        """Loop principal - monitora números"""
        print("[▶️] Loop de análise iniciado!")
        
        while self.ativo:
            try:
                numero = await self.gerar_numero()
                
                if numero is not None:
                    await self.processar_numero(numero)
                    self.estado.rodadas += 1
                
                await asyncio.sleep(25)
                
            except Exception as e:
                print(f"[✗] Erro no loop: {e}")
                await asyncio.sleep(10)
    
    async def processar_numero(self, numero: int):
        """Processa número e detecta sequências"""
        numero_str = str(numero)
        
        if self.estado.ultimo != numero_str:
            self.estado.contagem = 1
            self.estado.ultimo = numero_str
        else:
            self.estado.contagem += 1
        
        print(f"[📊] Número: {numero} | Sequência: {self.estado.contagem}x | Rodadas: {self.estado.rodadas}")
        
        if self.estado.contagem == 10:
            self.estado.greens += 1
            sinal = (
                f"🟢 **SINAL GREEN!** 🟢\n\n"
                f"📍 Número: {numero}\n"
                f"📊 Sequência: {self.estado.contagem}x IGUAIS\n"
                f"🟢 Total GREENs: {self.estado.greens}\n"
                f"🎯 Rodadas analisadas: {self.estado.rodadas}"
            )
            print(f"\n{'='*50}")
            print(f"🟢 SINAL DETECTADO!")
            print(f"{'='*50}\n")
            
            if self.context and self.chat_id:
                await self.enviar_sinal(sinal)
            
            self.estado.contagem = 0
    
    async def enviar_sinal(self, mensagem: str):
        """Envia sinal para Telegram"""
        try:
            await self.context.bot.send_message(
                chat_id=self.chat_id,
                text=mensagem,
                parse_mode="Markdown"
            )
            print("[✓] Sinal enviado ao Telegram com sucesso!")
        except Exception as e:
            print(f"[✗] Erro ao enviar sinal: {e}")
    
    def parar(self):
        """Para o bot"""
        self.ativo = False
        print("[⏹️] Bot parado")

botauto = Bot32RedAuto()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    botauto.chat_id = update.effective_chat.id
    botauto.context = context
    
    msg = (
        "🤖 **Bot 32Red AUTOMÁTICO v3.0**\n\n"
        "**Comandos:**\n"
        "/iniciar - Ligar monitoramento 24/7\n"
        "/status - Ver status em tempo real\n"
        "/parar - Desligar bot\n"
        "/greens - Ver total de GREENs\n\n"
        "✅ Bot pronto para usar!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    print(f"[✓] Chat autorizado: {botauto.chat_id}")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /iniciar"""
    if botauto.ativo:
        await update.message.reply_text("❌ Bot já está ativo!")
        return
    
    await update.message.reply_text("⏳ Iniciando monitoramento 24/7...")
    
    try:
        sucesso = await botauto.iniciar_monitoramento()
        
        if sucesso:
            botauto.loop_task = asyncio.create_task(botauto.loop_analise())
            
            await update.message.reply_text(
                "✅ **BOT LIGADO!**\n\n"
                "🔍 Monitorando números da roleta\n"
                f"⏱️ Início: {botauto.estado.hora_inicio}\n"
                "📊 Analisando sequências...\n\n"
                "Use /status para atualizações",
                parse_mode="Markdown"
            )
            print("[✓] Bot inicializado com sucesso!")
        else:
            await update.message.reply_text("❌ Erro ao iniciar bot")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        print(f"[✗] Erro: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    if botauto.ativo:
        msg = (
            f"✅ **STATUS: ATIVO**\n\n"
            f"📍 Último número: {botauto.estado.ultimo or 'Aguardando...'}\n"
            f"📊 Sequência atual: {botauto.estado.contagem}x\n"
            f"🟢 **GREENs detectados: {botauto.estado.greens}**\n"
            f"🎯 Rodadas analisadas: {botauto.estado.rodadas}\n"
            f"⏱️ Rodando desde: {botauto.estado.hora_inicio}"
        )
    else:
        msg = (
            "❌ **STATUS: DESLIGADO**\n\n"
            "Use /iniciar para ligar o bot"
        )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def greens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /greens"""
    await update.message.reply_text(
        f"🟢 **GREENs detectados hoje: {botauto.estado.greens}**\n\n"
        f"Rodadas analisadas: {botauto.estado.rodadas}",
        parse_mode="Markdown"
    )

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /parar"""
    botauto.parar()
    await update.message.reply_text(
        "⏹️ **Bot parado com sucesso**\n\n"
        f"📊 Resumo:\n"
        f"🟢 GREENs: {botauto.estado.greens}\n"
        f"🎯 Rodadas: {botauto.estado.rodadas}",
        parse_mode="Markdown"
    )

def main():
    print("\n" + "="*60)
    print("🤖 BOT 32RED AUTOMÁTICO v3.0")
    print("="*60)
    print(f"[✓] Token carregado: 8792963382:AAF2...JE4")
    print(f"[✓] Inicializando Telegram Bot...")
    print("="*60 + "\n")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iniciar", iniciar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("greens", greens))
    app.add_handler(CommandHandler("parar", parar))
    
    print("[✓] Handlers carregados")
    print("[✓] Bot aguardando comandos do Telegram...\n")
    
    app.run_polling()

if __name__ == "__main__":
    main()
EOF
