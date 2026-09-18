import subprocess
import time
import os
import logging
import traceback
from pathlib import Path

from notifier import send_status_message

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOGS_DIR / "n8n_credential_renewer.log", encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

CHROME = os.getenv("CHROME")
PROFILE = os.getenv("PROFILE")

LOGIN_NAME = os.getenv("LOGIN_NAME")
DOMINIO = os.getenv("DOMINIO")
GMAIL_CREDENTIAL_N8N = os.getenv("GMAIL_CREDENTIAL_N8N")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

N8N_URL = os.getenv("N8N_URL")
N8N_USER = os.getenv("N8N_USER")
N8N_PASSWORD = os.getenv("N8N_PASSWORD")

# Verifica se as credenciais estão válidas se não o programa encerra aqui
if not all([N8N_URL, N8N_USER, N8N_PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    raise ValueError(
        "Variáveis obrigatórias não encontradas no .env"
    )


subprocess.Popen([
    CHROME,
    "--remote-debugging-port=9222",
    #"headless=new",
    f"--user-data-dir={PROFILE}"
])

time.sleep(3)


status_ok = False
error_detail = ""

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    try:
        context = browser.contexts[0]
        # Fecha guias antigas caso tenham ficado abertas
        for old_page in context.pages:
            old_page.close()

        page = context.new_page()

        # Acessar n8n
        page.goto(N8N_URL)

        # Fazer login, somente se necessário
        try:
            email = page.locator("#emailOrLdapLoginId")

            email.wait_for(
                state="visible",
                timeout=5000
            )

            email.fill(N8N_USER)

            page.locator("#password").fill(
                N8N_PASSWORD
            )

            page.get_by_role(
                "button",
                name="Sign in"
            ).click()

        except PlaywrightTimeoutError:
            logger.info("Já está logado no n8n.")

        # Abrir aba de credencial
        page.get_by_role(
            "link",
            name="Credentials"
        ).click()

        page.get_by_text(
            GMAIL_CREDENTIAL_N8N,
            exact=True
        ).click()

        # Desconecta a credencial do google
        page.get_by_text(
            "Disconnect",
            exact=True
        ).click()

        confirm_button = page.locator(
            "button.btn--confirm"
        )

        confirm_button.wait_for(
            state="visible"
        )

        confirm_button.click()

        # Conecta novamente a credencial
        with page.expect_popup() as popup_info:
            page.get_by_role(
                "button",
                name="Sign in with Google"
            ).click()

        google_page = popup_info.value

        # Interação com popup de confirmação
        google_page.get_by_text(
            LOGIN_NAME,
            exact=True
        ).click()

        google_page.get_by_role(
            "link",
            name="Avançado"
        ).click()

        google_page.get_by_role(
            "link",
            name=DOMINIO
        ).click()

        # Se necessário, ceder permisões de reativação
        try:
            checkbox = google_page.get_by_role(
                "checkbox",
                name="Selecionar tudo"
            )

            checkbox.wait_for(
                state="visible",
                timeout=3000
            )

            checkbox.check()

        except PlaywrightTimeoutError:
            logger.info("Checkbox não apareceu.")

        google_page.get_by_text(
            "Continuar",
            exact=True
        ).click()

        logger.info("Reautenticação concluída.")

    except Exception:
        error_detail = traceback.format_exc()
        logger.error("Falha no fluxo de reautenticação:\n%s", error_detail)

    else:
        status_ok = True

    # Fecha as páginas abertas
    finally:
        page.close()
        browser.close()

send_status_message(
    success=status_ok,
    detail="Reautenticação concluída com sucesso." if status_ok else error_detail,
    bot_token=TELEGRAM_BOT_TOKEN,
    chat_id=TELEGRAM_CHAT_ID,
)