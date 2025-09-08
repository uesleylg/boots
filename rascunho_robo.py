import requests
import time

# Taxa da exchange (em %)
TAXA = 0.1  # 0,1%

# Lista de moedas monitoradas
moedas_lista = ["TRX","XLM","DOGE","ADA","MATIC","SOL","SHIB","AVAX","FTM","LUNA","BTC","ETH"]

# Exchanges e endpoints públicos
exchanges = {
    "binance": {
        "TRX": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=TRXUSDT",
        "XLM": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=XLMUSDT",
        "DOGE": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=DOGEUSDT",
        "ADA": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=ADAUSDT",
        "MATIC": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=POLUSDT",
        "SOL": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=SOLUSDT",
        "SHIB": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=SHIBUSDT",
        "AVAX": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=AVAXUSDT",
       
        "LUNA": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=LUNAUSDT",
        "BTC": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT",
        "ETH": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=ETHUSDT"
    },
    "coinbase": {
        "TRX": "https://api.coinbase.com/v2/prices/TRX-USD/spot",
        "XLM": "https://api.coinbase.com/v2/prices/XLM-USD/spot",
        "DOGE": "https://api.coinbase.com/v2/prices/DOGE-USD/spot",
        "ADA": "https://api.coinbase.com/v2/prices/ADA-USD/spot",
        "MATIC": "https://api.coinbase.com/v2/prices/POL-USD/spot",
        "SOL": "https://api.coinbase.com/v2/prices/SOL-USD/spot",
        "SHIB": "https://api.coinbase.com/v2/prices/SHIB-USD/spot",
        "AVAX": "https://api.coinbase.com/v2/prices/AVAX-USD/spot",
       
        "LUNA": "https://api.coinbase.com/v2/prices/LUNA-USD/spot",
        "BTC": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        "ETH": "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    },
    "coinex": {
        "TRX": "https://api.coinex.com/v1/market/ticker?market=TRXUSDT",
        "XLM": "https://api.coinex.com/v1/market/ticker?market=XLMUSDT",
        "DOGE": "https://api.coinex.com/v1/market/ticker?market=DOGEUSDT",
        "ADA": "https://api.coinex.com/v1/market/ticker?market=ADAUSDT",
        "MATIC": "https://api.coinex.com/v1/market/ticker?market=POLUSDT",
        "SOL": "https://api.coinex.com/v1/market/ticker?market=SOLUSDT",
        "SHIB": "https://api.coinex.com/v1/market/ticker?market=SHIBUSDT",
        "AVAX": "https://api.coinex.com/v1/market/ticker?market=AVAXUSDT",

        "LUNA": "https://api.coinex.com/v1/market/ticker?market=LUNAUSDT",
        "BTC": "https://api.coinex.com/v1/market/ticker?market=BTCUSDT",
        "ETH": "https://api.coinex.com/v1/market/ticker?market=ETHUSDT"
    }
}

# Função para buscar cotação do dólar
def pegar_usd():
    try:
        return float(requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()["USDBRL"]["bid"])
    except:
        return 5.0

# Função para buscar preços e normalizar dados
def pegar_precos(usd_brl):
    precos = {}
    for exchange, moedas in exchanges.items():
        precos[exchange] = {}
        for moeda, url in moedas.items():
            try:
                data = requests.get(url, timeout=5).json()
                if exchange == "binance":
                    precos[exchange][moeda] = {
                        "bid": float(data["bidPrice"]) * usd_brl,
                        "ask": float(data["askPrice"]) * usd_brl,
                        "bidVol": float(data["bidQty"]),
                        "askVol": float(data["askQty"])
                    }
                elif exchange == "coinbase":
                    price = float(data['data']['amount']) * usd_brl
                    precos[exchange][moeda] = {
                        "bid": price, "ask": price,
                        "bidVol": None, "askVol": None
                    }
                elif exchange == "coinex":
                    price = float(data['data']['ticker']['last']) * usd_brl
                    precos[exchange][moeda] = {
                        "bid": price, "ask": price,
                        "bidVol": None, "askVol": None
                    }
            except Exception as e:
                print(f"Erro ao pegar preço de {moeda} em {exchange}: {e}")
    return precos

# Loop principal
while True:
    usd_brl = pegar_usd()
    precos = pegar_precos(usd_brl)
    
    for moeda in moedas_lista:
        asks = {ex: precos[ex][moeda]["ask"] for ex in precos if moeda in precos[ex] and precos[ex][moeda]["ask"] > 0}
        bids = {ex: precos[ex][moeda]["bid"] for ex in precos if moeda in precos[ex] and precos[ex][moeda]["bid"] > 0}

        if len(asks) > 0 and len(bids) > 0:
            ex_compra = min(asks, key=asks.get)
            preco_compra = asks[ex_compra]

            ex_venda = max(bids, key=bids.get)
            preco_venda = bids[ex_venda]

            taxa_compra = preco_compra * TAXA / 100
            taxa_venda = preco_venda * TAXA / 100
            lucro_unitario = (preco_venda - preco_compra) - (taxa_compra + taxa_venda)

            if lucro_unitario > 0:
                print(f"\n💸 Oportunidade de arbitragem encontrada para {moeda}!")
                print(f"Comprar em {ex_compra} por R$ {preco_compra:.4f}")
                print(f"Vender em {ex_venda} por R$ {preco_venda:.4f}")
                print(f"Lucro unitário: R$ {lucro_unitario:.4f}")
    
    time.sleep(10)  # espera 10 segundos antes de buscar novamente
