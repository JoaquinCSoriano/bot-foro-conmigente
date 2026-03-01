import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # 1. Recuperamos tus secretos de las variables de entorno de GitHub
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        # Lanzamos el navegador en modo invisible (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 2. PROCESO DE LOGIN
        # Vamos a la página de acceso
        page.goto("https://conmigente.es/login")
        
        # Rellenamos los campos usando selectores flexibles para evitar el error del número "-496"
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        
        # Pulsamos Enter para entrar (más fiable que buscar el botón de "Acceder")
        page.keyboard.press("Enter")

        # Esperamos a que la web procese el inicio de sesión
        page.wait_for_load_state("networkidle")

        # 3. NAVEGACIÓN AL FORO (Tu nueva ruta)
        # En lugar de quedarnos en /cuenta/, saltamos directamente a la raíz del foro
        page.goto("https://conmigente.es/community/")
        page.wait_for_load_state("networkidle")
        
        # Capturamos el título de la página para confirmar que estamos en el foro
        titulo_foro = page.title()
        
        # Simulación del resumen que recibirá Zapier
        resumen = f"¡Bot conectado con éxito! Actualmente en: {titulo_foro}"

        # 4. ENVIAR SEÑAL A ZAPIER
        # Tu URL de Webhook específica
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        
        try:
            response = requests.post(webhook_url, json={"resumen": resumen})
            if response.status_code == 200:
                print("Señal enviada a Zapier correctamente.")
        except Exception as e:
            print(f"Error al contactar con Zapier: {e}")

        browser.close()

if __name__ == "__main__":
    run()
