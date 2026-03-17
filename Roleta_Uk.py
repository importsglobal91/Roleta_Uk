from dataclasses import dataclass, field
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

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

        self.total_green = 0
        self.total_win = 0
        self.total_loss = 0

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
        respostas = []
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

            teclado = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🎰 Abrir mesa",
                            url=self.link_mesa,
                        )
                    ]
                ]
            )

            if acao == "analise":
                msg = f"""🧠 ANÁLISE NA 9ª ENTRADA

🎲 Estratégia: Repetição de {tipo_legenda}
🎰 Mesa: {self.nome_mesa}
🔁 Sequência até agora: {seq_str}

⏱ Aguardando 10ª jogada para possível entrada...
"""
                respostas.append((msg, teclado))

            elif acao == "entrada":
                aposta_contra = self._oposto(tipo_evt, valor_evt)

                msg = f"""🪙 E-GAMES – ROLETA UK
💰 ENTRADA CONFIRMADA 💰

🎲 Estratégia: Repetição de {tipo_legenda} (análise na 9ª, entrada na 10ª)
🎰 Mesa: {self.nome_mesa}
🔁 Sequência observada: {seq_str}

💵 Entrar na 10ª jogada em {aposta_contra.upper()}
👉 Cobrir o zero
🔄 Fazer até 3 gales (máx. 3 tentativas)
"""
                respostas.append((msg, teclado))

        return respostas

    def registrar_green(self):
        self.total_green += 1

    def registrar_red(self, resultado: str):
        if resultado == "win":
            self.total_win += 1
        elif resultado == "loss":
            self.total_loss += 1

    def obter_placar(self) -> str:
        return (
            f"Placar atual:\n"
            f"GREEN: {self.total_green}\n"
            f"WIN: {self.total_win}\n"
            f"LOSS: {self.total_loss}"
        )

    def resetar_placar(self):
        self.total_green = 0
        self.total_win = 0
        self.total_loss = 0


TOKEN = "8792963382:AAF2rxy7oZw0f6cYT2Lg2xP0aznAUTL7JE4"

estrategia = EstrategiaRepeticao(
    nome_mesa="Airwave Roulette - 32Red",
    link_mesa="https://www.32red.com/play/airwave-roulette#playforreal",
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot de Roleta iniciado!\n"
        "Envie resultados no formato: '13 vermelho', '0 verde', '22 preto'.\n"
        "Comandos:\n"
        "/green - marcar entrada GREEN\n"
        "/red - marcar WIN/LOSS\n"
        "/placar - ver placar\n"
        "/reset - zerar contadores"
    )


async def receber_resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().lower()

    partes = texto.split()
    if len(partes) != 2:
        await update.message.reply_text("Formato inválido. Use: '13 vermelho'.")
        return

    try:
        numero = int(partes[0])
    except ValueError:
        await update.message.reply_text("Número inválido. Use algo como: '13 vermelho'.")
        return

    cor = partes[1]
    if cor not in ["vermelho", "preto", "verde"]:
        await update.message.reply_text("Cor inválida. Use: vermelho, preto ou verde.")
        return

    respostas = estrategia.processar_resultado(numero, cor)
    for texto_msg, teclado in respostas:
        await update.message.reply_text(texto_msg, reply_markup=teclado)


async def cmd_green(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estrategia.registrar_green()
    await update.message.reply_text("Entrada GREEN registrada.")


async def cmd_red(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /red win ou /red loss")
        return

    resultado = context.args[0].lower()
    if resultado not in ["win", "loss"]:
        await update.message.reply_text("Use: /red win ou /red loss")
        return

    estrategia.registrar_red(resultado)
    await update.message.reply_text(f"Resultado {resultado.upper()} registrado.")


async def cmd_placar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    placar = estrategia.obter_placar()
    await update.message.reply_text(placar)


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estrategia.resetar_placar()
    await update.message.reply_text("Placar resetado.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("green", cmd_green))
    app.add_handler(CommandHandler("red", cmd_red))
    app.add_handler(CommandHandler("placar", cmd_placar))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receber_resultado,
        )
    )

    print("Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
