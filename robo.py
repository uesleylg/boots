import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Defina as informações da conta
smtp_server = "smtp.hostinger.com"  # Servidor SMTP da Hostinger
smtp_port = 465  # Porta SMTP segura
email_sender = "no-reply@bolaplaytv.com.br"  # Seu endereço de e-mail
email_password = "789456123Numlock@"  # Sua senha de e-mail
email_receiver = "mateusoaresdomumbaba@gmail.com"  # E-mail do destinatário

# Defina o nome e o endereço de e-mail do remetente
sender_name = "Bola Play TV"
sender_email = "no-reply@bolaplaytv.com.br"  # E-mail do remetente
sender = f"{sender_name} <{sender_email}>"

# Criando a mensagem
message = MIMEMultipart()
message["From"] = sender  # Usando o nome e o e-mail do remetente
message["To"] = email_receiver
message["Subject"] = "Jogo Ao Vivo Hoje no BolaPlayTV"

# Corpo do e-mail em HTML
body = """
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f8f8f8; padding: 20px;">
    <table style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
      <tr>
        <td style="text-align: center; ">
           <img src="https://bolaplaytv.com.br/img/banner_bolaplaytv.jpg" alt="Imagem do Jogo" style="max-width: 100%;  ">
       <div style="padding: 20px;">
          <h1 style="color: #ff6a00;">🎉 Jogo Ao Vivo Hoje! ⚽</h1>
          <p style="color: #333333; font-size: 16px;">Não deixe passar a emoção do jogo ao vivo! Acompanhe cada lance, cada jogada, e cada gol sem interrupções. Assista <b>sem anúncios</b>, com a qualidade e a emoção que você merece, só na <b>BolaPlayTV!</b> (bolaplaytv.com.br)</p>
      </div>
        </td>
      </tr>
      <tr>
        <td style="padding: 20px; text-align: center; background-color: #000c4f; color: #ffffff; border-radius: 0 0 8px 8px;">
          <p style="font-size: 14px;">Clique abaixo para assistir ao vivo:</p><br>
          <a href="https://bolaplaytv.com.br/" style="text-decoration: none; background-color: #ffffff; color: #ff6a00; padding: 12px 25px; border-radius: 4px; font-weight: bold;">Assistir Agora</a>
        
        </td>
      </tr>
    </table>
  </body>
</html>
"""

# Anexando o corpo HTML à mensagem
message.attach(MIMEText(body, "html"))

# Estabelecendo uma conexão segura com o servidor SMTP
context = ssl.create_default_context()

# Enviando o e-mail
try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, message.as_string())
        print("E-mail enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {e}")
