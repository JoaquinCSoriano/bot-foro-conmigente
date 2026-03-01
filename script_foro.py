import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # Recuperamos tus secretos de forma segura
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        # Lanzamos el navegador
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Ir al login y rellenar campos
        # Usamos ^= para que el bot busque el campo que EMPIEZA por ese nombre
        # Así ignoramos el número "-496" que la web añade al final
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        
        # Hacemos clic en el botón de Acceder usando su ID flexible
        page.click('input[id^="um-submit-btn-"]')

        # 2. Esperar a que cargue la página tras el login
        page.wait_for_load_state("networkidle")
        
        # Simulación del resumen (en el futuro aquí irá el código de lectura de posts)
        resumen = "Aquí van las novedades encontradas hoy..."

        # 3. ENVIAR A ZAPIER
        # He incluido tu URL exacta de Zapier para que no tengas que tocar nada
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": resumen})

        browser.close()

if __name__ == "__main__":
    run()
