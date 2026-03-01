import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 1. LOGIN
        page.goto("https://conmigente.es/login", wait_until="networkidle")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        # 2. SECCIÓN DE PRUEBA
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/", wait_until="networkidle")
        page.wait_for_timeout(5000)

        # 3. CAPTURAR CUALQUIER ENLACE DE HILO
        # Buscamos de forma más amplia cualquier enlace que parezca un tema
        enlaces = page.query_selector_all('a[href*="topic"], .wpf-thread-title a, .wpforo-topic-title a')
        urls = [el.get_attribute('href') for el in enlaces if el.get_attribute('href')][:2]

        cuerpo_email = "REPORTE DE CONTENIDO DETALLADO:\n" + "="*30 + "\n\n"

        if not urls:
            # Si no encuentra hilos, enviamos el texto visible de la página principal para no ir vacíos
            cuerpo_email += "No se localizaron hilos. Texto de la página:\n"
            cuerpo_email += page.inner_text()[:500]
        else:
            for url in urls:
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(3000)
                # Capturamos el texto principal del post
                cuerpo_email += f"📌 TÍTULO: {page.title()}\n"
                # Buscamos el div principal del mensaje
                post = page.query_selector('.wpf-post-content, .wpforo-post-content, #wpforo-wrap')
                texto = post.inner_text().strip()[:800] if post else "Texto no extraíble"
                cuerpo_email += f"📝 CONTENIDO:\n{texto}\n" + "-"*30 + "\n\n"

        # 4. ENVÍO FORZADO A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": cuerpo_email})
        print("Datos enviados a Zapier.")
        browser.close()

if __name__ == "__main__":
    run()
