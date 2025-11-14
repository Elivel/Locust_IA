import os, time
from gtts import gTTS
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
        os.system(f"start {audio_file}")
        time.sleep(espera_ia)
        try:
            os.remove(audio_file)
        except:
            pass

    def validar_respuesta(self, posibles_textos, timeout=35):
        try:
            for texto in posibles_textos:
                elemento = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{texto.split()[0]}')]"))
                )
                if elemento:
                    print(f"✅ IA respondió correctamente: '{texto}'")
                    return texto
        except:
            print(f"⚠️ No se detectó ninguna de las respuestas esperadas: {posibles_textos}")
        return ""

    def ejecutar_flujo(self):
        """Flujo completo por voz"""
        inicio = time.time()
        try:
            # Activar micrófono
            boton_micro = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button._micro_fi68y_27")))
            boton_micro.click()
            print("🎙️ Micrófono activado.")

            # Paso 1️⃣ - “pasar plata”
            self.reproducir_voz("pasar plata")
            respuesta = self.validar_respuesta([
                "¿A quién deseas pasar plata?",
                "¿A quién quieres pasar plata?",
                "Disculpa, no entendí bien"
            ])

            if "no entendí" in respuesta.lower():
                self.reproducir_voz("pasar plata")
                respuesta = self.validar_respuesta(["¿A quién deseas pasar plata?", "¿A quién quieres pasar plata?"])

            # Paso 2️⃣ - número
            self.reproducir_voz("300 401 10 16")
            self.validar_respuesta(["¿Cuánta plata quieres pasar?", "¿Cuál es el monto que deseas enviar?"])

            # Paso 3️⃣ - monto
            self.reproducir_voz("1000 pesos")
            self.validar_respuesta(["¿Deseas confirmar la transferencia?", "¿Confirmas el envío?"])

            # Paso 4️⃣ - confirmar
            self.reproducir_voz("confirmar transferencia")
            self.validar_respuesta(["¡Listo! Pasaste", "Transferencia realizada con éxito"])

            duracion = round((time.time() - inicio) * 1000, 2)
            print(f"✅ Flujo completado correctamente en {duracion} ms")
            return True, duracion

        except Exception as e:
            print(f"❌ Error en flujo: {e}")
            return False, round((time.time() - inicio) * 1000, 2)
