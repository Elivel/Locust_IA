# performanceIA/flujo_texto_locust.py
from locust import task, between, HttpUser
from flujoTextoIA.session_service import SessionService
from flujoTextoIA.locust_texto_flow import FlujoTexto
import time


class UsuarioFlujoTexto(HttpUser):
    """
    Usuario Locust que abre el navegador y ejecuta el flujo de texto con IA
    """
    wait_time = between(2, 4)
    host = "https://dev-kairos-frontend.dvpapps.io"  # obligatorio para Locust

    def on_start(self):
        print("🚀 Inicializando flujo con navegador...")
        # 1️⃣ Obtener URL con token
        app_url = SessionService.obtener_appurl()

        # 2️⃣ Abrir navegador en esa URL (¡aquí se abre Chrome!)
        self.driver, self.wait = SessionService.iniciar_navegador(app_url)

        # 3️⃣ Preparar flujo de interacción textual
        self.flujo = FlujoTexto(self.driver, self.wait)

    @task
    def flujo_textual(self):
        """Ejecuta el flujo completo con la IA y reporta métricas a Locust"""
        inicio = time.time()
        exito, pasos = self.flujo.ejecutar_flujo()

        # Reportar cada paso como una métrica a Locust (para que aparezca en el HTML)
        print("\n" + "="*70)
        print("📊 RESULTADO DEL FLUJO TEXTUAL")
        print("="*70)
        for paso in pasos:
            name = paso.get("name")
            duration = paso.get("duration_ms")
            success = paso.get("success")
            detail = paso.get("detail", "")
            
            status = "✅" if success else "❌"
            print(f"{status} {name:25} | Duración: {duration:8}ms | Respuesta: {detail[:50]}")
            
            # Registrar en Locust usando catch_response para marcar éxito/fallo
            try:
                with self.client.get(
                    f"/flujo_texto/{name}",
                    name=f"flujo_texto_{name}",
                    timeout=1,
                    verify=False,
                    catch_response=True
                ) as resp:
                    if success:
                        resp.success()  # Marca como éxito
                    else:
                        resp.failure(detail)  # Marca como fallo con detalles
            except Exception as e:
                # Si falla el reporte, al menos log en consola
                print(f"⚠️ Error registrando paso '{name}': {e}")
        
        # Métrica de flujo completo
        duracion_total = int((time.time() - inicio) * 1000)
        status_total = "✅ ÉXITO" if exito else "❌ FALLÓ"
        print("="*70)
        print(f"Estado Final: {status_total} | Tiempo Total: {duracion_total}ms")
        print("="*70 + "\n")
        
        # Reportar flujo completo a Locust
        try:
            with self.client.get(
                "/flujo_texto/completo",
                name="flujo_texto_completo",
                timeout=1,
                verify=False,
                catch_response=True
            ) as resp:
                if exito:
                    resp.success()
                else:
                    resp.failure("Flujo incompleto o con pasos fallidos")
        except Exception as e:
            print(f"⚠️ Error registrando flujo completo: {e}")
    
    def on_stop(self):
        """Cerrar navegador al finalizar"""
        print("🧹 Cerrando navegador...")
        try:
            self.driver.quit()
        except:
            pass
