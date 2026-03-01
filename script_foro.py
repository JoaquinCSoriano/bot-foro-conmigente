import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. LOGIN
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 2. IR A LA SECCIÓN DE BARRANCOS
        # Usamos la URL directa para ir más rápido
        page.goto("https://conmigente.es/community/barrancos/")
        page.wait_for_load_state("networkidle")

        # 3. EXTRAER LOS TÍTULOS DE LOS TEMAS
        # Buscamos los elementos que contienen los nombres de los hilos
        temas = page.query_selector_all('.wpforo-topic-title')
        
        lista_temas = []
        for tema in temas[:5]: # Leemos los 5 más recientes
            texto = tema.inner_text().strip()
            lista_temas.append(f"- {texto}")

        if lista_temas:
            resumen = "Novedades en BARRANCOS:\n" + "\n".join(lista_temas)
        else:
            resumen = "No se han encontrado temas nuevos en Barrancos hoy."

        # 4. ENVIAR A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": resumen})

        browser.close()

if __name__ == "__main__":
    run()
