import subprocess
import time
from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = r"C:\Automacao\gazeta_do_pneu\chrome-debug"

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

    page.goto("https://api.gpcorpbr.com/signin?redirect=%252F")

    # daqui começam os cliques do n8n