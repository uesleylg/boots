import asyncio
import websockets
import json
import time

URL_WS = "wss://contract.mexc.com/edge"
MOEDAS = [
    "GALA_USDT", "SHIB_USDT", "TRX_USDT", "PEPE_USDT", "DOGE_USDT",
    "SUI_USDT", "ARB_USDT", "BLZ_USDT", "XEC_USDT", "POL_USDT",
    "ENJ_USDT", "CHZ_USDT", "STMX_USDT"
]

TAXA_SPOT = 0.05  # % do taker
TAXA_FUTURO = 0.02  # % do taker

async def ping(ws):
    while True:
        await asyncio.sleep(15)
        await ws.send(json.dumps({"method": "ping"}))

async def monitor_moeda(simbolo):
    preco_futuro = None
    preco_spot = None
    async with websockets.connect(URL_WS) as ws:
        print(f"[{simbolo}] Conectado ao WebSocket")

        # Subscribes
        await ws.send(json.dumps({"method": "sub.deal", "param": {"symbol": simbolo}}))  # Futuro
        await ws.send(json.dumps({"method": "sub.ticker", "param": {"symbol": simbolo}}))  # Spot

        asyncio.create_task(ping(ws))

        ultima_impressao = 0
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                # Atualiza preço FUTURO
                if data.get("channel") == "push.deal" and data.get("data"):
                    preco_futuro = data.get('data')[0]['p']

                # Atualiza preço SPOT
                elif data.get("channel") == "push.ticker" and 'data' in data:
                    preco_spot = float(data['data']['lastPrice'])

                # Verifica oportunidades
                if preco_futuro is not None and preco_spot is not None:
                    # Calculo do spread líquido considerando taxas
                    spread_liquido = (preco_futuro - preco_spot) / preco_spot * 100 - (TAXA_SPOT + TAXA_FUTURO)

                    # Alerta somente se for lucrativo
                    if spread_liquido > 0:
                        if time.time() - ultima_impressao > 2:
                            ultima_impressao = time.time()
                            print(f"⚡ Oportunidade {simbolo}: COMPRAR Spot e VENDER Futuro | Spread Líquido: {spread_liquido:.2f}%")

            except Exception as e:
                print(f"[{simbolo}] Erro: {e}")
                await asyncio.sleep(1)

async def main():
    tarefas = [monitor_moeda(simbolo) for simbolo in MOEDAS]
    await asyncio.gather(*tarefas)

asyncio.run(main())
