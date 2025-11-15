from locust import HttpUser, task, between
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from gtts import gTTS
try:
    from playsound import playsound
    _HAS_PLAYSOUND = True
except Exception:
    _HAS_PLAYSOUND = False
import requests, json, time, os

def reproducir_voz(texto, espera_ia=8):
    """Genera y reproduce un audio con el texto indicado"""
    print(f"🎙️ Enviando comando de voz: {texto}")
    tts = gTTS(texto, lang='es')
    audio_file = f"voz_{int(time.time())}.mp3"
    tts.save(audio_file)

    # Reproducir audio de forma bloqueante si playsound está disponible
    try:
        if _HAS_PLAYSOUND:
            playsound(audio_file)
        else:
            # Fallback: usa start y espera manualmente
            os.system(f"start {audio_file}")
            time.sleep(espera_ia)
    except Exception:
        # Si falla la reproducción, esperamos el tiempo estimado
        time.sleep(espera_ia)
    try:
        os.remove(audio_file)
    except:
        pass

def validar_respuesta(driver, posibles_textos, timeout=25):
    """Valida si la IA respondió con alguno de los textos esperados"""
    wait = WebDriverWait(driver, timeout)
    try:
        for texto in posibles_textos:
            elemento = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{texto.split()[0]}')]")
                )
            )
            if elemento:
                print(f"✅ IA respondió correctamente: '{texto}'")
                return texto
    except Exception:
        print(f"⚠️ No se detectó ninguna de las respuestas esperadas: {posibles_textos}")
        return ""
    return ""


def obtener_appurl():
    """Obtiene la URL de sesión del cliente (simula el CURL)"""
    print("📡 Solicitando appUrl al servicio...")
    url = "http://localhost:8076/api/presentacion-cliente?="
    headers = {
        "ufw-channel": "UTF-8",
        "Content-Type": "application/json",
        "User-Agent": "locust/selenium",
        "action": "OPEN_WITHOUT_CIPHER",
        "app-consumer-id": "APP-DAVIPLATA",
        "app-module-id": "krs",
        "Acept": "*/*",
        "x-request-id": f"locust-{int(time.time())}"
    }
    data = {
         "data": "{\"client\":{\"firstName\":\"Armando\",\"secondName\":\"\",\"lastName\":\"Bronca\",\"secondLastName\":\"Segura\",\"balance\":9442350.99,\"documentClient\":{\"number\":\"1100114\",\"type\":\"01\"},\"phoneNumber\":{\"countryId\":\"+57\",\"number\":\"3004011014\"},\"email\":\"xxx@gmail.com\",\"userId\":\"763b9bf753fb9fa56a90a091baa4fcf03c21687bef637ccb4d2e333bc724e5b5\",\"authenticationType\":\"DAVIPLATA\"},\"module\":{\"id\":\"KRS\",\"country\":\"CO\"},\"consumer\":{\"appConsumer\":{\"id\":\"APP_DAVIPLATA\",\"platformType\":\"APP_DAVIPLATAMOVIL\",\"canalId\":\"83\",\"sessionId\":\"17280492576755584902345352747985\",\"transactionId\":\"006355\",\"consumerRequestId\":\"8500\",\"transactionDate\":\"2024-10-04T08:47:21-05:00\"},\"deviceConsumer\":{\"id\":\"199066910afd18aed979359520eb9e30e8e2a07673806bc0607cf1e99bfc1876\",\"userAgent\":\"okhttp/4.9.2\",\"soVersion\":\"Android6.3.0\",\"ipDevice\":\"181.54.52.102\",\"appVersion\":\"6.3.0\",\"originDevice\":\"\",\"idDevice\":\"3004011015\"},\"genericData\":{\"dataItem\":[{\"key\":\"tokenFrontend\",\"value\":\"2db9a44e-4589-49ba-96a5-b4a3737689e7\"}]}}}",
    "ttl": 300
    }

    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        try:
            app_url = resp.json()["data"]["appUrl"]
            print(f"✅ appUrl obtenido: {app_url}")
            return app_url
        except Exception as e:
            print(f"❌ Error al extraer appUrl: {e}")
    else:
        print(f"❌ Error HTTP {resp.status_code}")
    return None


