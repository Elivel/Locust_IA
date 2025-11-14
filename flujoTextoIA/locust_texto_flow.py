from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def _now_ms():
    return round(time.time() * 1000, 2)


class FlujoTexto:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def escribir_texto(self, texto):
        """Hace clic en el campo de texto y escribe el mensaje"""
        start = _now_ms()
        try:
            campo = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='chat-input']"))
            )
            campo.click()
            time.sleep(0.5)
            campo.send_keys(texto)
            print(f"✏️ Texto enviado: {texto}")

            # clic en el botón de enviar
            boton_enviar = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='btn-send']"))
            )
            boton_enviar.click()
            print("📤 Mensaje enviado correctamente.")
            return True, round(_now_ms() - start, 2)
        except Exception as e:
            print(f"⚠️ No se pudo escribir o enviar el texto '{texto}': {e}")
            return False, round(_now_ms() - start, 2)

    def obtener_ultima_respuesta(self):
        """Obtiene el último mensaje del bot"""
        try:
            mensajes = self.driver.find_elements(By.CSS_SELECTOR, "div._message_164qe_42")
            if mensajes:
                ultimo = mensajes[-1].text.strip()
                print(f"🤖 Respuesta IA: {ultimo}")
                return ultimo
            return ""
        except Exception as e:
            print(f"⚠️ Error al leer mensaje IA: {e}")
            return ""

    def esperar_respuesta(self, segundos=8):
        """Esperar antes de validar respuesta"""
        print(f"⏱️ Esperando {segundos}s por la respuesta de la IA...")
        time.sleep(segundos)

    def ejecutar_flujo(self):
        """Flujo completo texto a texto. Devuelve (exito_total, pasos)

        pasos: lista de dicts con keys: name, success (bool), duration_ms, detail
        """
        print("🚀 Iniciando flujo textual con la IA...")
        pasos = []

        # 🔹 1. Abrir teclado Kairos
        start = _now_ms()
        try:
            boton_teclado = self.wait.until(EC.element_to_be_clickable((By.ID, "keyboard-kairos")))
            boton_teclado.click()
            duration = round(_now_ms() - start, 2)
            print("⌨️ Teclado Kairos abierto.")
            pasos.append({"name": "abrir_teclado", "success": True, "duration_ms": duration, "detail": ""})
        except Exception as e:
            duration = round(_now_ms() - start, 2)
            print(f"⚠️ No se pudo abrir el teclado: {e}")
            pasos.append({"name": "abrir_teclado", "success": False, "duration_ms": duration, "detail": str(e)})

        # 🔹 2. Enviar "pasar plata"
        start = _now_ms()
        ok, dur = self.escribir_texto("pasar plata")
        # esperar y leer respuesta
        self.esperar_respuesta(3)
        respuesta = self.obtener_ultima_respuesta().strip().lower()
        success = any(p.lower() in respuesta for p in ["¿a quién deseas pasar plata?", "¿a quién quieres pasar plata?" ])
        duration_total = round(_now_ms() - start, 2)
        pasos.append({"name": "pasar_plata", "success": success and ok, "duration_ms": duration_total, "detail": respuesta})

        # 🔹 3. Enviar número de contacto
        start = _now_ms()
        ok_num, dur_num = self.escribir_texto("3004011016")
        self.esperar_respuesta(4)
        respuesta = self.obtener_ultima_respuesta().strip()
        duration_total = round(_now_ms() - start, 2)
        if "¿Cuánta" in respuesta or "cuánta" in respuesta.lower():
            pasos.append({"name": "decir_numero", "success": True and ok_num, "duration_ms": duration_total, "detail": respuesta})
            # Enviar monto
            start = _now_ms()
            ok_monto, dur_monto = self.escribir_texto("1000")
            self.esperar_respuesta(3)
            respuesta_monto = self.obtener_ultima_respuesta().strip()
            duration_monto = round(_now_ms() - start, 2)
            pasos.append({"name": "decir_monto", "success": ok_monto, "duration_ms": duration_monto, "detail": respuesta_monto})
        else:
            pasos.append({"name": "decir_numero", "success": False, "duration_ms": duration_total, "detail": respuesta})

        # 🔹 4. Confirmar transferencia (texto o botón)
        start = _now_ms()
        ok_conf, dur_conf = self.escribir_texto("confirmar")
        self.esperar_respuesta(3)
        final = self.obtener_ultima_respuesta().strip()
        success_conf = "¡listo" in final.lower() or "transferencia realizada" in final.lower()
        duration_final = round(_now_ms() - start, 2)
        pasos.append({"name": "confirmar_transferencia", "success": success_conf and ok_conf, "duration_ms": duration_final, "detail": final})

        exito_total = all(p["success"] for p in pasos)
        print("🏁 Fin del flujo textual.")
        return exito_total, pasos
    def confirmar_envio(self):
        """Confirma la transferencia cuando la IA pregunta si deseas confirmar"""
        try:
            print("💬 Esperando mensaje de confirmación de la IA...")
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '¿Confirmas que deseas pasar')]")
                )
            )
            print("✅ La IA solicitó confirmación, procediendo a hacer clic en el check.")

            boton_check = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div._buttons_f59dq_106[data-testid='btn-check']")
                    )
                )
            boton_check.click()
            print("🖱️ Clic realizado en el botón check correctamente.")

            time.sleep(3)

            self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(text(), '¡Listo! Pasaste') or contains(text(), 'Transferencia realizada con éxito')]")
                )
            )
            print("🎉 ¡Transferencia confirmada exitosamente!")
        except Exception as e:
            print(f"⚠️ Error durante la confirmación de la transferencia: {e}")   
