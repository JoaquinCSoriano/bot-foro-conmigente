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
            # 1. Vamos al login y esperamos 5 segundos para que cargue todo
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 2. LOGIN CIEGO: Usamos TAB para navegar, evitando selectores dinámicos
            page.keyboard.press("Tab") 
            page.keyboard.type(user, delay=120)
            page.keyboard.press("Tab")
            page.keyboard.type(password, delay=120)
            page.keyboard.press("Enter")
            
            # Espera larga para que el servidor valide la sesión de socio
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(8000)

            # 3. IR A LA SECCIÓN DE PRUEBA
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
            page.wait_for_timeout(5000)

            # 4. CAPTURAR EL TEXTO REAL
            if "restringida" not in page.content().lower():
                # Buscamos el contenedor principal de los temas
                foro = page.query_selector("#wpforo-wrap")
                resumen = "CONTENIDO DE SOCIO DETECTADO:\n\n" + foro.inner_text()[:1500] if foro else "Logueado pero sin contenedor visible."
            else:
                resumen = "El login falló de nuevo. Sigue apareciendo zona restringida."

        except Exception as e:
            resumen = f"Error en ejecución #30: {str(e)}"

        # 5. Envío a Zapier (Esto generará la Request K o L)
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