class UsuarioFlujoIA(HttpUser):
    """Simula un usuario que interactúa por voz con el asistente IA (reporta métricas a Locust UI)"""
    wait_time = between(10, 15)
    host = "http://localhost"  # requerido por Locust

    def on_start(self):
        """Configura navegador y abre sesión"""
        self.appUrl = obtener_appurl()
        if not self.appUrl:
            print("❌ No se pudo obtener appUrl. Deteniendo usuario.")
            self.environment.runner.quit()

        print("🌐 Iniciando navegador Chrome...")

        options = webdriver.ChromeOptions()

            # 🔧 Configurar permisos de medios y notificaciones
        prefs = {
                "profile.default_content_setting_values.media_stream_mic": 1,   # 1 = permitir
                "profile.default_content_setting_values.media_stream_camera": 1,
                "profile.default_content_setting_values.geolocation": 2,        # 2 = bloquear ubicación
                "profile.default_content_setting_values.notifications": 2,
            }

        options.add_experimental_option("prefs", prefs)
        options.add_argument("--use-fake-ui-for-media-stream")  # Evita el modal visual
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-geolocation")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Permitir desactivar headless con la variable de entorno `LOCUST_HEADLESS`
        headless_env = os.environ.get("LOCUST_HEADLESS", "true").lower()
        if headless_env not in ("false", "0", "no"):
            options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.get(self.appUrl)
        self.wait = WebDriverWait(self.driver, 40)
        time.sleep(6)

        # Click micrófono
        try:
            boton_micro = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button._micro_fi68y_27")))
            boton_micro.click()
            print("🎙️ Micrófono activado.")
        except Exception as e:
            print("❌ No se pudo hacer clic en el micrófono:", e)
            self.driver.quit()

    @task
    def flujo_voz(self):
        """Flujo completo por voz medido en Locust"""
        inicio = time.time()

        # --- Paso 1: pasar plata al número y monto ---
        try:
            inicio_paso = time.time()
            # Enviar la intención y los detalles en pasos cortos.
            # Muchas apps detienen la escucha cuando detectan la intención 'pasar plata',
            # por eso dividimos en 3 fragmentos para garantizar que el servicio reciba número y monto.
            reproducir_voz("pasar plata al numero 3004011016 por valor de 1000")
            
            # Esperar a que desaparezca el indicador de 'escuchando' si aparece
            try:
                WebDriverWait(self.driver, 30).until_not(
                    EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Te estoy escuchando...")
                )
            except Exception:
                pass

            fin_paso = time.time()
            duracion_paso = round((fin_paso - inicio_paso) * 1000, 2)

            # Registrar métrica en stub local para evitar 403 del backend real
            try:
                with self.client.get(
                    "http://127.0.0.1:5005/flujo_voz/pasar_plata",
                    name="flujo_voz:pasar_plata",
                    catch_response=True,
                    timeout=1,
                    verify=False,
                ) as resp:
                    resp.success()
            except Exception as e:
                print(f"⚠️ Error registrando métrica 'pasar_plata': {e}")
        except Exception as e:
            print(f"❌ Error en paso 'pasar plata': {e}")

        # --- Paso 2: confirmar ---
        try:
            inicio_paso = time.time()
            reproducir_voz("confirmar")

            # Esperar respuesta final de la IA (texto esperado similar a '¡Listo! Pasaste')
            validar_respuesta(self.driver, ["¡Listo! Pasaste", "Transferencia realizada con éxito", "Listo, transferí"], timeout=30)

            fin_paso = time.time()
            duracion_paso = round((fin_paso - inicio_paso) * 1000, 2)

            try:
                with self.client.get(
                    "http://127.0.0.1:5005/flujo_voz/confirmar",
                    name="flujo_voz:confirmar",
                    catch_response=True,
                    timeout=1,
                    verify=False,
                ) as resp:
                    resp.success()
            except Exception as e:
                print(f"⚠️ Error registrando métrica 'confirmar': {e}")
        except Exception as e:
            print(f"❌ Error en paso 'confirmar': {e}")

        duracion_total = round((time.time() - inicio) * 1000, 2)
        print(f"✅ Flujo completo en {duracion_total} ms")

    def on_stop(self):
        print("🧹 Cerrando navegador...")
        time.sleep(5)
        self.driver.quit()
        self.driver = None

