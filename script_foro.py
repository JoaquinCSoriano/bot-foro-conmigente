import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # Recuperamos tus credenciales seguras
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        # Iniciamos el navegador con el 'agente' que ya sabemos que no bloquea
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. LOGIN (Usamos selectores más flexibles para evitar el Timeout)
            page.goto("https://conmigente.es/login", wait_until="domcontentloaded")
            
            # Esperamos a que el input exista antes de intentar escribir
            page.wait_for_selector('input[type="text"], input[name*="user"]', timeout=20000)
            
            page.type('input[type="text"], input[name*="user"]', user, delay=100)
            page.type('input[type="password"]', password, delay=100)
            page.keyboard.press("Enter")
            
            # Esperamos a que el login procese (como en tu versión exitosa #15)
            page.wait_for_load_state("networkidle")

            # 2. IR A LA SECCIÓN DE PRUEBA
            page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/", wait_until="networkidle")
            page.wait_for_timeout(5000)

            # 3. CAPTURAR EL TEXTO (Para que no llegue vacío a Zapier)
            # En lugar de buscar hilos uno a uno, capturamos lo que se ve en pantalla
            contenido_visible = page.inner_text("#wpforo-wrap") if page.query_selector("#wpforo-wrap") else "No se detectó el contenedor del foro."
            
            resumen = f"ESTADO DEL FORO:\n\n{contenido_visible[:1000]}"

        except Exception as e:
            # Si algo falla, el bot NO dará aspa roja. Enviará el error a Zapier para que lo leas.
            resumen = f"El bot no pudo completar la lectura: {str(e)}"

        # 4. ENVÍO A ZAPIER
        requests.post("https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/", json={"resumen": resumen})
        browser.close()

if __name__ == "__main__":
    run()
