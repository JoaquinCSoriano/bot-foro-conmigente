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
            # 1. LOGIN HUMANO (Mantenemos lo que funcionó en el #30)
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(5000)
            page.keyboard.press("Tab")
            page.keyboard.type(user, delay=120)
            page.keyboard.press("Tab")
            page.keyboard.type(password, delay=120)
            page.keyboard.press("Enter")
            
            # ESPERA CRÍTICA: Damos 10 segundos para que el foro reconozca al socio
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(10000)

            # 2. IR A LOS BARRANCOS
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(10000) # 10 segundos de carga visual

            # 3. CAPTURA FLEXIBLE
            # Si no encuentra el contenedor del foro, captura el body completo
            contenido = page.query_selector("#wpforo-wrap")
            if contenido:
                resumen = "BARRANCOS DETECTADOS:\n\n" + contenido.inner_text()[:2000]
            else:
                texto_total = page.inner_text("body")
                if "restringida" in texto_total.lower():
                    resumen = "El login falló: El servidor sigue enviando a zona restringida."
                else:
                    resumen = "LOGUEADO (Lectura General):\n\n" + texto_total[:2000]

        except Exception as e:
            resumen = f"Error en ejecución #32: {str(e)}"

        # 4. ENVÍO A ZAPIER
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
