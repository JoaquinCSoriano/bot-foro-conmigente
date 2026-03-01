import os
import requests
from playwright.sync_api import sync_playwright

def run():
    # 1. Recuperamos tus secretos de GitHub
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        # Lanzamos el navegador
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 2. LOGIN (Proceso verificado)
        print("Iniciando sesión en ConMiGente...")
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 3. IR A LA SECCIÓN DE PRUEBA
        print("Entrando en la sección de Barrancos...")
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_load_state("networkidle")
        
        # Pausa de 4 segundos para que aparezcan los títulos dinámicos
        page.wait_for_timeout(4000) 

        # 4. BUSCADOR QUIRÚRGICO (Basado en tu captura del Inspector)
        # Atacamos directamente los títulos de los hilos dentro del wrap de wpForo
        elementos = page.query_selector_all('#wpforo-wrap .wpf-thread-title, #wpforo-wrap .wpforo-topic-title')
        
        lista_temas = []
        for el in elementos:
            texto = el.inner_text().strip()
            if texto and len(texto) > 3:
                lista_temas.append(f"- {texto}")

        # Limpieza de duplicados
        lista_temas = list(dict.fromkeys(lista_temas))

        # 5. PREPARAR EL RESUMEN
        if lista_temas:
            resumen = "¡ÉXITO! Temas detectados:\n\n" + "\n".join(lista_temas[:5])
        else:
            resumen = f"El bot no ha detectado los títulos. Título de página: {page.title()}"

        # 6. ENVIAR A ZAPIER CON REPORTE DE ERRORES
        webhook_url = "https://hooks.zapier.com/hooks/catch/26578118/u0s07g6/"
        
        print(f"Enviando este contenido a Zapier:\n{resumen}")
        
        try:
            response = requests.post(webhook_url, json={"resumen": resumen})
            if response.status_code == 200:
                print(f"¡PETICIÓN ENVIADA! Zapier ha respondido: {response.text}")
            else:
                print(f"ERROR EN EL ENVÍO: Código de estado {response.status_code}")
        except Exception as e:
            print(f"OCURRIÓ UN ERROR TÉCNICO AL ENVIAR: {e}")

        browser.close()

if __name__ == "__main__":
    run()
