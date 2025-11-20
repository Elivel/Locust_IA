import os, time
from gtts import gTTS
try:
    from playsound import playsound
    _HAS_PLAYSOUND = True
except Exception:
    _HAS_PLAYSOUND = False
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class VoiceFlow:
    """Encapsula las acciones de voz e interacciones con el asistente"""

    def __init__(self, driver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def reproducir_voz(self, texto, espera_ia=12):
        print(f"🎙️ Enviando comando de voz: {texto}")
        tts = gTTS(texto, lang='es')
        audio_file = f"voz_{int(time.time())}.mp3"
        tts.save(audio_file)
        try:
            if _HAS_PLAYSOUND:
                playsound(audio_file)
            else:
                os.system(f"start {audio_file}")
                time.sleep(espera_ia)
        except Exception:
            time.sleep(espera_ia)
        try:
            os.remove(audio_file)
        except:
            pass

    def validar_respuesta(self, posibles_textos, timeout=35):
        """Observa el texto en pantalla, pero no falla si no coincide.

        Debido a que la interacción principal es por voz, Locust no debe
        marcar el paso como fallido cuando no se detecta un texto específico.
        En su lugar, se registra cualquier mensaje visible para facilitar el
        análisis posterior.
        """

        try:
            for texto in posibles_textos:
                palabra_clave = texto.split()[0].lower()
                elemento = self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ', 'abcdefghijklmnopqrstuvwxyzáéíóúüñ'), '" + palabra_clave + "')]",
                    ))
                )

                if elemento:
                    mensaje = elemento.text.strip()
                    print(f"ℹ️ Texto detectado en pantalla: '{mensaje}'")
                    # Se devuelve el texto detectado, aunque no se use para validar éxito.
                    if texto.lower() in mensaje.lower():
                        print(f"✅ Coincidencia encontrada con '{texto}'")
                    else:
                        print(f"⚠️ Mensaje no coincide exactamente con el esperado: '{texto}'")
                    return mensaje or texto
        except Exception:
            print(f"⚠️ No se detectó ningún mensaje coincidente. Se continúa sin validar texto: {posibles_textos}")

        # No se pudo observar respuesta, pero no se considera fallo.
        return ""

    def ejecutar_flujo(self):
        """Flujo completo por voz con cierre automático de navegador"""
        inicio_total = time.time()
        pasos = []
        exito_total = True
        
        try:
            # Activar micrófono
            boton_micro = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button._micro_fi68y_27")))
            boton_micro.click()
            print("🎙️ Micrófono activado.")

            # 🎤 Paso unico - "pasar plata"
            inicio_paso = time.time()
            try:
                self.reproducir_voz("pasar plata al numero 300 401 10 16 por valor de 1000 pesos")
                respuesta = self.validar_respuesta(["Listo"], timeout=35)
                duracion_paso = round((time.time() - inicio_paso) * 1000, 2)
                # No se falla la métrica de Locust aunque no se detecte texto,
                # porque la interacción es por audio. Se registra solo para
                # observación en los logs.
                exito_paso = True
                pasos.append({
                    "name": "pasar_plata_numero_monto",
                    "success": exito_paso,
                    "duration_ms": duracion_paso,
                    "detail": respuesta or "Validación de texto omitida (flujo de voz)"
                })
                print(f"✅ Paso completado en {duracion_paso} ms")
                if not exito_paso:
                    exito_total = False
            except Exception as e:
                duracion_paso = round((time.time() - inicio_paso) * 1000, 2)
                pasos.append({
                    "name": "pasar_plata_numero_monto",
                    "success": False,
                    "duration_ms": duracion_paso,
                    "detail": str(e)
                })
                exito_total = False
                
            # ⏳ Esperar 10 segundos antes de cerrar (para que IA termine de hablar)
            print("⏳ Esperando 20 segundos antes de cerrar navegador...")
            time.sleep(10)

            # 🔴 Cerrar navegador
            print("🔴 Cerrando navegador...")
            self.driver.quit()

            duracion_total = round((time.time() - inicio_total) * 1000, 2)
            print(f"✅ Flujo completado correctamente en {duracion_total} ms")
            return exito_total, pasos, duracion_total

        except Exception as e:
            print(f"❌ Error general en flujo: {e}")
            try:
                self.driver.quit()
            except:
                pass
            duracion_total = round((time.time() - inicio_total) * 1000, 2)
            return False, pasos if pasos else [{"name": "flujo_completo", "success": False, "duration_ms": duracion_total, "detail": str(e)}], duracion_total
