import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    response = requests.post(
        TELEGRAM_URL.format(token=bot_token),
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    response.raise_for_status()


def send_status_message(
    *,
    success: bool,
    detail: str,
    bot_token: str,
    chat_id: str,
) -> bool:
    """Envia o status via Telegram. Nunca lança exceção — retorna True/False."""
    title = (
        "✅ Reautenticação Gmail OK"
        if success
        else "🚨 FALHA na reautenticação do Gmail"
    )
    text = (
        f"{title}\n"
        f"Horário: {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"Detalhes:\n{detail}"
    )

    try:
        send_telegram_message(bot_token, chat_id, text)
        logger.info("Mensagem de notificação enviada ao Telegram.")
        return True

    except Exception:
        logger.exception("Falha ao enviar mensagem de notificação ao Telegram.")
        return False
