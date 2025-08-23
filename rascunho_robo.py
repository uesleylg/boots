import requests

# Dicionário com as exchanges e os endpoints públicos para cada moeda
# Cada chave é o nome da exchange e dentro temos as moedas com suas URLs
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

# Dicionário para armazenar os preços coletados
precos = {}

# Loop para buscar os preços em cada exchange
for exchange, moedas in exchanges.items():
    precos[exchange] = {}  # cria um dicionário vazio para cada exchange
    for moeda, url in moedas.items():
        try:
            # Faz a requisição HTTP para o endpoint da moeda
            data = requests.get(url, timeout=5).json()

            # Cada exchange retorna os dados em formatos diferentes
            if exchange == "binance":
                precos[exchange][moeda] = float(data['price'])  # pega o preço direto
            elif exchange == "coinbase":
                precos[exchange][moeda] = float(data['data']['amount'])  # está dentro de 'data'
            elif exchange == "coinex":
                precos[exchange][moeda] = float(data['data']['ticker']['last'])  # último preço
        except Exception as e:
            print(f"Erro ao pegar preço de {moeda} em {exchange}: {e}")

# Lista de moedas que vamos exibir
moedas_lista = ["TRX","XLM","DOGE","ADA","MATIC","SOL","SHIB","AVAX","FTM","LUNA"]

# Exibir os preços coletados
for moeda in moedas_lista:
    print(f"\n📊 Preços de {moeda} (USD):")
    for exchange in precos:
        if moeda in precos[exchange]:
            print(f"  {exchange}: {precos[exchange][moeda]}")
