import os
from datetime import date
from playwright.sync_api import sync_playwright, TimeoutError


hoy = date.today().strftime("%Y-%m-%d")

LOGIN_URL = "https://360.altanredes.com/login"
TARGET_URL = "https://360.altanredes.com/operations/reactivation"


USER = os.getenv("VIEW360_USER")
PASS = os.getenv("VIEW360_PASSWORD")

def preactivar_linea(msisdn: str) -> dict:
    if len(msisdn) != 10:
        return {"status": "error", "message": "El número ingresado es incorrecto"}
    else:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                            channel="chromium",  # fuerza el Chromium de Playwright
                            headless=True,  # 👈 abre el navegador visible
                            #slow_mo=1000,    # 👈 cada acción tarda 1s, así lo ves paso a paso
                            args=[  "--no-sandbox",
                                    "--disable-gpu",
                                    "--disable-dev-shm-usage",
                                    "--disable-blink-features=AutomationControlled",
                                    "--no-first-run",
                                    "--no-default-browser-check",
                                    "--disable-default-apps",
                                    "--disable-features=TranslateUI",
                                    "--disable-ipc-flooding-protection"]
                        )
            
            context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        
            

            #page = browser.new_page()

            page = context.new_page()

            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en']});
        """)
        

            # login
            page.goto(LOGIN_URL, wait_until="networkidle")
            page.wait_for_selector("#email", timeout=60000)
            page.fill("#email", USER)
            page.fill("#password", PASS)
            page.click("#consulta")  # botón login
            page.wait_for_selector("nav", timeout=20000)  # o algo del dashboard que aparezca solo después del login
            page.wait_for_load_state("networkidle")

            # ir a la sección
            page.goto(TARGET_URL, wait_until="networkidle")
            # llenar msisdn
            page.fill("#inputData", msisdn)
            page.click("#next")
            page.wait_for_timeout(3000) # esperar 3 segundos a que cargue

            try:
                # intentamos esperar el campo fecha
                page.wait_for_selector("#txtDate", timeout=5000)
                print("📅 La línea existe, se debe llenar la fecha.")
                
                # si llega aquí es porque encontró el input de fecha
                page.fill("#txtDate", hoy)  # Ejemplo de fecha
                page.click("#finish")
                
                # esperar resultado
                page.wait_for_selector("label", timeout=20000)

                # obtener el texto del label dentro de ese div
                mensaje = page.inner_text("#message label").strip().lower()

                if "no exitosa" in mensaje:
                    print("❌ Reactivación no exitosa:", mensaje)
                    return {"status": "danger", "message": mensaje}

                elif "se realizó con éxito" in mensaje:
                    print("✅ Reactivación exitosa:", mensaje)
                    return {"status": "success", "message": mensaje}

                else:
                    print("❓ Mensaje desconocido:", mensaje)
                    return {"status": "danger", "message": "No se encontró mensaje de resultado"}

            except TimeoutError:
                # si no aparece el campo fecha, revisamos si salió el mensaje de error
                try:
                    page.wait_for_selector("label.help-block", timeout=3000)
                    mensaje_error = page.inner_text("label.help-block strong")
                    print("❌ Error:", mensaje_error)
                    return {"status": "not_found", "message": mensaje_error}
                
                except TimeoutError:
                    print("❓ No se encontró ni fecha ni mensaje de error (revisar la lógica).")
                    
                    return {"status": "danger", "message": "❓ No se encontró ni fecha ni mensaje de error (revisar la lógica)."}
                
        return {"status": "unknown", "message": "Ocurrió un error desconocido. Consulte al administrador."}
