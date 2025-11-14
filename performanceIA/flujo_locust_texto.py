# performanceIA/flujo_locust_texto.py
from locust import User, task, between
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from performanceIA.services.session_service import SessionService
import time


class UsuarioFlujoTexto(User):
    host = "http://localhost"  # requerido por Locust
    wait_time = between(2, 4)

    def on_start(self):
        """Obtiene appUrl, abre el navegador y prepara el teclado"""
        app_url = SessionService.obtener_appurl()
        if not app_url:
            print("❌ No se pudo obtener appUrl.")
            self.environment.runner.quit()
            return

        self.driver, self.wait = SessionService.iniciar_navegador(app_url)
        SessionService.abrir_teclado(self.driver, self.wait)
        print("🧠 Chat listo para interactuar.")

    @task
    def flujo_chat(self):
        try:
        
            # 🔹 2. Escribir “pasar plata”
            campo_texto = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='chat-input']"))
            )
            campo_texto.click()
            time.sleep(5)
            texto = "pasar plata"
            campo_texto.send_keys(texto)
            print(f"✅ Texto escrito: {texto}")

            # 🔹 3. Clic en botón enviar
            boton_enviar = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='btn-send']"))
            )
            boton_enviar.click()
            print("📤 Mensaje enviado correctamente.")

            # 🔹 4. Esperar respuesta de la IA
            time.sleep(6)
            print("🤖 Esperando respuesta de la IA...")

        except Exception as e:
            print("❌ Error en flujo teclado:", e)
    def on_stop(self):
        """Cerrar navegador"""
        print("🧹 Cerrando navegador...")
        try:
            time.sleep(3)
            self.driver.quit()
        except:
            pass
