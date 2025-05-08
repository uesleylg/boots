import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configurações SMTP
smtp_server = "smtp.hostinger.com"
smtp_port = 465
email_sender = "no-reply@bolaplaytv.com.br"
email_password = "789456123Numlock@"

# Nome do remetente
sender_name = "Bola Play TV"
sender_email = email_sender
sender = f"{sender_name} <{sender_email}>"

# Corpo do e-mail em HTML
body = """
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f8f8f8; padding: 20px;">
    <table style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
       
        <tr>
         
        <td style="text-align: center; ">
            <img src="https://bolaplaytv.com.br/img/banner_bolaplaytv.jpg" alt="Imagem do Jogo" style="max-width: 100%; border-radius: 8px; ">
        <div style="padding: 20px;">
            <h1 style="color: #ff6a00;">Você Vai Assistir GRÁTIS!</h1>
            <p style="color: #333333; font-size: 16px;"><b>BolaPlayTV</b> está de volta, trazendo uma nova maneira de assistir aos seus jogos favoritos com qualidade excepcional e sem interrupções de anúncios!</p>
            <p style="color: #333333; font-size: 16px;"><b>E o melhor:</b> Use o código abaixo e assista totalmente de graça com um bônus exclusivo para você!</p>
            <p style="font-weight: bold; color: #ff6a00; font-size: 18px;">Seu código de bônus: <b>NGNPY</b></p>
            
       </div>
        </td>
      </tr>
      <tr>
        <td style="padding: 20px; text-align: center; background-color: #ff6a00; color: #ffffff; border-radius: 0 0 8px 8px;">
          <p style="font-size: 14px; ">Clique abaixo para assistir ao vivo:</p> <br>
          <a href="https://bolaplaytv.com.br" style=" text-decoration: none; background-color: #ffffff; color: #ff6a00; padding: 12px 25px; border-radius: 4px; font-weight: bold;">Assistir Agora</a>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

# Lê os e-mails do arquivo
with open("emails.txt", "r") as f:
    email_list = [line.strip() for line in f if line.strip()]

# Conexão segura com o servidor SMTP
context = ssl.create_default_context()

try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(email_sender, email_password)
        for email_receiver in email_list:
            # Cria a mensagem para cada destinatário
            message = MIMEMultipart()
            message["From"] = sender
            message["To"] = email_receiver
            message["Subject"] = "FUTEBOL AO VIVO GRÁTIS"
            message.attach(MIMEText(body, "html"))

            # Envia o e-mail individualmente
            server.sendmail(email_sender, email_receiver, message.as_string())
            print(f"E-mail enviado para: {email_receiver}")

except Exception as e:
    print(f"Erro ao enviar e-mails: {e}")
