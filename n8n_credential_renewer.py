import subprocess
import time
import os

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)
from dotenv import load_dotenv


load_dotenv(r"C:/Automacao/gazeta_do_pneu/.env")

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PROFILE = r"C:/Automacao/gazeta_do_pneu/chrome-debug"

N8N_URL = os.getenv("N8N_URL")
N8N_USER = os.getenv("N8N_USER")
N8N_PASSWORD = os.getenv("N8N_PASSWORD")

# Verifica se as credenciais estão válidas se não o programa encerra aqui
if not all([N8N_URL, N8N_USER, N8N_PASSWORD]):
    raise ValueError(
        "Variáveis obrigatórias não encontradas no .env"
    )


subprocess.Popen([
    CHROME,
    "--remote-debugging-port=9222",
    f"--user-data-dir={PROFILE}"
])

time.sleep(3)


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
            print("Já está logado no n8n.")

        # Abrir aba de credencial
        page.get_by_role(
            "link",
            name="Credentials"
        ).click()

        page.get_by_text(
            "Gmail Henrique",
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
            "henriquegp",
            exact=True
        ).click()

        google_page.get_by_role(
            "link",
            name="Avançado"
        ).click()

        google_page.get_by_role(
            "link",
            name="Acessar gpcorpbr.com (não seguro)"
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
            print("Checkbox não apareceu.")

        google_page.get_by_text(
            "Continuar",
            exact=True
        ).click()

        print("Reautenticação concluída.")

    # Fecha as páginas abertas
    finally:
        page.close()
        browser.close()