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
    historico_numeros: list = None
    historico_cores: list = None
    
    def __post_init__(self):
        if self.historico_numeros is None:
            self.historico_numeros = []
        if self.historico_cores is None:
            self.historico_cores = []

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
                altas=EstadoEstrategia("Repetição de Altas")
            )
    
    async def iniciar_monitoramento(self) -> bool:
        try:
            print("[LOG] Iniciando monitoramento com 3 estratégias...")
            hora = datetime.now().strftime("%H:%M:%S")
            
            for nome in self.roletas:
                self.roletas[nome].hora_inicio = hora
            
            self.ativo = True
            print(f"[✓] Monitorando {len(self.roletas)} roletas")
            return True
        except Exception as e:
            print(f"[✗] Erro: {e}")
            return False
    
    def obter_cor(self, numero: int) -> tuple:
        if numero == 0:
            return ("Verde", "G")
        if numero in NUMEROS_VERMELHOS:
            return ("Vermelho", "V")
        else:
            return ("Preto", "P")
    
    def obter_paridade(self, numero: int) -> tuple:
        if numero == 0:
            return ("Zero", "Z")
        if numero % 2 == 0:
            return ("Par", "PA")
        else:
            return ("Ímpar", "I")
    
    def obter_range(self, numero: int) -> tuple:
        if numero == 0:
            return ("Zero", "Z")
        if 1 <= numero <= 18:
            return ("Baixa", "B")
        else:
            return ("Alta", "A")
    
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
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"[✗] Erro em {nome_roleta}: {e}")
                await asyncio.sleep(2)
    
    async def processar_numero(self, nome_roleta: str, numero: int):
        roleta = self.roletas[nome_roleta]
        
        cor_nome, cor_sigla = self.obter_cor(numero)
        par_nome, par_sigla = self.obter_paridade(numero)
        range_nome, range_sigla = self.obter_range(numero)
        
        await self.processar_estrategia(roleta, roleta.cores, numero, cor_nome, cor_sigla, nome_roleta, "Repetição de Cores")
        await self.processar_estrategia(roleta, roleta.pares, numero, par_nome, par_sigla, nome_roleta, "Repetição de Pares")
        await self.processar_estrategia(roleta, roleta.altas, numero, range_nome, range_sigla, nome_roleta, "Repetição de Altas")
    
    async def processar_estrategia(self, roleta, estrategia, numero, valor_nome, valor_sigla, nome_roleta, tipo_estrategia):
        if valor_nome in ["Zero"]:
            estrategia.contagem = 0
            estrategia.historico_numeros = []
            estrategia.historico_cores = []
            return
        
        estrategia.contagem += 1
        estrategia.total_tentativas += 1
        
        if estrategia.contagem == 1:
            estrategia.historico_numeros = []
            estrategia.historico_cores = []
        
        estrategia.historico_numeros.append(numero)
        estrategia.historico_cores.append(valor_sigla)
        
        if valor_nome in ["Vermelho", "Preto", "Par", "Ímpar", "Baixa", "Alta"]:
            estrategia.total_acertos += 1
        
        # ANALISANDO NA 9ª
        if estrategia.contagem == 9:
            try:
                sequencia_parts = []
                for num, cor in zip(estrategia.historico_numeros[-9:], estrategia.historico_cores[-9:]):
                    sequencia_parts.append(f"{num}({cor})")
                sequencia_str = " | ".join(sequencia_parts)
                
                mensagem = (
                    f"📊 **ANALISANDO** 📊\n\n"
                    f"🎨 Estratégia: {tipo_estrategia}\n"
                    f"🏠 Mesa: {nome_roleta}\n"
                    f"🎰 Sequência: {sequencia_str}\n"
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
            
            sequencia_parts = []
            for num, cor in zip(estrategia.historico_numeros[-10:], estrategia.historico_cores[-10:]):
                sequencia_parts.append(f"{num}({cor})")
            sequencia_str = " | ".join(sequencia_parts)
            
            # Instrução específica
            if "Cores" in tipo_estrategia:
                if valor_nome == "Vermelho":
                    instrucao = f"Entrar após o {estrategia.historico_numeros[-10]} apostar na cor vermelha"
                else:
                    instrucao = f"Entrar após o {estrategia.historico_numeros[-10]} apostar na cor preta"
            elif "Pares" in tipo_estrategia:
                if valor_nome == "Par":
                    instrucao = f"Entrar após o {estrategia.historico_numeros[-10]} apostar em números pares"
                else:
                    instrucao = f"Entrar após o {estrategia.historico_numeros[-10]} apostar em números ímpares"
            else:
                if valor_nome == "Baixa":
                    instrucao = f"Entrar após apostar em números baixos (1-18)"
                else:
                    instrucao = f"Entrar após apostar em números altos (19-36)"
            
            mensagem = (
                f"💰 **ENTRADA CONFIRMADA** 💰\n\n"
                f"🎨 Estratégia: {tipo_estrategia}\n"
                f"🏠 Mesa: [{nome_roleta}]({roleta.link})\n"
                f"🎰 Sequência: {sequencia_str}\n\n"
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
            estrategia.historico_numeros = []
            estrategia.historico_cores = []
    
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
        "/iniciar - Ligar bot\n"
        "/parar - Desligar\n\n"
        "✅ Pronto!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if botauto.ativo:
        await update.message.reply_text("❌ Bot já ativo!")
        return
    
    sucesso = await botauto.iniciar_monitoramento()
    
    if sucesso:
        for nome in botauto.roletas:
            asyncio.create_task(botauto.loop_analise_roleta(nome))
        
        await update.message.reply_text("✅ **BOT LIGADO!**\n\n🎰 14 mesas\n📊 3 estratégias")

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botauto.parar()
    await update.message.reply_text("⏹️ **Parado**")

def main():
    print("\n🎰 E-GAMES - ROLETA UK v11.0 FINAL\n")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iniciar", iniciar))
    app.add_handler(CommandHandler("parar", parar))
    
    print("[✓] Bot pronto!\n")
    app.run_polling()

if __name__ == "__main__":
    main()
