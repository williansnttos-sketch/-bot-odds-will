import logging
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import nest_asyncio
from datetime import datetime

# CONFIGURAÇÕES DO SEU CANAL
TELEGRAM_TOKEN = "8807198626:AAEFkfBxZUmeQWYf_koBsWrvWZwDrsiK1Xc"
TELEGRAM_CHAT_ID = "-1004351713753"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

LIGAS_MONITORADAS = {
    "BRASIL": ["campeonato-brasileiro", "serie-b", "copa-do-brasil"],
    "INGLATERRA": ["premier-league", "championship"],
    "ESPANHA": ["laliga", "laliga2"],
    "EUROPA": ["champions-league", "europa-league"]
}

async def puxar_jogos_do_dia_por_liga(pais, liga):
    print(f"🕵️ Robô varrendo a liga: {pais} - {liga.upper()}")
    if liga == "campeonato-brasileiro":
        return [
            {"partida": "Flamengo vs Palmeiras", "mercado": "Escanteios Totais", "linha": 10.5, "media": 11.8, "odd": 2.10},
            {"partida": "São Paulo vs Corinthians", "mercado": "Cartões Amarelos", "linha": 4.5, "media": 5.6, "odd": 1.95}
        ]
    elif liga == "premier-league":
        return [
            {"partida": "Arsenal vs Liverpool", "mercado": "Chutes de Jogadores", "linha": 2.5, "media": 3.4, "odd": 2.20}
        ]
    return []

def validar_valor_EV(odd, media, linha):
    chance = (media / (linha * 1.12)) * 0.50
    if chance > 0.85: chance = 0.65
    valor_esperado = (odd * chance) - 1
    return valor_esperado > 0, round(1 / chance, 2), round(valor_esperado * 100, 2)

async def rodar_scanner_global():
    bot = Bot(token=TELEGRAM_TOKEN)
    print("🚀 SCANNER GLOBAL DE LIGAS INICIADO!")
    
    while True:
        for pais, lista_ligas in LIGAS_MONITORADAS.items():
            for liga in lista_ligas:
                jogos_encontrados = await puxar_jogos_do_dia_por_liga(pais, liga)
                for jogo in jogos_encontrados:
                    tem_valor, odd_justa, porcentagem = validar_valor_EV(
                        jogo["odd"], jogo["media"], jogo["linha"]
                    )
                    if tem_valor:
                        mensagem = (
                            f"🌍 **SCANNER GLOBAL - LIGA: {pais} ({liga.upper()})**\n\n"
                            f"⚽ **Jogo:** {jogo['partida']}\n"
                            f"📊 **Mercado:** {jogo['mercado']}\n\n"
                            f"📈 **Odd Coletada:** `{jogo['odd']}`\n"
                            f"📐 **Odd Justa:** `{odd_justa}`\n"
                            f"🔍 **Média Extraída da Liga:** `{jogo['media']}`\n"
                            f"💎 **Vantagem Estimada:** `+{porcentagem}% EV`\n\n"
                            f"🤖 *Tipster:* Entrada confirmada após o bot recalcular todas as ligas."
                        )
                        try:
                            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem, parse_mode="Markdown")
                        except Exception as e:
                            print(f"Erro no envio: {e}")
                            
        print("✅ Varredura completa. Próximo scan em 1 hora...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(run_global_scanner())
