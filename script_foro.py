import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Usamos un agente de navegador muy común para pasar desapercibidos
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            # 1. Acceso con tiempo de espera extendido
            page.goto("https://conmigente.es/login", wait_until="networkidle", timeout=60000)
            
            # 2. LOGIN SIN SELECTORES FIJOS (Presionamos 'Tab' para navegar por los campos)
            page.wait_for_timeout(3000)
            # Hacemos clic en el centro para asegurar que la página tiene el foco
            page.mouse.click(200, 200) 
            
            # Buscamos cualquier input que parezca de usuario
            page.focus('input[type="text"]')
            page.keyboard.type(user, delay=100)
            page.keyboard.press("Tab")
            page.keyboard.type(password, delay=100)
            page.keyboard.press("Enter")
            
            page.wait_for_load_state("networkidle")

            # 3. NAVEGACIÓN A LA SECCIÓN
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/", timeout=60000)
            page.wait_for_timeout(8000)

            # 4. CAPTURA DE TEXTO (Usamos el cuerpo entero si falla el contenedor)
            cuerpo = page.query_selector("body")
            resumen = "LECTURA EXITOSA:\n" + cuerpo.inner_text()[:1500] if cuerpo else "No se pudo leer el cuerpo de la web."

        except Exception as e:
            resumen = f"Error crítico en intento #27: {str(e)}"

        # 5. Envío a Zapier (Request K)
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
