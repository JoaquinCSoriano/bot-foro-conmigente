import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # Recuperamos tus secretos de GitHub
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. LOGIN
        print("Iniciando sesión en ConMiGente...")
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 2. IR A LA SECCIÓN DE PRUEBA
        print("Entrando en la sección de Barrancos...")
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_timeout(5000)

        # 3. CAPTURAR ENLACES DE LOS TEMAS (Sin filtro de fecha)
        hilos = page.query_selector_all('#wpforo-wrap .wpf-thread-title a, #wpforo-wrap .wpforo-topic-title a')
        
        urls_a_leer = []
        for link in hilos:
            url = link.get_attribute('href')
            if url and url not in urls_a_leer:
                urls_a_leer.append(url)
        
        urls_a_leer = urls_a_leer[:3] # Limitamos a los 3 más recientes para el test
        
        cuerpo_email = "DETALLE COMPLETO DE LOS ÚLTIMOS BARRANCOS:\n"
        cuerpo_email += "="*40 + "\n\n"
        encontrados = 0

        # 4. ENTRAR EN CADA TEMA Y EXTRAER EL TEXTO
        for url in urls_a_leer:
            try:
                print(f"Leyendo contenido de: {url}")
                new_page = browser.new_page()
                new_page.goto(url)
                new_page.wait_for_timeout(3000)
                
                titulo = new_page.title().split("-")[0].strip()
                # Localizamos el contenido del mensaje
                contenido_html = new_page.query_selector('.wpf-post-content, .wpforo-post-content')
                texto_post = contenido_html.inner_text().strip() if contenido_html else "Contenido no disponible."
                
                cuerpo_email += f"📌 TÍTULO: {titulo}\n"
                cuerpo_email += f"📝 CONTENIDO:\n{texto_post}\n"
                cuerpo_email += "-"*40 + "\n\n"
                
                new_page.close()
                encontrados += 1
            except Exception as e:
                print(f"Error al leer el tema {url}: {e}")

        if encontrados == 0:
            cuerpo_email = "No se ha podido extraer información de los temas."

        # 5. ENVIAR A ZAPIER
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        print("Enviando reporte detallado a Zapier...")
        response = requests.post(webhook_url, json={"resumen": cuerpo_email})
        
        if response.status_code == 200:
            print(f"¡ÉXITO! Zapier ha recibido los datos de {encontrados} temas.")
        else:
            print(f"Fallo en el envío. Código: {response.status_code}")

        browser.close()

if __name__ == "__main__":
    run()
