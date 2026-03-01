import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Usamos el agente de usuario que funcionaba en los éxitos anteriores
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 1. LOGIN (Copiado exactamente de la versión que te daba "Verde")
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 2. SECCIÓN
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_timeout(5000)

        # 3. CAPTURAR ENLACES
        enlaces = page.query_selector_all('.wpf-thread-title a, .wpforo-topic-title a')
        urls = [el.get_attribute('href') for el in enlaces if el.get_attribute('href')][:2]
        
        cuerpo_email = "CONTENIDO DE LOS BARRANCOS:\n\n"

        # 4. CAPTURA DE TEXTO (Aquí está el arreglo para Zapier)
        for url in urls:
            page.goto(url)
            page.wait_for_timeout(4000)
            titulo = page.title().split("-")[0].strip()
            
            # Usamos un selector mucho más amplio para que NO llegue vacío
            post = page.query_selector('#wpforo-wrap')
            texto = post.inner_text().strip() if post else "No se pudo extraer el texto."
            
            cuerpo_email += f"📌 {titulo}\n📝 {texto[:800]}\n\n" + "-"*30 + "\n\n"

        # 5. ENVÍO A ZAPIER
        requests.post("https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/", json={"resumen": cuerpo_email})
        browser.close()

if __name__ == "__main__":
    run()
