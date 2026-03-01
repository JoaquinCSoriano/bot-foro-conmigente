import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        try:
            # 1. Vamos al login
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(4000)
            
            # 2. LOGIN CIEGO (Navegando con teclado para evitar bloqueos de selectores)
            page.keyboard.press("Tab") # Saltamos al primer campo
            page.keyboard.type(user, delay=100)
            page.keyboard.press("Tab") # Saltamos al campo contraseña
            page.keyboard.type(password, delay=100)
            page.keyboard.press("Enter")
            
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

            # 3. IR A LA SECCIÓN DE PRUEBA
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(10000) # Esperamos 10s para que carguen los barrancos

            # 4. CAPTURAR EL FORO REAL
            # Buscamos el texto que SÍ queremos ver (los barrancos)
            foro = page.query_selector(".wpforo-main") or page.query_selector("#wpforo-wrap")
            if foro:
                resumen = "BARRANCOS DETECTADOS:\n" + foro.inner_text()[:2000]
            else:
                resumen = "Página cargada, pero sigo viendo: " + page.inner_text("body")[:500]

        except Exception as e:
            resumen = f"Error en intento #28: {str(e)}"

        # 5. Envío a Zapier (Request K)
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
