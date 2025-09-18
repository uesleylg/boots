import asyncio
import websockets
import json
import time

# URL WebSocket das exchanges
URL_MEXC = "wss://contract.mexc.com/edge"
URL_BINANCE = "wss://stream.binance.com:9443/ws/galausdt@depth"  # Alterado para depth

# Taxas de transação (em decimal)
TAXA_BINANCE = 0.001  
TAXA_MEXC = 0.0005  

# Fila de preços
fila_precos = asyncio.Queue()

# Valor mínimo para arbitragem (em USDT)
VALOR_MINIMO = 50.0

# Função para ping (manter conexão ativa)
async def ping(ws):
    while True:
        await asyncio.sleep(15)
        try:
            await ws.send(json.dumps({"method": "ping"}))
        except:
            break

# Função para pegar o livro de ordens na MEXC
async def handler_mexc():
    simbolo = "GALA_USDT"

    async with websockets.connect(URL_MEXC) as ws:
        print("[MEXC] Conectado")

        # Subscrição do livro de ordens (depth)
        await ws.send(json.dumps({
            "method": "sub.depth",
            "param": {"symbol": simbolo, "limit": 5}  # 5 níveis de profundidade
        }))

        # Inicia a tarefa do ping
        asyncio.create_task(ping(ws))

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                # Verifica se a mensagem é sobre o livro de ordens
                if data.get("channel") == "push.depth" and "data" in data:
                    simbolo = data.get("symbol")
                    asks = data["data"]["asks"]  # Ordens de venda
                    bids = data["data"]["bids"]  # Ordens de compra
                    
                    # Verifica a liquidez das ordens de compra e venda
                    volume_ask = sum(float(ask[1]) for ask in asks)
                    volume_bid = sum(float(bid[1]) for bid in bids)

                    # Se houver liquidez suficiente, armazena o preço e volume
                    if volume_ask >= VALOR_MINIMO and volume_bid >= VALOR_MINIMO:
                        preco_ask = float(asks[0][0])  # Preço da primeira ordem de venda
                        preco_bid = float(bids[0][0])  # Preço da primeira ordem de compra
                        await fila_precos.put(("MEXC", simbolo, preco_ask, preco_bid, volume_ask, volume_bid))  # Armazena na fila
            except Exception as e:
                print(f"[MEXC] Erro: {e}")
                break

# Função para pegar o livro de ordens na Binance
async def handler_binance():
    async with websockets.connect(URL_BINANCE) as ws:
        print("[Binance] Conectado ao par GALA_USDT")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                asks = data["a"]  # Ordens de venda
                bids = data["b"]  # Ordens de compra

                # Verifica a liquidez das ordens de compra e venda
                volume_ask = sum(float(ask[1]) for ask in asks)
                volume_bid = sum(float(bid[1]) for bid in bids)

                # Se houver liquidez suficiente, armazena o preço e volume
                if volume_ask >= VALOR_MINIMO and volume_bid >= VALOR_MINIMO:
                    preco_ask = float(asks[0][0])  # Preço da primeira ordem de venda
                    preco_bid = float(bids[0][0])  # Preço da primeira ordem de compra
                    await fila_precos.put(("Binance", "GALA_USDT", preco_ask, preco_bid, volume_ask, volume_bid))  # Armazena na fila
            except Exception as e:
                print(f"[Binance] Erro: {e}")
                break

# Função para monitorar a arbitragem e calcular o spread
async def monitorar_arbitragem():
    precos_mexc = {}
    precos_binance = {}

    while True:
        # Espera que os preços sejam inseridos na fila
        exchange, simbolo, preco_ask, preco_bid, volume_ask, volume_bid = await fila_precos.get()

        if exchange == "MEXC":
            precos_mexc[simbolo] = (preco_ask, preco_bid, volume_ask, volume_bid)
        elif exchange == "Binance":
            precos_binance[simbolo] = (preco_ask, preco_bid, volume_ask, volume_bid)

        if simbolo in precos_mexc and simbolo in precos_binance:
            preco_ask_mexc, preco_bid_mexc, volume_ask_mexc, volume_bid_mexc = precos_mexc[simbolo]
            preco_ask_binance, preco_bid_binance, volume_ask_binance, volume_bid_binance = precos_binance[simbolo]

            # Calculando o spread bidirecional (MEXC -> Binance e Binance -> MEXC)
            custo_compra_mexc = preco_ask_mexc * (1 + TAXA_MEXC)
            valor_venda_binance = preco_bid_binance * (1 - TAXA_BINANCE)
            spread_liquido_mb = (valor_venda_binance - custo_compra_mexc) / custo_compra_mexc * 100

            custo_compra_binance = preco_ask_binance * (1 + TAXA_BINANCE)
            valor_venda_mexc = preco_bid_mexc * (1 - TAXA_MEXC)
            spread_liquido_bm = (valor_venda_mexc - custo_compra_binance) / custo_compra_binance * 100

            # Obtém a hora atual
            hora_atual = time.strftime("%H:%M:%S")

            # Exibindo as oportunidades de arbitragem com a hora e condições de liquidez
            if spread_liquido_mb >= 0.03:
                print(f"{hora_atual} ⚡ GALA_USDT: COMPRAR MEXC ({preco_ask_mexc:.6f}) e VENDER BINANCE ({preco_bid_binance:.6f}) | Spread líquido: {spread_liquido_mb:.4f}%")
                print(f"   Liquidez MEXC: Compras ({volume_bid_mexc:.2f} GALA) / Vendas ({volume_ask_mexc:.2f} GALA)")
                print(f"   Liquidez Binance: Compras ({volume_bid_binance:.2f} GALA) / Vendas ({volume_ask_binance:.2f} GALA)")

            if spread_liquido_bm >= 0.03:
                print(f"{hora_atual} ⚡ GALA_USDT: COMPRAR BINANCE ({preco_ask_binance:.6f}) e VENDER MEXC ({preco_bid_mexc:.6f}) | Spread líquido: {spread_liquido_bm:.4f}%")
                print(f"   Liquidez MEXC: Compras ({volume_bid_mexc:.2f} GALA) / Vendas ({volume_ask_mexc:.2f} GALA)")
                print(f"   Liquidez Binance: Compras ({volume_bid_binance:.2f} GALA) / Vendas ({volume_ask_binance:.2f} GALA)")

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
