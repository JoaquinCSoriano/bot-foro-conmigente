import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Usamos el agente de usuario que nos ha mantenido en verde
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        try:
            # 1. Ir al login con espera generosa
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 2. LOGIN: Usamos selectores genéricos para evitar el Timeout
            # Buscamos cualquier campo que sea de tipo texto o password
            page.fill('input[type="text"]', user)
            page.fill('input[type="password"]', password)
            page.keyboard.press("Enter")
            
            # Espera crítica para que el servidor procese la sesión
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

            # 3. IR A LA SECCIÓN DE PRUEBA (Ya como socio logueado)
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(5000)

            # 4. CAPTURA DEL CONTENIDO
            # Si el login funcionó, veremos el contenedor del foro
            if page.query_selector("#wpforo-wrap"):
                resumen = "CONTENIDO RECUPERADO:\n" + page.inner_text("#wpforo-wrap")[:1500]
            else:
                # Si seguimos fuera, capturamos qué está viendo el bot para diagnosticar
                resumen = f"Login fallido o acceso denegado. Texto visible: {page.inner_text('body')[:500]}"

        except Exception as e:
            resumen = f"Error en ejecución #28: {str(e)}"

        # 5. Envío a Zapier (Esto generará la Request K)
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
