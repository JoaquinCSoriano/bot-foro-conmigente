import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1. Recuperamos el contexto que NO fallaba
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 2. Login estable (Versión que daba check verde)
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 3. Navegación a la sección de prueba
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_timeout(5000)

        # 4. Capturar enlaces de los temas
        hilos = page.query_selector_all('.wpf-thread-title a, .wpforo-topic-title a')
        urls = [el.get_attribute('href') for el in hilos if el.get_attribute('href')][:2]
        
        cuerpo_email = "REPORTE DE BARRANCOS:\n\n"

        # 5. Lectura de contenido (Aquí es donde por fin veremos texto en Zapier)
        for url in urls:
            page.goto(url)
            page.wait_for_timeout(4000)
            titulo = page.title().split("-")[0].strip()
            
            # Selector infalible para el cuerpo del foro
            post = page.query_selector('#wpforo-wrap')
            texto = post.inner_text().strip() if post else "No se pudo extraer el texto."
            
            cuerpo_email += f"📌 {titulo}\n📝 {texto[:800]}...\n\n" + "-"*30 + "\n\n"

        # 6. Envío a Zapier
        requests.post("https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/", json={"resumen": cuerpo_email})
        browser.close()

if __name__ == "__main__":
    run()
