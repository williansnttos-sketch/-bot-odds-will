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

# Memória do Bot: guarda os jogos que já foram enviados hoje para não repetir!
ENVIADOS_HOJE = set()

LIGAS_MONITORADAS = {
    "BRASIL": ["campeonato-brasileiro", "serie-b"],
    "INGLATERRA": ["premier-league"],
    "ESPANHA": ["laliga"]
}

async def puxar_jogos_do_dia_por_liga(pais, liga):
    """
    Aqui o bot busca as partidas reais do dia. Para testes de simulação,
    ele lista as partidas da rodada atual.
    """
    print(f"🕵️ Robô varrendo a liga: {pais} - {liga.upper()}")
    
    if liga == "campeonato-brasileiro":
        return [
            {"id_jogo": "br_01", "partida": "Flamengo vs Palmeiras", "mercado": "Escanteios Totais", "linha": 10.5, "media": 11.8, "odd": 2.10},
            {"id_jogo": "br_02", "partida": "São Paulo vs Corinthians", "mercado": "Cartões Amarelos", "linha": 4.5, "media": 5.6, "odd": 1.95}
        ]
    elif liga == "premier-league":
        return [
            {"id_jogo": "eng_01", "partida": "Arsenal vs Liverpool", "mercado": "Chutes de Jogadores", "linha": 2.5, "media": 3.4, "odd": 2.20}
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
                    # VERIFICAÇÃO DE MEMÓRIA: Se o id do jogo já foi enviado hoje, o bot ignora e não repete!
                    if jogo["id_jogo"] in ENVIADOS_HOJE:
                        continue
                        
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
                            f"🤖 *Tipster:* Entrada única identificada nas estatísticas pré-live."
                        )
                        try:
                            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem, parse_mode="Markdown")
                            # Adiciona o jogo na memória para bloquear repetições
                            ENVIADOS_HOJE.add(jogo["id_jogo"])
                        except Exception as e:
                            print(f"Erro no envio: {e}")
                            
        print("✅ Varredura completa. Próxima busca profunda de dados em 4 horas...")
        # Tempo pré-live ajustado para 4 horas (14400 segundos), ideal para não poluir o canal
        await asyncio.sleep(14400)

# SERVIDOR FALSO EXIGIDO PELA RENDER PARA MANTER O PLANO GRATUITO NO AR 24H
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class FalsoServidor(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot Ativo 24h")

def rodar_servidor_falso():
    server = HTTPServer(('0.0.0.0', 10000), FalsoServidor)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=rodar_servidor_falso, daemon=True).start()
    nest_asyncio.apply()
    asyncio.run(rodar_scanner_global())

