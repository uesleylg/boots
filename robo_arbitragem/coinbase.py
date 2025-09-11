import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    if 'type' in data and data['type'] == 'ticker':
        price = data.get('price')
        product_id = data.get('product_id')
        print(f"[{product_id}] Preço atual: ${price}")

def on_error(ws, error):
    print("Erro:", error)

def on_close(ws, close_status_code, close_msg):
    print("Conexão fechada")

def on_open(ws):
    print("Conexão aberta")
    subscribe_message = {
        "type": "subscribe",
        "channels": [{"name": "ticker", "product_ids": ["XMR-USD"]}]
    }
    ws.send(json.dumps(subscribe_message))

if __name__ == "__main__":
    url = "wss://ws-feed.exchange.coinbase.com"
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    print("Conectando ao WebSocket da Coinbase para LUNA...")
    ws.run_forever()
