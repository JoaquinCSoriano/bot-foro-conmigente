import os
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')
    
    # Obtenemos la fecha de hoy en el formato que suele usar el foro (ej: "marzo 01, 2026" o "hoy")
    hoy = datetime.now().strftime("%d/%m/%Y") 

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. LOGIN
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 2. IR A LA SECCIÓN
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_timeout(5000)

        # 3. BUSCAR HILOS DE HOY
        # Seleccionamos las filas de los temas
        hilos = page.query_selector_all('.wpf-thread-row, .wpforo-topic-row')
        
        cuerpo_email = "RESUMEN DE PUBLICACIONES DE HOY:\n"
        cuerpo_email += "="*35 + "\n\n"
        encontrados = 0

        for hilo in hilos:
            # Verificamos si la fecha del hilo contiene "hoy" o la fecha actual
            texto_fila = hilo.inner_text().lower()
            if "hoy" in texto_fila or "1 min" in texto_fila or "ahora" in texto_fila:
                link_element = hilo.query_selector('.wpf-thread-title a, .wpforo-topic-title a')
                if link_element:
                    url = link_element.get_attribute('href')
                    titulo = link_element.inner_text().strip()
                    
                    # Entramos a leer el contenido
                    new_page = browser.new_page()
                    new_page.goto(url)
                    new_page.wait_for_timeout(3000)
                    
                    contenido_html = new_page.query_selector('.wpf-post-content, .wpforo-post-content')
                    texto_post = contenido_html.inner_text().strip() if contenido_html else "Contenido no disponible."
                    
                    cuerpo_email += f"📌 TÍTULO: {titulo}\n"
                    cuerpo_email += f"📝 CONTENIDO:\n{texto_post}\n"
                    cuerpo_email += "-"*35 + "\n\n"
                    
                    new_page.close()
                    encontrados += 1

        if encontrados == 0:
            cuerpo_email = "No se han encontrado publicaciones nuevas realizadas hoy."

        # 4. ENVÍO A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        requests.post(webhook_url, json={"resumen": cuerpo_email})
        print(f"Proceso finalizado. Temas de hoy enviados: {encontrados}")

        browser.close()

if __name__ == "__main__":
    run()
