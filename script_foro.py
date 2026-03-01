import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    # SEÑAL DE VIDA: Esto debería generar la Request H de inmediato
    requests.post(webhook_url, json={"resumen": "Iniciando proceso de scraping... buscando datos."})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        try:
            # LOGIN (El que ya funciona y da verde)
            page.goto("https://conmigente.es/login", wait_until="domcontentloaded")
            page.wait_for_selector('input[type="text"]', timeout=20000)
            page.fill('input[name^="username-"]', user)
            page.fill('input[name^="user_password-"]', password)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")

            # NAVEGACIÓN
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(5000)

            # LECTURA
            contenido = page.inner_text("#wpforo-wrap") if page.query_selector("#wpforo-wrap") else "Foro cargado pero vacío."
            resultado = f"DATOS EXTRAÍDOS:\n{contenido[:1500]}"

        except Exception as e:
            resultado = f"Error capturado: {str(e)}"

        # ENVÍO FINAL: Esto debería actualizar la Request H con los datos reales
        requests.post(webhook_url, json={"resumen": resultado})
        browser.close()

if __name__ == "__main__":
    run()
