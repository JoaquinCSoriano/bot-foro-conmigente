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
        print("Iniciando sesión...")
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 2. IR A LA SECCIÓN DE BARRANCOS
        url_seccion = "https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/"
        page.goto(url_seccion)
        page.wait_for_timeout(5000) # Tiempo para carga de hilos

        # 3. CAPTURAR ENLACES DE LOS TEMAS
        # Buscamos los enlaces (<a>) que contienen los títulos
        enlaces = page.query_selector_all('#wpforo-wrap .wpf-thread-title a, #wpforo-wrap .wpforo-topic-title a')
        
        # Guardamos las URLs (máximo 3 para no saturar el correo)
        urls_a_leer = []
        for link in enlaces:
            url = link.get_attribute('href')
            if url and url not in urls_a_leer:
                urls_a_leer.append(url)
        
        urls_a_leer = urls_a_leer[:3] # Limitamos a los 3 más recientes
        
        cuerpo_completo = "DETALLE DE NOVEDADES ENCONTRADAS:\n"
        cuerpo_completo += "="*30 + "\n\n"

        # 4. ENTRAR EN CADA TEMA Y LEER EL CONTENIDO
        for url in urls_a_leer:
            try:
                print(f"Leyendo tema: {url}")
                page.goto(url)
                page.wait_for_timeout(3000)
                
                titulo = page.title().split("-")[0].strip()
                # Buscamos el texto del primer mensaje del foro
                contenido = page.query_selector('.wpf-post-content, .wpforo-post-content')
                texto_post = contenido.inner_text().strip() if contenido else "No se pudo extraer el texto."
                
                cuerpo_completo += f"TÍTULO: {titulo}\n"
                cuerpo_completo += f"CONTENIDO:\n{texto_post}\n"
                cuerpo_completo += "-"*30 + "\n\n"
            except Exception as e:
                print(f"Error leyendo {url}: {e}")

        # 5. ENVIAR TODO A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        
        if not urls_a_leer:
            cuerpo_completo = "No se encontraron temas nuevos para leer."

        print(f"Enviando contenido detallado a Zapier...")
        response = requests.post(webhook_url, json={"resumen": cuerpo_completo})
        print(f"Respuesta Zapier: {response.status_code}")

        browser.close()

if __name__ == "__main__":
    run()
