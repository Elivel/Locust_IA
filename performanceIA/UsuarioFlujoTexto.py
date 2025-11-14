from locust import task, between, User
from performanceIA.services.session_service import SessionService
from performanceIA.tasks.locust_texto_flow import FlujoTexto

class UsuarioFlujoTexto(User):
    wait_time = between(2, 4)
    host = "https://dev-kairos-frontend.dvpapps.io"  # Requerido por Locust

    def on_start(self):
        app_url = SessionService.obtener_appurl()
        self.driver, self.wait = SessionService.iniciar_navegador(app_url)
        self.flujo = FlujoTexto(self.driver, self.wait)

    @task
    def flujo_textual(self):
        self.flujo.ejecutar_flujo()
