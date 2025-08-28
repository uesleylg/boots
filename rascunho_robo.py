import requests

# Taxa da exchange (em %)
TAXA = 0.1  # 0,1%

# Cotação do dólar
try:
    usd_brl = float(requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()["USDBRL"]["bid"])
except:
    usd_brl = 5.0  # fallback se API falhar

# Exchanges e endpoints públicos
exchanges = {
    "binance": {
        "TRX": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=TRXUSDT",
        "XLM": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=XLMUSDT",
        "DOGE": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=DOGEUSDT",
        "ADA": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=ADAUSDT",
        "MATIC": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=MATICUSDT",
        "SOL": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=SOLUSDT",
        "SHIB": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=SHIBUSDT",
        "AVAX": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=AVAXUSDT",
        "FTM": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=FTMUSDT",
        "LUNA": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=LUNAUSDT",
        "BTC": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT",
        "ETH": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=ETHUSDT"
    },
    "coinbase": {
        "TRX": "https://api.coinbase.com/v2/prices/TRX-USD/spot",
        "XLM": "https://api.coinbase.com/v2/prices/XLM-USD/spot",
        "DOGE": "https://api.coinbase.com/v2/prices/DOGE-USD/spot",
        "ADA": "https://api.coinbase.com/v2/prices/ADA-USD/spot",
        "MATIC": "https://api.coinbase.com/v2/prices/MATIC-USD/spot",
        "SOL": "https://api.coinbase.com/v2/prices/SOL-USD/spot",
        "SHIB": "https://api.coinbase.com/v2/prices/SHIB-USD/spot",
        "AVAX": "https://api.coinbase.com/v2/prices/AVAX-USD/spot",
        "FTM": "https://api.coinbase.com/v2/prices/FTM-USD/spot",
        "LUNA": "https://api.coinbase.com/v2/prices/LUNA-USD/spot",
        "BTC": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        "ETH": "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    },
    "coinex": {
        "TRX": "https://api.coinex.com/v1/market/ticker?market=TRXUSDT",
        "XLM": "https://api.coinex.com/v1/market/ticker?market=XLMUSDT",
        "DOGE": "https://api.coinex.com/v1/market/ticker?market=DOGEUSDT",
        "ADA": "https://api.coinex.com/v1/market/ticker?market=ADAUSDT",
        "MATIC": "https://api.coinex.com/v1/market/ticker?market=MATICUSDT",
        "SOL": "https://api.coinex.com/v1/market/ticker?market=SOLUSDT",
        "SHIB": "https://api.coinex.com/v1/market/ticker?market=SHIBUSDT",
        "AVAX": "https://api.coinex.com/v1/market/ticker?market=AVAXUSDT",
        "FTM": "https://api.coinex.com/v1/market/ticker?market=FTMUSDT",
        "LUNA": "https://api.coinex.com/v1/market/ticker?market=LUNAUSDT",
        "BTC": "https://api.coinex.com/v1/market/ticker?market=BTCUSDT",
        "ETH": "https://api.coinex.com/v1/market/ticker?market=ETHUSDT"
    }
}

# Função para buscar preços e normalizar dados
def pegar_precos():
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

# Lista de moedas monitoradas
moedas_lista = ["TRX","XLM","DOGE","ADA","MATIC","SOL","SHIB","AVAX","FTM","LUNA","BTC","ETH"]

# Buscar preços
precos = pegar_precos()

# Mostrar preços em BRL
for moeda in moedas_lista:
    print(f"\n📊 Preços de {moeda} (BRL):")
    for exchange in precos:
        if moeda in precos[exchange]:
            bid = precos[exchange][moeda]["bid"]
            ask = precos[exchange][moeda]["ask"]
            bidVol = precos[exchange][moeda]["bidVol"]
            askVol = precos[exchange][moeda]["askVol"]
            print(f"{exchange}: bid={bid:.4f} (vol {bidVol}) | ask={ask:.4f} (vol {askVol})")

# Calcular oportunidades de arbitragem
for moeda in moedas_lista:
    asks = {ex: precos[ex][moeda]["ask"] for ex in precos if moeda in precos[ex] and precos[ex][moeda]["ask"] > 0}
    bids = {ex: precos[ex][moeda]["bid"] for ex in precos if moeda in precos[ex] and precos[ex][moeda]["bid"] > 0}

    if len(asks) > 0 and len(bids) > 0:
        ex_compra = min(asks, key=asks.get)
        preco_compra = asks[ex_compra]
        vol_compra = precos[ex_compra][moeda]["askVol"]

        ex_venda = max(bids, key=bids.get)
        preco_venda = bids[ex_venda]
        vol_venda = precos[ex_venda][moeda]["bidVol"]

        if preco_compra > 0:
            spread = (preco_venda - preco_compra) / preco_compra * 100
        else:
            spread = 0

        volume_max = min(vol_compra, vol_venda) if vol_compra and vol_venda else None

        taxa_compra = preco_compra * TAXA / 100
        taxa_venda = preco_venda * TAXA / 100
        lucro_unitario = (preco_venda - preco_compra) - (taxa_compra + taxa_venda)
        lucro_total = lucro_unitario * volume_max if volume_max else None

        status = "💰 Arbitragem lucrativa!" if lucro_unitario > 0 and (lucro_total is None or lucro_total > 0) else "⚠️ Arbitragem não compensa com as taxas."

        print(f"\n🚀 Oportunidade {moeda}: comprar em {ex_compra} e vender em {ex_venda}")
        print(f"Spread bruto: {spread:.2f}%")
        print(f"Lucro unitário (1 {moeda}): R$ {lucro_unitario:.4f}")
        if volume_max:
            print(f"Volume max possível: {volume_max} {moeda}")
            print(f"Lucro total possível: R$ {lucro_total:.2f}")
        else:
            print("Volume não informado para uma das exchanges.")
        print(status)
