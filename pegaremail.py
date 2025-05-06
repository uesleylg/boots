import requests

# URL da API
url = "http://localhost/api/dados-usuarios"

# Fazer a requisição GET para obter os dados
response = requests.get(url)

# Verificar se a requisição foi bem-sucedida (status code 200)
if response.status_code == 200:
    # Converter a resposta JSON para um dicionário Python
    data = response.json()
    
    # Verificar se 'data' não é None
    if data:
        # Usar um conjunto (set) para garantir que os e-mails sejam únicos
        emails = set()
        for user in data.values():
            email = user.get("email")  # Usar .get() para evitar KeyError
            if email:  # Verificar se o e-mail não é None ou vazio
                emails.add(email.strip())  # Adicionar ao set (remove duplicados automaticamente)
        
        # Salvar os e-mails em um arquivo .txt
        with open("emails.txt", "w") as file:
            for email in emails:
                file.write(email + "\n")
        
        print("E-mails salvos com sucesso no arquivo 'emails.txt'.")
    else:
        print("Nenhum dado encontrado na resposta da API.")
else:
    print(f"Erro ao acessar a API. Código de status: {response.status_code}")
