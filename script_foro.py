import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # 1. Recuperamos tus secretos
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        # Lanzamos el navegador
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 2. LOGIN (Proceso ya verificado)
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 3. IR A BARRANCOS
        # Vamos a la URL donde acabas de escribir tu post
        page.goto("https://conmigente.es/community/barrancos/")
        page.wait_for_load_state("networkidle")
        
        # Opcional: Una pequeña espera extra por si la web es lenta cargando los temas
        page.wait_for_timeout(3000)

        # 4. BUSCADOR MEJORADO (Probamos varios anzuelos a la vez)
        # Buscamos por la clase del título Y por los enlaces dentro de los hilos
        elementos = page.query_selector_all('.wpforo-topic-title, .wpf-thread-title a, h3.wpf-thread-title')
        
        lista_temas = []
        for el in elementos:
            texto = el.inner_text().strip()
            # Solo guardamos si tiene texto y no es un duplicado
            if texto and len(texto) > 3:
                lista_temas.append(f"- {texto}")

        # Limpiamos duplicados por si acaso
        lista_temas = list(dict.fromkeys(lista_temas))

        # 5. PREPARAR EL RESUMEN
        if lista_temas:
            # Si encuentra temas, los lista (incluyendo tu nuevo post de "Barranco Pajaruco")
            resumen = "Novedades encontradas en BARRANCOS:\n\n" + "\n".join(lista_temas[:5])
        else:
            # Si falla, nos avisará de que ha entrado pero no ha visto el texto
            resumen = "El bot entró en la sección pero no detectó los títulos. Revisando estructura..."

        # 6. ENVIAR A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": resumen})

        browser.close()

if __name__ == "__main__":
    run()
