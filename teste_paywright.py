import subprocess
import time
import os

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

load_dotenv(r"C:/Automacao/gazeta_do_pneu/.env")

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PROFILE = r"C:/Automacao/gazeta_do_pneu/chrome-debug"

N8N_URL = os.getenv("N8N_URL")
N8N_USER = os.getenv("N8N_USER")
N8N_PASSWORD = os.getenv("N8N_PASSWORD")

#Verificando se as variáveis existem
if not all([N8N_URL, N8N_USER, N8N_PASSWORD]):
        raise ValueError("Variáveis obrigatórias não encontradas no .env")

# 1. Abre o Chrome em modo debug
subprocess.Popen([
    CHROME,
    "--remote-debugging-port=9222",
    f"--user-data-dir={PROFILE}"
])

# 2. Aguarda Chrome iniciar
time.sleep(3)

# 3. Playwright conecta
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    context = browser.contexts[0]

    page = context.new_page()

    page.goto(N8N_URL)
    try:
        page.locator("#emailOrLdapLoginId").wait_for(
            state="visible",
            timeout=5000
        )

        page.locator("#emailOrLdapLoginId").fill(N8N_USER)
        page.locator("#password").fill(N8N_PASSWORD)
        page.get_by_role("button", name="Sign in").click()

    except PlaywrightTimeoutError:
        print("Já está logado no n8n.")