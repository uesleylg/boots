import requests

# Taxa da exchange (em %)
TAXA = 0.1  # 0,1%

# Exchanges e endpoints públicos
exchanges = {
    "binance": {
        "TRX": "https://api.binance.com/api/v3/ticker/price?symbol=TRXUSDT",
        "XLM": "https://api.binance.com/api/v3/ticker/price?symbol=XLMUSDT",
        "DOGE": "https://api.binance.com/api/v3/ticker/price?symbol=DOGEUSDT",
        "ADA": "https://api.binance.com/api/v3/ticker/price?symbol=ADAUSDT",
        "MATIC": "https://api.binance.com/api/v3/ticker/price?symbol=MATICUSDT",
        "SOL": "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT",
        "SHIB": "https://api.binance.com/api/v3/ticker/price?symbol=SHIBUSDT",
        "AVAX": "https://api.binance.com/api/v3/ticker/price?symbol=AVAXUSDT",
        "FTM": "https://api.binance.com/api/v3/ticker/price?symbol=FTMUSDT",
        "LUNA": "https://api.binance.com/api/v3/ticker/price?symbol=LUNAUSDT"
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
        "LUNA": "https://api.coinbase.com/v2/prices/LUNA-USD/spot"
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
        "LUNA": "https://api.coinex.com/v1/market/ticker?market=LUNAUSDT"
    }
}

# Buscar preços
precos = {}
for exchange, moedas in exchanges.items():
    precos[exchange] = {}
    for moeda, url in moedas.items():
        try:
            data = requests.get(url, timeout=5).json()
            if exchange == "binance":
                precos[exchange][moeda] = float(data['price'])
            elif exchange == "coinbase":
                precos[exchange][moeda] = float(data['data']['amount'])
            elif exchange == "coinex":
                precos[exchange][moeda] = float(data['data']['ticker']['last'])
        except Exception as e:
            print(f"Erro ao pegar preço de {moeda} em {exchange}: {e}")

# Mostrar preços
moedas_lista = ["TRX","XLM","DOGE","ADA","MATIC","SOL","SHIB","AVAX","FTM","LUNA"]

for moeda in moedas_lista:
    print(f"\nPreços de {moeda} (USD):")
    for exchange in precos:
        if moeda in precos[exchange]:
            print(f"{exchange}: {precos[exchange][moeda]}")

# Calcular spread máximo e lucro líquido
for moeda in moedas_lista:
    moeda_precos = {ex: precos[ex][moeda] for ex in precos if moeda in precos[ex]}
    if len(moeda_precos) > 1:
        mais_barato = min(moeda_precos, key=moeda_precos.get)
        mais_caro = max(moeda_precos, key=moeda_precos.get)
        preco_compra = moeda_precos[mais_barato]
        preco_venda = moeda_precos[mais_caro]

        # Spread bruto (%)
        spread = (preco_venda - preco_compra) / preco_compra * 100

        # Cálculo das taxas
        taxa_compra = preco_compra * TAXA / 100
        taxa_venda = preco_venda * TAXA / 100
        lucro_liquido = (preco_venda - preco_compra) - (taxa_compra + taxa_venda)

        if lucro_liquido > 0:
            status = "💰 Arbitragem lucrativa!"
        else:
            status = "⚠️ Arbitragem não compensa com as taxas."

        print(f"\nMaior oportunidade de arbitragem {moeda}: comprar em {mais_barato} e vender em {mais_caro}")
        print(f"Spread bruto: {spread:.2f}%")
        print(f"Lucro líquido considerando taxas: {lucro_liquido:.6f} USD")
        print(status)
