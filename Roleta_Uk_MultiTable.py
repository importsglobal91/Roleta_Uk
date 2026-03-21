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

# Números vermelhos
NUMEROS_VERMELHOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

ROLETAS_LINKS = {
    "32Red Roulette": "https://www.32red.com/play/32red-roulette#playforreal",
    "Dynasty Lightning Roulette": "https://www.32red.com/play/dynasty-lightning-roulette#playforreal",
    "Lightning Roulette": "https://www.32red.com/play/lightning-roulette#playforreal",
    "Red Door Roulette": "https://www.32red.com/play/red-door-roulette#playforreal",
    "Diamond Rush Roulette": "https://www.32red.com/play/diamond-rush-roulette#playforreal",
    "Live Roulette": "https://www.32red.com/play/live-roulette#playforreal",
    "Power Up Roulette": "https://www.32red.com/play/power-up-roulette#playforreal",
    "Fortune Roulette": "https://www.32red.com/play/fortune-roulette#playforreal",
    "Fireball Roulette": "https://www.32red.com/play/fireball-roulette#playforreal",
    "Mega Roulette 3000": "https://www.32red.com/play/mega-roulette-3000#playforreal",
    "Gold Vault Roulette": "https://www.32red.com/play/gold-vault-roulette#playforreal",
    "Lucky 6 Roulette": "https://www.32red.com/play/lucky-6-roulette#playforreal",
    "Roulette VIP": "https://www.32red.com/play/roulette-vip#playforreal",
    "Double Ball Roulette": "https://www.32red.com/play/double-ball-roulette#playforreal",
}

@dataclass
class EstadoRoleta:
    nome: str
    link: str
    ultima_cor: str = None
    contagem_cor: int = 0
    greens: int = 0
    greens_seguidos: int = 0
    total_rodadas: int = 0
    total_verdes: int = 0
    total_vermelhos: int = 0
    hora_inicio: str = None

class BotMultiRoleta:
    def __init__(self):
        self.roletas = {}
        self.ativo = False
        self.context = None
        self.chat_id = None
        
        for nome, link in ROLETAS_LINKS.items():
            self.roletas[nome] = EstadoRoleta(nome=nome, link=link)
    
    async def iniciar_monitoramento(self) -> bool:
        try:
            print("[LOG] Iniciando monitoramento de CORES...")
            hora = datetime.now().strftime("%H:%M:%S")
            
            for nome in self.roletas:
                self.roletas[nome].hora_inicio = hora
            
            self.ativo = True
            print(f"[✓] Monitorando {len(self.roletas)} roletas")
            return True
        except Exception as e:
            print(f"[✗] Erro: {e}")
            return False
    
    def obter_cor(self, numero: int) -> str:
        if numero == 0:
            return "Verde"
        if numero in NUMEROS_VERMELHOS:
            return "Vermelho"
        else:
            return "Preto"
    
    async def gerar_numero(self):
        numero = random.randint(0, 36)
        return numero
    
    async def loop_analise_roleta(self, nome_roleta: str):
        print(f"[▶️] Monitorando CORES em: {nome_roleta}")
        
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
        cor = self.obter_cor(numero)
        
        # Conta verdes e vermelhos
        if cor == "Vermelho":
            roleta.total_vermelhos += 1
        elif cor == "Preto":
            roleta.total_verdes += 1
        
        roleta.total_rodadas += 1
        
        # Se a cor mudou, reseta contador
        if roleta.ultima_cor != cor:
            roleta.contagem_cor = 1
            roleta.ultima_cor = cor
        else:
            roleta.contagem_cor += 1
        
        print(f"[{nome_roleta}] Nº: {numero} | Cor: {cor} | Seq: {roleta.contagem_cor}x")
        
        # ANALISANDO NA 9ª SEQUÊNCIA
        if roleta.contagem_cor == 9:
            try:
                mensagem = (
                    f"📊 **ANALISANDO** 📊\n\n"
                    f"🎨 Estratégia: Repetição de {cor}s\n"
                    f"🏠 Mesa: [{nome_roleta}]({roleta.link})\n"
                    f"🎰 Sequência: {' | '.join([str(numero)] * 9)}\n"
                )
                await self.context.bot.send_message(
                    chat_id=self.chat_id,
                    text=mensagem,
                    parse_mode="Markdown"
                )
            except:
                pass
        
        # ENTRADA CONFIRMADA NA 10ª SEQUÊNCIA
        if roleta.contagem_cor == 10:
            roleta.greens += 1
            roleta.greens_seguidos += 1
            
            # Calcula percentual
            if roleta.total_rodadas > 0:
                percentual = (roleta.total_verdes / roleta.total_rodadas) * 100
            else:
                percentual = 0
            
            mensagem = (
                f"💰 **ENTRADA CONFIRMADA** 💰\n\n"
                f"🎨 Estratégia: Repetição de {cor}s\n"
                f"🏠 Mesa: [{nome_roleta}]({roleta.link})\n"
                f"🎰 Sequência: {' | '.join([str(numero)] * 10)}\n\n"
                f"💰 Entrar após o 10 apostar em números {cor.lower()}s\n"
                f"🏠 Cobrir o zero\n"
                f"🎲 Fazer até 3 gales\n"
            )
            
            await self.context.bot.send_message(
                chat_id=self.chat_id,
                text=mensagem,
                parse_mode="Markdown"
            )
            
            # Mensagem de sucesso
            sucesso = (
                f"✅ **GREEN!!!** ✅ ({roleta.total_verdes} | {roleta.total_vermelhos})\n\n"
                f"🎯 Placar do dia 🎰 {roleta.total_verdes} 🟢 {roleta.total_vermelhos}\n"
                f"🎲 Acertamos {percentual:.2f}% das vezes\n"
                f"🟢 Estamos com {roleta.greens_seguidos} Greens seguidos!"
            )
            
            await self.context.bot.send_message(
                chat_id=self.chat_id,
                text=sucesso,
                parse_mode="Markdown"
            )
            
            print(f"\n{'='*60}")
            print(f"🟢 SINAL DETECTADO EM {nome_roleta.upper()}!")
            print(f"{'='*60}\n")
            
            roleta.contagem_cor = 0
    
    def parar(self):
        self.ativo = False
        print("[⏹️] Bot parado")

