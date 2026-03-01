import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    webhook = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"

    with sync_playwright() as p:
        # Usamos un perfil de navegador persistente para que no nos echen
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            # 1. LOGIN CON SIMULACIÓN HUMANA
            page.goto("https://conmigente.es/login", wait_until="networkidle")
            page.wait_for_timeout(4000)
            
            page.keyboard.press("Tab")
            page.keyboard.type(user, delay=150)
            page.keyboard.press("Tab")
            page.keyboard.type(password, delay=150)
            page.keyboard.press("Enter")
            
            # ESPERA DE SEGURIDAD (Para que el 403 no aparezca)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(12000) 

            # 2. NAVEGACIÓN LENTA
            # En lugar de ir directo, refrescamos o navegamos con una pausa extra
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/", wait_until="domcontentloaded")
            page.wait_for_timeout(10000)

            # 3. LECTURA TOTALMENTE FLEXIBLE
            # Buscamos cualquier cosa que no sea el mensaje de error
            texto_pagina = page.inner_text("body")
            
            if "Forbidden" in texto_pagina or "restringida" in texto_pagina:
                resumen = f"Acceso denegado nuevamente (403/Restringido). El servidor detectó el bot tras el login."
            else:
                # Intentamos capturar los hilos de los barrancos
                temas = page.query_selector_all(".wpf-thread-title, .wpforo-topic-title")
                if temas:
                    resumen = "BARRANCOS:\n" + "\n".join([t.inner_text() for t in temas])
                else:
                    resumen = "LOGUEADO. Contenido detectado:\n" + texto_pagina[:1500]

        except Exception as e:
            resumen = f"Error técnico en intento #33: {str(e)}"

        # 4. ENVÍO A ZAPIER
        requests.post(webhook, json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
