from locust import HttpUser, task, between
from services.session_service import SessionService
from flows.voice_flow import VoiceFlow
import time

class UsuarioFlujoIA(HttpUser):
    wait_time = between(10, 15)
    host = "http://127.0.0.1:5005"  # Stub local para métricas

    def on_start(self):
        self.appUrl = SessionService.obtener_appurl()
        if not self.appUrl:
            print("❌ No se pudo obtener appUrl. Abortando usuario.")
            self.environment.runner.quit()

        self.driver, self.wait = SessionService.iniciar_navegador(self.appUrl)
        self.voice_flow = VoiceFlow(self.driver, self.wait)

    @task
    def flujo_voz(self):
        exito_total, pasos, duracion_total = self.voice_flow.ejecutar_flujo()
        
        # Registrar cada paso como métrica separada en Locust para visualizar en Statistics
        for paso in pasos:
            try:
                with self.client.get(
                    f"/flujo_voz/{paso['name']}",
                    name=f"flujo_voz:{paso['name']}",
                    catch_response=True,
                    timeout=1,
                    verify=False
                ) as resp:
                    if paso['success']:
                        resp.success()
                    else:
                        resp.failure(paso.get('detail', 'Paso fallido'))
            except Exception as e:
                print(f"⚠️ Error registrando métrica '{paso['name']}': {e}")
        
        # Registrar métrica total del flujo
        try:
            with self.client.get(
                "/flujo_voz/completo",
                name="flujo_voz:flujo_completo",
                catch_response=True,
                timeout=1,
                verify=False
            ) as resp:
                if exito_total:
                    resp.success()
                else:
                    resp.failure("Flujo de voz falló")
        except Exception as e:
            print(f"⚠️ Error registrando métrica total: {e}")

    def on_stop(self):
        print("🧹 Cerrando navegador...")
        time.sleep(3)
        self.driver.quit()
