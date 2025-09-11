import asyncio
import websockets
import json

WS_URL = "wss://perpetual.coinex.com/"

async def orderbook(valor_usdt):
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("✅ Conectado ao WebSocket da CoinEx")

                subscribe_msg = {
                    "id": 1,
                    "method": "depth.subscribe",
                    "params": ["LUNAUSDT", 20, "0"]
                }
                await ws.send(json.dumps(subscribe_msg))
                print("📡 Inscrito no Order Book BTC/USDT\n")

                while True:
                    response = await ws.recv()
                    data = json.loads(response)

                    if "method" in data and data["method"] == "depth.update":
                        orderbook = data["params"][1]
                        asks = orderbook.get("asks", [])
                        bids = orderbook.get("bids", [])

                        if not asks:
                            continue  # ignora updates sem asks

                        print("\n🔴 Asks (vendas):")
                        acumulado_btc = 0.0
                        gasto_usdt = 0.0
                        preco_final = None

                        for price, volume in asks:
                            price = float(price)
                            volume = float(volume)
                            valor_disponivel = volume * price

                            if gasto_usdt < valor_usdt:
                                falta = valor_usdt - gasto_usdt
                                if valor_disponivel >= falta:
                                    btc_comprado = falta / price
                                    acumulado_btc += btc_comprado
                                    gasto_usdt += falta
                                    preco_final = price
                                    print(f"  -> Preço: {price:.2f} | BTC comprado: {btc_comprado:.6f} | Acumulado BTC: {acumulado_btc:.6f} | USDT gasto: {gasto_usdt:.2f}")
                                    break
                                else:
                                    acumulado_btc += volume
                                    gasto_usdt += valor_disponivel
                                    print(f"  Preço: {price:.2f} | BTC comprado: {volume:.6f} | Acumulado BTC: {acumulado_btc:.6f} | USDT gasto: {gasto_usdt:.2f}")

                        if gasto_usdt >= valor_usdt:
                            preco_medio = gasto_usdt / acumulado_btc
                            print(f"\n✅ É viável comprar ${valor_usdt:.2f} em BTC")
                            print(f"💰 BTC total comprado: {acumulado_btc:.6f}")
                            print(f"💵 Preço médio: {preco_medio:.2f} USDT\n")
                        else:
                            print(f"\n❌ Não há liquidez suficiente para comprar ${valor_usdt:.2f} em BTC neste momento.\n")

        except Exception as e:
            print(f"⚠️ Conexão perdida: {e}, tentando reconectar em 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    valor = 100  # USDT
    asyncio.run(orderbook(valor))
