import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Usamos el agente exacto de cuando funcionaba
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        try:
            # 1. Volvemos al login simplificado que funcionó en el #15
            page.goto("https://conmigente.es/login")
            
            # Usamos selectores por nombre, que son más estables que el tipo "text"
            page.wait_for_selector('input[name*="username"]', timeout=20000)
            page.fill('input[name*="username"]', user)
            page.fill('input[name*="password"]', password)
            page.keyboard.press("Enter")
            
            page.wait_for_load_state("networkidle")

            # 2. Navegamos directo a la sección
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(5000)

            # 3. Captura total (Si hay foro, lo mandamos)
            if page.query_selector("#wpforo-wrap"):
                resumen = "CONTENIDO:\n" + page.inner_text("#wpforo-wrap")[:1500]
            else:
                resumen = "Logueado, pero la página de la comunidad no cargó el contenido esperado."

        except Exception as e:
            resumen = f"Fallo en el paso de login/lectura: {str(e)}"

        # 4. Envío a Zapier (Esto generará la Request J)
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
