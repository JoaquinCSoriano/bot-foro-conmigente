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

        # 2. IR A LA SECCIÓN DE PRUEBA / BARRANCOS
        # He puesto la URL exacta que me has pasado
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(4000) # Pausa necesaria para que cargue el contenido dinámico

        # 3. BUSCADOR QUIRÚRGICO (Basado en tu captura del Inspector)
        # Atacamos directamente los títulos de los hilos dentro del wrap de wpForo
        elementos = page.query_selector_all('#wpforo-wrap .wpf-thread-title, #wpforo-wrap .wpforo-topic-title')
        
        lista_temas = []
        for el in elementos:
            texto = el.inner_text().strip()
            if texto and len(texto) > 3:
                lista_temas.append(f"- {texto}")

        # Limpieza de duplicados
        lista_temas = list(dict.fromkeys(lista_temas))

        # 4. PREPARAR EL RESUMEN
        if lista_temas:
            resumen = "¡ÉXITO! Temas detectados:\n\n" + "\n".join(lista_temas[:5])
        else:
            resumen = "El bot no ha detectado los títulos. Estructura detectada: " + page.title()

        # 5. ENVIAR A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": resumen})

        browser.close()

if __name__ == "__main__":
    run()
