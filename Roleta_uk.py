import os
from dataclasses import dataclass, field
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Token vem da variável de ambiente TOKEN (Render)
TOKEN = os.getenv("TOKEN")

TIPOS_MERCADO = ["cor", "paridade", "faixa"]


@dataclass
class EstadoMercado:
    ultimo: str | None = None
    contagem: int = 0
    sequencia: list = field(default_factory=list)


class EstrategiaRepeticao:
    def __init__(self, nome_mesa: str, link_mesa: str):
        self.nome_mesa = nome_mesa
        self.link_mesa = link_mesa
        self.mercados = {
            "cor": EstadoMercado(),
            "paridade": EstadoMercado(),
            "faixa": EstadoMercado(),
        }

    def classificar_resultado(self, numero: int, cor: str):
        if numero == 0:
            cor_tipo = "zero"
            paridade = "zero"
            faixa = "zero"
        else:
            cor_tipo = cor.lower()
            paridade = "par" if numero % 2 == 0 else "impar"
            faixa = "baixo" if 1 <= numero <= 18 else "alto"

        return {
            "cor": cor_tipo,
            "paridade": paridade,
            "faixa": faixa,
        }

    def _atualizar_mercado(self, tipo: str, valor: str):
        estado = self.mercados[tipo]

        if valor == "zero":
            estado.ultimo = None
            estado.contagem = 0
            estado.sequencia.clear()
            return None

        if estado.ultimo == valor:
            estado.contagem += 1
            estado.sequencia.append(valor)
        else:
            estado.ultimo = valor
            estado.contagem = 1
            estado.sequencia = [valor]
            return None

        if estado.contagem == 9:
            return ("analise", tipo, valor, list(estado.sequencia))

        if estado.contagem == 10:
            return ("entrada", tipo, valor, list(estado.sequencia))

        return None

    def _oposto(self, tipo: str, valor: str) -> str:
        if tipo == "cor":
            return "preto" if valor == "vermelho" else "vermelho"
        if tipo == "paridade":
            return "par" if valor == "impar" else "impar"
        if tipo == "faixa":
            return "alto" if valor == "baixo" else "baixo"
        return valor

    def processar_resultado(self, numero: int, cor: str):
        mensagens = []
        classes = self.classificar_resultado(numero, cor)

        for tipo in TIPOS_MERCADO:
            valor = classes[tipo]
            evento = self._atualizar_mercado(tipo, valor)

            if not evento:
                continue

            acao, tipo_evt, valor_evt, seq = evento
            seq_str = " | ".join(seq)

            tipo_legenda = {
                "cor": "Cores",
                "paridade": "Par/Ímpar",
                "faixa": "Altos/Baixos",
            }[tipo_evt]

            if acao == "analise":
                msg = f"""🧠 ANÁLISE NA 9ª ENTRADA

🎲 Estratégia: Repetição de {tipo_legenda}
🎰 Mesa: {self.nome_mesa} – {self.link_mesa}
🔁 Sequência até agora: {seq_str}

⏱ Aguardando 10ª jogada para possível entrada...
"""
                mensagens.append(msg)

            elif acao == "entrada":
                aposta_contra = self._oposto(tipo_evt, valor_evt)

                msg = f"""🪙 E-GAMES – ROLETA UK
💰 ENTRADA CONFIRMADA 💰

🎲 Estratégia: Repetição de {tipo_legenda} (análise na 9ª, entrada na 10ª)
🎰 Mesa: {self.nome_mesa} – {self.link_mesa}
🔁 Sequência observada: {seq_str}

💵 Entrar na 10ª jogada em {aposta_contra.upper()}
👉 Cobrir o zero
🔄 Fazer até 3 gales (máx. 3 tentativas)
"""
                mensagens.append(msg)

        return mensagens


# instância da estratégia (32Red - Dynasty Roulette)
estrategia = EstrategiaRepeticao(
    nome_mesa="32Red - Dynasty Roulette",
    link_mesa="https://www.32red.com/play/dynasty-roulette#playforreal",
)

# >>> PLACAR DO DIA <<<
greens = 0
reds = 0
greens_seguidos = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Envie os resultados no formato: numero cor\nExemplo: 13 vermelho"
    )


async def receber_resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().lower()
    partes = texto.split()

    if len(partes) != 2:
        await update.message.reply_text("Formato inválido. Use: 13 vermelho")
        return

    try:
        numero = int(partes[0])
    except Exception as e:  # ou except ValueError: dependendo do que você queria
