from locust import User, task, between, events
from services.session_service import SessionService
from flows.voice_flow import VoiceFlow
import time

class UsuarioFlujoIA(User):
    wait_time = between(10, 15)
    host = "http://localhost"

    def on_start(self):
        self.appUrl = SessionService.obtener_appurl()
        if not self.appUrl:
            print("❌ No se pudo obtener appUrl. Abortando usuario.")
            self.environment.runner.quit()

        self.driver, self.wait = SessionService.iniciar_navegador(self.appUrl)
        self.voice_flow = VoiceFlow(self.driver, self.wait)

    @task
    def flujo_voz(self):
        inicio = time.time()
        exito, duracion = self.voice_flow.ejecutar_flujo()
        if exito:
            events.request_success.fire(
                request_type="flujo_voz",
                name="flujo_selenium",
                response_time=duracion,
                response_length=0
            )
        else:
            events.request_failure.fire(
                request_type="flujo_voz",
                name="flujo_selenium",
                response_time=duracion,
                response_length=0,
                exception=Exception("Flujo fallido")
            )

    def on_stop(self):
        print("🧹 Cerrando navegador...")
        time.sleep(3)
        self.driver.quit()
