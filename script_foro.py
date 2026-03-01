import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # Recuperamos tus secretos de forma segura
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Ir al login
        page.goto("https://conmigente.es/login") # Ajusta esta URL si es distinta
        page.fill('input[name="username"]', user) # "fill" escribe en el campo
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]') # "click" pulsa el botón
        
        # 2. Esperar a que cargue y buscar novedades
        page.wait_for_load_state("networkidle")
        # Aquí el script recogería los textos de los foros (Scraping)
        resumen = "Aquí van las novedades encontradas hoy..."
        
        # 3. ENVIAR A ZAPIER (Un solo envío al día = 1 sola tarea)
        # Sustituye la URL de abajo por tu "Catch Hook" de Zapier
        webhook_url = "TU_URL_DE_ZAPIER_AQUÍ"
        requests.post(webhook_url, json={"resumen": resumen})
        
        browser.close()

if __name__ == "__main__":
    run()
