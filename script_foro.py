import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Usamos un agente de navegador humano estándar
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            # 1. Ir al login y esperar a que la página cargue visualmente
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 2. LOGIN HUMANO: No buscamos cajas, usamos la posición del cursor
            # Presionamos TAB para entrar en el primer campo (Usuario)
            page.keyboard.press("Tab")
            page.wait_for_timeout(500)
            page.keyboard.type(user, delay=150)
            
            # Presionamos TAB para ir al segundo campo (Contraseña)
            page.keyboard.press("Tab")
            page.wait_for_timeout(500)
            page.keyboard.type(password, delay=150)
            
            # Presionamos ENTER
            page.keyboard.press("Enter")
            
            # 3. Esperar a que el servidor cree la sesión
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(7000)

            # 4. Ir a la sección de barrancos
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(5000)

            # 5. CAPTURA DE TEXTO
            # Si el login funcionó, el texto del foro estará ahí
            if "soci" in page.content().lower() and "restringida" not in page.content().lower():
                resumen = "LOGUEADO CON ÉXITO:\n" + page.inner_text("body")[:1500]
            else:
                resumen = "El login parece no haber funcionado. Texto actual: " + page.inner_text("body")[:500]

        except Exception as e:
            resumen = f"Error en intento #29: {str(e)}"

        # 6. Envío a Zapier (Request K)
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