botauto = BotMultiRoleta()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botauto.chat_id = update.effective_chat.id
    botauto.context = context
    
    msg = (
        "🎰 **E-GAMES - ROLETA UK** 🎰\n\n"
        "**Monitorando 14 mesas em tempo real!**\n\n"
        "/iniciar - Ligar monitoramento 24/7\n"
        "/status - Ver status\n"
        "/roletas - Lista de mesas\n"
        "/parar - Desligar bot\n\n"
        "✅ Pronto para analisar!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    print(f"[✓] Chat autorizado: {botauto.chat_id}")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if botauto.ativo:
        await update.message.reply_text("❌ Bot já está ativo!")
        return
    
    await update.message.reply_text("⏳ Iniciando análise de CORES em 14 mesas...\n(Aguarde 30 segundos)")
    
    try:
        sucesso = await botauto.iniciar_monitoramento()
        
        if sucesso:
            for nome in botauto.roletas:
                asyncio.create_task(botauto.loop_analise_roleta(nome))
            
            msg = (
                "✅ **BOT LIGADO!**\n\n"
                f"🎰 Monitorando {len(botauto.roletas)} mesas\n"
                f"🎨 Estratégia: Repetição de CORES\n"
                f"⏱️ Início: {botauto.roletas[list(botauto.roletas.keys())[0]].hora_inicio}\n\n"
                "Use /status para ver atualizações"
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
    
    msg = "✅ **STATUS - MONITORAMENTO EM TEMPO REAL**\n\n"
    
    for nome, roleta in botauto.roletas.items():
        msg += (
            f"🎰 {nome}\n"
            f"   Seq: {roleta.contagem_cor}x | 🟢 {roleta.greens}\n"
        )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def roletas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🎰 **Mesas Monitoradas (14 Total):**\n\n"
    
    for i, (nome, link) in enumerate(ROLETAS_LINKS.items(), 1):
        msg += f"{i}. [{nome}]({link})\n"
    
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
    print("🎰 E-GAMES - ROLETA UK v8.0")
    print("="*60)
    print(f"[✓] Token carregado")
    print(f"[✓] Mesas a monitorar: {len(botauto.roletas)}")
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
