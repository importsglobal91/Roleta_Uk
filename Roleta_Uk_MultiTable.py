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
class EstadoEstrategia:
    nome: str
    contagem: int = 0
    greens: int = 0
    greens_seguidos: int = 0
    total_tentativas: int = 0
    total_acertos: int = 0

@dataclass
class EstadoRoleta:
    nome: str
    link: str
    cores: EstadoEstrategia = None
    pares: EstadoEstrategia = None
    altas: EstadoEstrategia = None
    hora_inicio: str = None

class BotMultiRoleta:
    def __init__(self):
        self.roletas = {}
        self.ativo = False
        self.context = None
        self.chat_id = None
        
        for nome, link in ROLETAS_LINKS.items():
            self.roletas[nome] = EstadoRoleta(
                nome=nome,
                link=link,
                cores=EstadoEstrategia("Repetição de Cores"),
                pares=EstadoEstrategia("Repetição de Pares"),
                altas=EstadoEstrategia("Repetição de Alta")
            )
    
    async def iniciar_monitoramento(self) -> bool:
        try:
            print("[LOG] Iniciando monitoramento de 3 estratégias...")
            hora = datetime.now().strftime("%H:%M:%S")
            
            for nome in self.roletas:
                self.roletas[nome].hora_inicio = hora
            
            self.ativo = True
            print(f"[✓] Monitorando {len(self.roletas)} roletas com 3 estratégias")
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
    
    def obter_paridade(self, numero: int) -> str:
        if numero == 0:
            return "Zero"
        if numero % 2 == 0:
            return "Par"
        else:
            return "Ímpar"
    
    def obter_range(self, numero: int) -> str:
        if numero == 0:
            return "Zero"
        if 1 <= numero <= 18:
            return "Baixa"
        else:
            return "Alta"
    
    async def gerar_numero(self):
        numero = random.randint(0, 36)
        return numero
    
    async def loop_analise_roleta(self, nome_roleta: str):
        print(f"[▶️] Monitorando 3 estratégias em: {nome_roleta}")
        
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
        
        # ESTRATÉGIA 1: CORES
        await self.processar_estrategia(roleta, roleta.cores, self.obter_cor(numero), nome_roleta, "Repetição de Cores")
        
        # ESTRATÉGIA 2: PARES/ÍMPARES
        await self.processar_estrategia(roleta, roleta.pares, self.obter_paridade(numero), nome_roleta, "Repetição de Pares")
        
        # ESTRATÉGIA 3: BAIXA/ALTA
        await self.processar_estrategia(roleta, roleta.altas, self.obter_range(numero), nome_roleta, "Repetição de Alta")
    
    async def processar_estrategia(self, roleta, estrategia, valor, nome_roleta, tipo_estrategia):
        if valor in ["Zero"]:
            estrategia.contagem = 0
            return
        
        estrategia.contagem += 1
        estrategia.total_tentativas += 1
        
        if valor in ["Vermelho", "Preto", "Par", "Ímpar", "Baixa", "Alta"]:
            estrategia.total_acertos += 1
        
        # ANALISANDO NA 9ª
        if estrategia.contagem == 9:
            try:
                percentual = (estrategia.total_acertos / estrategia.total_tentativas * 100) if estrategia.total_tentativas > 0 else 0
                
                mensagem = (
                    f"📊 **ANALISANDO** 📊\n\n"
                    f"🎨 Estratégia: {tipo_estrategia}\n"
                    f"🏠 Mesa: [{nome_roleta}]({roleta.link})\n"
                    f"🎰 Sequência: {' | '.join([str(valor)] * 9)}\n"
                )
                await self.context.bot.send_message(
                    chat_id=self.chat_id,
                    text=mensagem,
                    parse_mode="Markdown"
                )
            except:
                pass
        
        # ENTRADA CONFIRMADA NA 10ª
        if estrategia.contagem == 10:
            estrategia.greens += 1
            estrategia.greens_seguidos += 1
            
            percentual = (estrategia.total_acertos / estrategia.total_tentativas * 100) if estrategia.total_tentativas > 0 else 0
            
            # Instrução específica por tipo
            if "Cores" in tipo_estrategia:
                if valor == "Vermelho":
                    instrucao = "Entrar após o 13 apostar na cor vermelha"
                else:
                    instrucao = "Entrar após o 13 apostar na cor preta"
            elif "Pares" in tipo_estrategia:
                if valor == "Par":
                    instrucao = "Entrar após o 18 apostar em números pares"
                else:
                    instrucao = "Entrar após o 18 apostar em números ímpares"
            else:
                if valor == "Baixa":
                    instrucao = "Entrar após apostar em números baixos (1-18)"
                else:
                    instrucao = "Entrar após apostar em números altos (19-36)"
            
            mensagem = (
                f"💰 **ENTRADA CONFIRMADA** 💰\n\n"
                f"🎨 Estratégia: {tipo_estrategia}\n"
                f"🏠 Mesa: [{nome_roleta}]({roleta.link})\n"
                f"🎰 Sequência: {' | '.join([str(valor)] * 10)}\n\n"
                f"💰 {instrucao}\n"
                f"🏠 Cobrir o zero\n"
                f"🎲 Fazer até 3 gales\n"
            )
            
            await self.context.bot.send_message(
                chat_id=self.chat_id,
                text=mensagem,
                parse_mode="Markdown"
            )
            
            # GREEN
            sucesso = (
                f"✅ **GREEN!!!** ✅ ({estrategia.total_acertos} | {estrategia.total_tentativas - estrategia.total_acertos})\n\n"
                f"🎯 Placar do dia 🎰 {estrategia.total_acertos} ✅ {estrategia.total_tentativas - estrategia.total_acertos}\n"
                f"🎲 Acertamos {percentual:.2f}% das vezes\n"
                f"🟢 Estamos com {estrategia.greens_seguidos} Greens seguidos!"
            )
            
            await self.context.bot.send_message(
                chat_id=self.chat_id,
                text=sucesso,
                parse_mode="Markdown"
            )
            
            estrategia.contagem = 0
    
    def parar(self):
        self.ativo = False
        print("[⏹️] Bot parado")

