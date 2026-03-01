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
            # 1. LOGIN (Ya sabemos que funciona)
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(4000)
            page.keyboard.press("Tab")
            page.keyboard.type(user, delay=100)
            page.keyboard.press("Tab")
            page.keyboard.type(password, delay=100)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(6000)

            # 2. IR A LA SECCIÓN DE BARRANCOS
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            
            # EL CAMBIO CLAVE: Esperamos hasta 20 segundos a que aparezca el foro
            page.wait_for_selector("#wpforo-wrap", timeout=20000)
            
            # 3. CAPTURA DE LOS TEMAS
            temas = page.query_selector_all(".wpf-thread-title, .wpforo-topic-title")
            if temas:
                titulos = [t.inner_text().strip() for t in temas]
                resumen = "BARRANCOS ENCONTRADOS:\n\n" + "\n".join(titulos)
            else:
                # Si no hay temas específicos, capturamos el texto general del foro
                resumen = "LOGUEADO. Texto del foro:\n" + page.inner_text("#wpforo-wrap")[:1500]

        except Exception as e:
            resumen = f"Logueado, pero el contenido tardó mucho: {str(e)}"

        # 4. ENVÍO FINAL A ZAPIER
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
