import os
from dotenv import load_dotenv
from notifier import send_status_message

load_dotenv()

resultado = send_status_message(
    success=True,
    detail="Isso é um teste manual, ignorar.",
    bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
    chat_id=os.getenv("TELEGRAM_CHAT_ID"),
)
print("Enviado com sucesso!" if resultado else "Falhou — confira o log.")
