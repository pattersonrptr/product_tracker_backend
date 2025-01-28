from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings

def send_price_alert(email, ad):
    message = Mail(
        from_email='notificacoes@olxtracker.com',
        to_emails=email,
        subject='Alteração de Preço',
        html_content=f'<strong>{ad.title}</strong> agora custa R$ {ad.price}!'
    )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)
