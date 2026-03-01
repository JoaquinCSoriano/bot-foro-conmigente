import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Disfraz avanzado: engañamos al servidor sobre quiénes somos
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="es-ES",
            timezone_id="Europe/Madrid"
        )
        page = context.new_page()

        try:
            # 1. Login con pausas humanas (150ms por tecla)
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            page.keyboard.press("Tab")
            page.keyboard.type(user, delay=150)
            page.wait_for_timeout(1000)
            page.keyboard.press("Tab")
            page.keyboard.type(password, delay=150)
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            
            # ESPERA CRÍTICA: Dejamos que el servidor "nos crea"
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(15000) 

            # 2. Navegación a la zona de socios
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(10000)

            # 3. Lectura del contenido
            if "Forbidden" in page.content() or "restringida" in page.content().lower():
                resumen = "BLOQUEO PERSISTENTE: El servidor sigue identificando el flujo como bot tras el login."
            else:
                # Buscamos el contenido real
                cuerpo = page.query_selector("#wpforo-wrap")
                resumen = "ÉXITO TOTAL:\n\n" + cuerpo.inner_text()[:2000] if cuerpo else "Logueado pero el foro no cargó."

        except Exception as e:
            resumen = f"Error en intento final #34: {str(e)}"

        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