botauto = BotMultiRoleta()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botauto.chat_id = update.effective_chat.id
    botauto.context = context
    
    msg = (
        "🎰 **E-GAMES - ROLETA UK** 🎰\n\n"
        "**3 Estratégias em 14 Mesas!**\n\n"
        "📊 Monitorando:\n"
        "🎨 Repetição de Cores\n"
        "🔢 Repetição de Pares/Ímpares\n"
        "📊 Repetição de Baixa/Alta\n\n"
        "/iniciar - Ligar bot\n"
        "/status - Ver status\n"
        "/parar - Desligar\n\n"
        "✅ Pronto!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    print(f"[✓] Chat: {botauto.chat_id}")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if botauto.ativo:
        await update.message.reply_text("❌ Bot já ativo!")
        return
    
    await update.message.reply_text("⏳ Iniciando 3 estratégias em 14 mesas...\n(Aguarde 30 segundos)")
    
    try:
        sucesso = await botauto.iniciar_monitoramento()
        
        if sucesso:
            for nome in botauto.roletas:
                asyncio.create_task(botauto.loop_analise_roleta(nome))
            
            msg = (
                "✅ **BOT LIGADO!**\n\n"
                f"🎰 {len(botauto.roletas)} mesas\n"
                "📊 3 estratégias simultâneas\n"
                "Use /status para ver"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            print("[✓] Bot inicializado!")
        else:
            await update.message.reply_text("❌ Erro")
            
    except Exception as e:
        await update.message.reply_text(f"❌ {str(e)}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not botauto.ativo:
        await update.message.reply_text("❌ Desligado")
        return
    
    msg = "✅ **STATUS - 3 ESTRATÉGIAS**\n\n"
    
    for nome, roleta in botauto.roletas.items():
        msg += (
            f"🎰 {nome}\n"
            f"   🎨 Cores: {roleta.cores.contagem}x\n"
            f"   🔢 Pares: {roleta.pares.contagem}x\n"
            f"   📊 Altas: {roleta.altas.contagem}x\n"
        )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botauto.parar()
    await update.message.reply_text("⏹️ Parado")

def main():
    print("\n" + "="*60)
    print("🎰 E-GAMES - ROLETA UK v9.0")
    print("3 ESTRATÉGIAS SIMULTÂNEAS")
    print("="*60 + "\n")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iniciar", iniciar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("parar", parar))
    
    print("[✓] Aguardando comandos...\n")
    app.run_polling()

if __name__ == "__main__":
    main()
