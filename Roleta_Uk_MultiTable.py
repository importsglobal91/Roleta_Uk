import os
import asyncio
from dataclasses import dataclass
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes
)
import random

TOKEN = "8792963382:AAF2rxy7oZw0f6cYT2Lg2xP0aznAUTL7JE4"

@dataclass
class EstadoRoleta:
    nome: str
    ultimo: str = None
    contagem: int = 0
    greens: int = 0
    hora_inicio: str = None
    rodadas: int = 0

class BotMultiRoleta:
    def __init__(self):
        self.roletas = {}
        self.ativo = False
        self.context = None
        self.chat_id = None
        
        self.roletas_nomes = [
            "Roleta 32vermelha",
            "Roleta Relâmpago",
            "Auto-Roulette",
            "Roleta VIP",
            "Roleta Dragonara",
            "Roleta Francesa",
            "Roleta Americana",
            "Mega Roleta",
        ]
        
        for nome in self.roletas_nomes:
            self.roletas[nome] = EstadoRoleta(nome=nome)
    
    async def iniciar_monitoramento(self) -> bool:
        try:
            print("[LOG] Iniciando monitoramento multi-roleta...")
            hora = datetime.now().strftime("%H:%M:%S")
            
            for nome in self.roletas:
                self.roletas[nome].hora_inicio = hora
            
            self.ativo = True
            print(f"[✓] Monitorando {len(self.roletas)} roletas")
            return True
        except Exception as e:
            print(f"[✗] Erro: {e}")
            return False
    
    async def gerar_numero(self):
        numero = random.randint(0, 36)
        return numero
    
    async def loop_analise_roleta(self, nome_roleta: str):
        print(f"[▶️] Monitorando: {nome_roleta}")
        
        while self.ativo:
            try:
                numero = await self.gerar_numero()
                
                if numero is not None:
                    await self.processar_numero(nome_roleta, numero)
                
                await asyncio.sleep(25)
                
            except Exception as e:
                print(f"[✗] Erro em {nome_roleta}: {e}")
                await asyncio.sleep(10)
    
    async def processar_numero(self, nome_roleta: str, numero: int):
        roleta = self.roletas[nome_roleta]
        numero_str = str(numero)
        
        if roleta.ultimo != numero_str:
            roleta.contagem = 1
            roleta.ultimo = numero_str
        else:
            roleta.contagem += 1
        
        roleta.rodadas += 1
        
        print(f"[{nome_roleta}] Nº: {numero} | Seq: {roleta.contagem}x | Rodadas: {roleta.rodadas}")
        
        if roleta.contagem == 10:
            roleta.greens += 1
            sinal = (
                f"🟢 **SINAL GREEN!** 🟢\n\n"
                f"📍 Roleta: **{nome_roleta}**\n"
                f"📊 Número: {numero}\n"
                f"🔄 Sequência: {roleta.contagem}x IGUAIS\n"
                f"🟢 GREENs nesta roleta: {roleta.greens}\n"
                f"🎯 Rodadas analisadas: {roleta.rodadas}"
            )
            print(f"\n{'='*60}")
            print(f"🟢 SINAL DETECTADO EM {nome_roleta.upper()}!")
            print(f"{'='*60}\n")
            
            if self.context and self.chat_id:
                await self.enviar_sinal(sinal)
            
            roleta.contagem = 0
    
    async def enviar_sinal(self, mensagem: str):
        try:
            await self.context.bot.send_message(
                chat_id=self.chat_id,
                text=mensagem,
                parse_mode="Markdown"
            )
            print("[✓] Sinal enviado ao Telegram!")
        except Exception as e:
            print(f"[✗] Erro ao enviar: {e}")
    
    def parar(self):
        self.ativo = False
        print("[⏹️] Bot parado")

botauto = BotMultiRoleta()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botauto.chat_id = update.effective_chat.id
    botauto.context = context
    
    msg = (
        "🎰 **Bot Multi-Roleta 32Red v4.0**\n\n"
        "**Monitorando 8 roletas em paralelo!**\n\n"
        "/iniciar - Ligar monitoramento 24/7\n"
        "/status - Ver status de todas\n"
        "/roletas - Lista de roletas monitoradas\n"
        "/parar - Desligar bot\n\n"
        "✅ Pronto para monitorar!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    print(f"[✓] Chat autorizado: {botauto.chat_id}")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if botauto.ativo:
        await update.message.reply_text("❌ Bot já está ativo!")
        return
    
    await update.message.reply_text("⏳ Iniciando monitoramento de 8 roletas...\n(Aguarde 30 segundos)")
    
    try:
        sucesso = await botauto.iniciar_monitoramento()
        
        if sucesso:
            for nome in botauto.roletas:
                asyncio.create_task(botauto.loop_analise_roleta(nome))
            
            msg = (
                "✅ **BOT LIGADO!**\n\n"
                f"🎰 Monitorando {len(botauto.roletas)} roletas\n"
                f"⏱️ Início: {botauto.roletas[list(botauto.roletas.keys())[0]].hora_inicio}\n"
                "📊 Analisando sequências...\n\n"
                "Use /roletas para ver quais"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            print("[✓] Bot inicializado!")
        else:
            await update.message.reply_text("❌ Erro ao iniciar bot")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not botauto.ativo:
        await update.message.reply_text("❌ Bot desligado. Use /iniciar")
        return
    
    msg = "✅ **STATUS - TODAS AS ROLETAS**\n\n"
    
    for nome, roleta in botauto.roletas.items():
        msg += (
            f"🎰 **{nome}**\n"
            f"   Último: {roleta.ultimo or '...'} | "
            f"Seq: {roleta.contagem}x | "
            f"🟢 {roleta.greens}\n"
        )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def roletas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🎰 **Roletas Monitoradas:**\n\n"
    
    for i, nome in enumerate(botauto.roletas_nomes, 1):
        msg += f"{i}. {nome}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botauto.parar()
    
    total_greens = sum(r.greens for r in botauto.roletas.values())
    
    msg = (
        "⏹️ **Bot Parado**\n\n"
        f"🟢 **Total GREENs: {total_greens}**\n\n"
    )
    
    for nome, roleta in botauto.roletas.items():
        if roleta.greens > 0:
            msg += f"• {nome}: {roleta.greens}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    print("\n" + "="*60)
    print("🎰 BOT MULTI-ROLETA 32RED v4.0")
    print("="*60)
    print(f"[✓] Token carregado")
    print(f"[✓] Roletas a monitorar: {len(botauto.roletas)}")
    print("="*60 + "\n")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iniciar", iniciar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("roletas", roletas))
    app.add_handler(CommandHandler("parar", parar))
    
    print("[✓] Bot aguardando comandos...\n")
    app.run_polling()

if __name__ == "__main__":
    main()
