
import asyncio
import websockets
import json
import time

# URL WebSocket das exchanges
URL_MEXC = "wss://contract.mexc.com/edge"
URL_BINANCE = "wss://stream.binance.com:9443/ws/galausdt@trade"  # Alterado para DOGE_USDT

# Taxas de transação (em decimal)
TAXA_BINANCE = 0.001 
TAXA_MEXC = 0.0005  

# Fila de preços
fila_precos = asyncio.Queue()

# Função para ping (manter conexão ativa)
async def ping(ws):
    while True:
        await asyncio.sleep(15)
        try:
            await ws.send(json.dumps({"method": "ping"}))
        except:
            break

# Função para pegar o preço da MEXC (Spot)
async def handler_mexc():
    simbolo = "GALA_USDT"  # Alterado para monitorar o par DOGE_USDT

    async with websockets.connect(URL_MEXC) as ws:
        print("[MEXC] Conectado")

        # Subscrição do par DOGE/USDT
        await ws.send(json.dumps({
            "method": "sub.ticker",
            "param": {"symbol": simbolo}
        }))

        # Inicia a tarefa do ping
        asyncio.create_task(ping(ws))

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                # Verifica se a mensagem é sobre o preço do ticker
                if data.get("channel") == "push.ticker" and "data" in data:
                    simbolo = data.get("symbol")
                    preco = float(data["data"]["lastPrice"])
                    await fila_precos.put(("MEXC", simbolo, preco))  # Armazena na fila
            except Exception as e:
                print(f"[MEXC] Erro: {e}")
                break

# Função para pegar o preço da Binance (Spot)
async def handler_binance():
    async with websockets.connect(URL_BINANCE) as ws:
        print("[Binance] Conectado ao par DOGE_USDT")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                preco_binance = float(data["p"])  # Preço de DOGE/USDT na Binance
                await fila_precos.put(("Binance", "GALA_USDT", preco_binance))  # Armazena na fila
            except Exception as e:
                print(f"[Binance] Erro: {e}")
                break

# Função para monitorar a arbitragem e calcular o spread
# Função para monitorar a arbitragem e calcular o spread
async def monitorar_arbitragem():
    precos_mexc = {}
    precos_binance = {}

    while True:
        # Espera que os preços sejam inseridos na fila
        exchange, simbolo, preco = await fila_precos.get()

        if exchange == "MEXC":
            precos_mexc[simbolo] = preco
        elif exchange == "Binance":
            precos_binance[simbolo] = preco

        if simbolo in precos_mexc and simbolo in precos_binance:
            preco_mexc = precos_mexc[simbolo]
            preco_binance = precos_binance[simbolo]

            # Calculando o spread bidirecional (MEXC -> Binance e Binance -> MEXC)
            # Spread líquido MEXC -> Binance
            custo_compra_mexc = preco_mexc * (1 + TAXA_MEXC)  # Preço de compra em MEXC com taxa
            valor_venda_binance = preco_binance * (1 - TAXA_BINANCE)  # Preço de venda em Binance com taxa
            spread_liquido_mb = (valor_venda_binance - custo_compra_mexc) / custo_compra_mexc * 100

            # Spread líquido Binance -> MEXC
            custo_compra_binance = preco_binance * (1 + TAXA_BINANCE)  # Preço de compra na Binance com taxa
            valor_venda_mexc = preco_mexc * (1 - TAXA_MEXC)  # Preço de venda na MEXC com taxa
            spread_liquido_bm = (valor_venda_mexc - custo_compra_binance) / custo_compra_binance * 100

            # Exibindo as oportunidades de arbitragem
            if spread_liquido_mb > 0:
                print(f"⚡ DOGE_USDT: COMPRAR MEXC ({preco_mexc:.6f}) e VENDER BINANCE ({preco_binance:.6f}) | Spread líquido: {spread_liquido_mb:.4f}%")
            if spread_liquido_bm > 0:
                print(f"⚡ DOGE_USDT: COMPRAR BINANCE ({preco_binance:.6f}) e VENDER MEXC ({preco_mexc:.6f}) | Spread líquido: {spread_liquido_bm:.4f}%")

# Função principal para rodar tudo
async def main():
    # Inicia os handlers para MEXC e Binance
    await asyncio.gather(
        handler_mexc(),
        handler_binance(),
        monitorar_arbitragem()
    )

# Executa o loop assíncrono
if __name__ == "__main__":
    asyncio.run(main())
