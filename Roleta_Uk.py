import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dataclasses import dataclass, field
import logging

# Configuração de log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TOKEN")  # Pega do Render Environment

TIPOS_MERCADO = ["cor", "paridade", "faixa"]

@dataclass
class EstadoMercado:
    ultimo: str | None = None
    contagem: int = 0
    mercados: dict = field(default_factory=dict)

@dataclass
class Placar:
    total_green: int = 0
    total_win: int = 0
    total_loss: int = 0

class BotRoleta:
    def __init__(self):
        self.estado = {tipo: EstadoMercado() for tipo in TIPOS_MERCADO}
        self.placar = Placar()
    
    def obter_placar(self) -> str:
        return (
            f"📊 *Placar atual:*\n"
            f"🟢 GREEN: `{self.placar.total_green}`\n"
            f"✅ WIN: `{self.placar.total_win}`\n"
            f"❌ LOSS: `{self.placar.total_loss}`"
        )
    
    def resetar_placar(self):
        self.placar.total_green = 0
        self.placar.total_win = 0
        self.placar.total_loss = 0

bot = BotRoleta()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 *Bot Roleta 32Red*\n\n"
        "Envie números da roleta (ex: 17, 0, 32) e receba sinais!\n\n"
        "Comandos:\n"
        "/placar - ver estatísticas\n"
        "/reset - zerar placar",
        parse_mode='Markdown'
    )

async def placar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(bot.obter_placar(), parse_mode='Markdown')

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot.resetar_placar()
    await update.message.reply_text("✅ Placar zerado!")

async def receber_resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        numeros = [int(n.strip()) for n in update.message.text.split(',')]
        ultimo = numeros[-1]
        
        resultado = f"🎲 Último: *{ultimo}*\n"
        sinal_gerado = False
        
        for tipo in TIPOS_MERCADO:
            estado = bot.estado[tipo]
            
            if estado.ultimo == ultimo:
                estado.contagem += 1
            else:
                if estado.contagem >= 9:
                    resultado += f"🚨 *SINAL {tipo.upper()}: {estado.ultimo} x{estado.contagem}*\n"
                    sinal_gerado = True
                
                estado.ultimo = ultimo
                estado.contagem = 1
        
        if sinal_gerado:
            bot.placar.total_green += 1
            resultado += f"🟢 GREEN detectado!"
        else:
            resultado += "⏳ Monitorando..."
        
        await update.message.reply_text(resultado, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Envie números válidos! Ex: 17, 0, 32")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

def main():
    if not TOKEN:
        print("❌ Erro: TOKEN não encontrado! Configure no Render Environment.")
        return
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("placar", placar))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_resultado))
    
    print("🤖 Bot Roleta rodando 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
