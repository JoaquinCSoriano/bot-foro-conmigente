import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # Recuperamos tus secretos
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Ir al login y rellenar campos
        page.goto("https://conmigente.es/login")
        # Estos ya funcionan (confirmado en tu último log)
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        
        # TRUCO: En lugar de buscar el botón, simplemente pulsamos "Enter"
        page.keyboard.press("Enter")

        # 2. Esperar a que la web procese el login y cargue la siguiente página
        page.wait_for_load_state("networkidle")
        
        # Simulación del resumen
        resumen = "¡Bot funcionando! El login ha sido un éxito."

        # 3. ENVIAR A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": resumen})

        browser.close()

if __name__ == "__main__":
    run()
