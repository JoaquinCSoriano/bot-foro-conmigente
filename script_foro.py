import os
import requests
from playwright.sync_api import sync_playwright

def run():
    user = os.getenv('USER_CONMIGENTE')
    password = os.getenv('PASS_CONMIGENTE')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context() # Creamos un contexto para mantener las cookies
        page = context.new_page()

        # 1. LOGIN
        print("Iniciando sesión...")
        page.goto("https://conmigente.es/login")
        page.fill('input[name^="username-"]', user)
        page.fill('input[name^="user_password-"]', password)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

        # 2. IR A LA SECCIÓN
        page.goto("https://conmigente.es/community/categoria-principal-categoria-principal-categoria-principal-prueba/")
        page.wait_for_timeout(5000)

        # 3. CAPTURAR ENLACES
        hilos = page.query_selector_all('#wpforo-wrap .wpf-thread-title a, #wpforo-wrap .wpforo-topic-title a')
        
        urls_a_leer = []
        for link in hilos:
            url = link.get_attribute('href')
            if url and url not in urls_a_leer:
                urls_a_leer.append(url)
        
        urls_a_leer = urls_a_leer[:3] # Limitamos a los 3 más recientes
        
        cuerpo_email = "DETALLE DE LOS TEMAS SELECCIONADOS:\n"
        cuerpo_email += "="*40 + "\n\n"
        encontrados = 0

        # 4. ENTRAR EN CADA TEMA Y EXTRAER TODO EL TEXTO POSIBLE
        for url in urls_a_leer:
            try:
                print(f"Abriendo tema: {url}")
                tema_page = context.new_page()
                tema_page.goto(url)
                tema_page.wait_for_timeout(4000) # Damos tiempo a que cargue el texto
                
                titulo = tema_page.title().split("-")[0].strip()
                
                # Intentamos varios selectores por si el foro cambia de estructura
                # Buscamos en el contenido del post, en el lado derecho o en el wrapper general
                contenido = tema_page.query_selector('.wpf-post-content, .wpforo-post-content, .wpf-right, #wpforo-wrap')
                
                if contenido:
                    texto_post = contenido.inner_text().strip()
                    # Si el texto es muy largo, lo cortamos para el email pero que se lea lo importante
                    texto_final = (texto_post[:1000] + '...') if len(texto_post) > 1000 else texto_post
                else:
                    texto_final = "No se pudo localizar el área de texto del mensaje."

                cuerpo_email += f"📌 TÍTULO: {titulo}\n"
                cuerpo_email += f"🔗 LINK: {url}\n"
                cuerpo_email += f"📝 CONTENIDO:\n{texto_final}\n"
                cuerpo_email += "-"*40 + "\n\n"
                
                tema_page.close()
                encontrados += 1
            except Exception as e:
                print
                
