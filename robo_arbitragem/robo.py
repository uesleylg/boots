import asyncio
import json
import websockets
from decimal import Decimal, getcontext

# ======= CONFIG PRECISÃO =======
getcontext().prec = 12

# ======= VARIÁVEIS GLOBAIS =======
orderbooks_binance = {}
orderbooks_coinex = {}

SYMBOLS = [
     "USDTBRL",  # já na sua lista
    "GALAUSDT",  # já na sua lista
    "SHIBUSDT",  # Shiba Inu
    "DOGEUSDT",  # Dogecoin
    "TRXUSDT",   # TRON
    "MANAUSDT",  # Decentraland
    "SANDUSDT",  # The Sandbox
    "XRPUSDT",   # XRP, ainda barato
    "CELRUSDT",  # Celer Network
]
VOLUME_MINIMO_USDT = Decimal("10")

# ======= CORES NO TERMINAL =======
def color(text, tipo="info"):
    if tipo == "success":
        return f"\033[92m{text}\033[0m"
    elif tipo == "warning":
        return f"\033[93m{text}\033[0m"
    elif tipo == "error":
        return f"\033[91m{text}\033[0m"
    return text

# ======= BINANCE ORDER BOOK =======
async def binance_ws(symbol):
    url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth5@100ms"
    while True:
        try:
            async with websockets.connect(url) as ws:
                print(color(f"📡 Conectado Binance ({symbol})", "success"))
                async for message in ws:
                    data = json.loads(message)
                    bids = [(Decimal(p), Decimal(q)) for p, q in data.get("bids", [])]
                    asks = [(Decimal(p), Decimal(q)) for p, q in data.get("asks", [])]
                    orderbooks_binance[symbol] = {"bids": bids, "asks": asks}
        except Exception as e:
            print(color(f"[Binance-{symbol}] Erro: {e}. Reconectando...", "error"))
            await asyncio.sleep(5)

# ======= COINEX ORDER BOOK =======
async def coinex_ws(symbol):
    WS_URL = "wss://perpetual.coinex.com/"
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                subscribe_msg = {
                    "id": 1,
                    "method": "depth.subscribe",
                    "params": [symbol, 5, "0"]
                }
                await ws.send(json.dumps(subscribe_msg))
                print(color(f"📡 Conectado CoinEx ({symbol})", "success"))
                async for response in ws:
                    data = json.loads(response)
                    if "method" in data and data["method"] == "depth.update":
                        orderbook = data["params"][1]
                        orderbooks_coinex[symbol] = {
                            "asks": [(Decimal(p), Decimal(v)) for p, v in orderbook.get("asks", [])],
                            "bids": [(Decimal(p), Decimal(v)) for p, v in orderbook.get("bids", [])]
                        }
        except Exception as e:
           # print(color(f"[CoinEx-{symbol}] Erro: {e}. Reconectando...", "error"))
            await asyncio.sleep(5)

# ======= LÓGICA DE DIFERENÇA DE PREÇO =======
# ======= LÓGICA DE DIFERENÇA DE PREÇO (APENAS OPORTUNIDADES POSITIVAS) =======
async def diferenca_precos():
    while True:
        await asyncio.sleep(1)
        for symbol in SYMBOLS:
            binance = orderbooks_binance.get(symbol)
            coinex = orderbooks_coinex.get(symbol)

            if not binance or not coinex:
                continue

            if not binance["asks"] or not binance["bids"] or not coinex["asks"] or not coinex["bids"]:
                continue

            # Melhor preço e volume
            b_ask, b_ask_qty = binance["asks"][0]
            b_bid, b_bid_qty = binance["bids"][0]
            c_ask, c_ask_qty = coinex["asks"][0]
            c_bid, c_bid_qty = coinex["bids"][0]

            # Verificar volume mínimo
            if (
                b_ask * b_ask_qty < VOLUME_MINIMO_USDT
                or b_bid * b_bid_qty < VOLUME_MINIMO_USDT
                or c_ask * c_ask_qty < VOLUME_MINIMO_USDT
                or c_bid * c_bid_qty < VOLUME_MINIMO_USDT
            ):
                continue

            # Diferença percentual
            diff_coinex_para_binance = (b_bid - c_ask) / c_ask * 100
            diff_binance_para_coinex = (c_bid - b_ask) / b_ask * 100

         

            # Mostrar apenas oportunidades positivas
            if diff_coinex_para_binance >= 0.02:
                print(color(f"\n💹 [{symbol}] Comparativo de Preços", "warning"))
                print(f"📌 Binance ASK: ${b_ask:.6f} | BID: ${b_bid:.6f}")
                print(f"📌 CoinEx  ASK: ${c_ask:.6f} | BID: ${c_bid:.6f}")
                print(color(f"⚡ CoinEx -> Binance: {diff_coinex_para_binance:.6f}%", "success"))
            if diff_binance_para_coinex > 0.02:
                print(color(f"\n💹 [{symbol}] Comparativo de Preços", "warning"))
                print(f"📌 Binance ASK: ${b_ask:.6f} | BID: ${b_bid:.6f}")
                print(f"📌 CoinEx  ASK: ${c_ask:.6f} | BID: ${c_bid:.6f}")
                print(color(f"⚡ Binance -> CoinEx: {diff_binance_para_coinex:.6f}%", "success"))


# ======= RODAR =======
if __name__ == "__main__":
    async def main():
        tasks = []
        for symbol in SYMBOLS:
            tasks.append(binance_ws(symbol))
            tasks.append(coinex_ws(symbol))
        tasks.append(diferenca_precos())
        await asyncio.gather(*tasks)

    asyncio.run(main())
