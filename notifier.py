import base64
import logging
from datetime import datetime
from email.message import EmailMessage

import requests

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class TokenRefreshError(Exception):
    """refresh_token inválido/revogado — precisa ser gerado novamente na mão."""


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=10,
    )

    if response.status_code == 400 and response.json().get("error") == "invalid_grant":
        raise TokenRefreshError(
            "refresh_token inválido ou revogado — é necessário reautorizar "
            "o app no Google Cloud e gerar um novo."
        )

    response.raise_for_status()
    return response.json()["access_token"]


def build_email_raw(sender: str, to: str, subject: str, body: str) -> str:
    message = EmailMessage()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject
    message.set_content(body)
    return base64.urlsafe_b64encode(message.as_bytes()).decode()


def send_email(access_token: str, sender: str, to: str, subject: str, body: str) -> None:
    raw = build_email_raw(sender, to, subject, body)
    response = requests.post(
        SEND_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json={"raw": raw},
        timeout=10,
    )
    response.raise_for_status()


def send_status_email(
    *,
    success: bool,
    detail: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    sender: str,
    to: str,
) -> bool:
    """Envia o e-mail de status. Nunca lança exceção — retorna True/False."""
    subject = (
        "[n8n] Reautenticação Gmail OK"
        if success
        else "[n8n] FALHA na reautenticação do Gmail"
    )
    body = (
        f"Status: {'SUCESSO' if success else 'FALHA'}\n"
        f"Horário: {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"Detalhes:\n{detail}"
    )

    try:
        access_token = get_access_token(client_id, client_secret, refresh_token)
        send_email(access_token, sender, to, subject, body)
        logger.info("E-mail de notificação enviado.")
        return True

    except Exception:
        logger.exception("Falha ao enviar e-mail de notificação.")
        return False
