# performanceIA/services/session_service.py
import requests
import time
import csv
import random
import os
import json
from selenium import webdriver
# 💡 Importación necesaria: Importamos Options desde selenium.webdriver.chrome.options
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SessionService:
    
    @staticmethod
    def cargar_datos_csv():
        """Lee DATA_Kairos.csv ubicado en la misma carpeta"""
        ruta_carpeta = os.path.dirname(__file__)
        ruta_csv = os.path.join(ruta_carpeta,"DATA_Kairos.csv")

        datos = []
        with open(ruta_csv, "r", encoding="utf-8") as file:
            lector = csv.DictReader(file, delimiter=";")
            for fila in lector:
                datos.append(fila)

        return datos

    @staticmethod
    def obtener_appurl():
        """Llama al backend y obtiene un appUrl con token nuevo"""
        print("📡 Solicitando appUrl al servicio...")
        usuario = random.choice(SessionService.cargar_datos_csv())
        documento = usuario["NumDocumento"]
        celular = usuario["NumCelular"]
        payload = {
            "client": {
                "firstName": "Armando",
                "secondName": "",
                "lastName": "Bronca",
                "secondLastName": "Segura",
                "balance": 1000,
                "documentClient": {"number": documento, "type": "01"},
                "phoneNumber": {"countryId": "+57", "number": celular},
                "email": "xxx@gmail.com",
                "userId": "763b9bf753fb9fa56a90a091baa4fcf03c21687bef637ccb4d2e333bc724e5b5",
                "authenticationType": "DAVIPLATA"
            },
            "module": {"id": "KRS", "country": "CO"},
            "consumer": {
                "appConsumer": {
                    "id": "APP_DAVIPLATA",
                    "platformType": "APP_DAVIPLATAMOVIL",
                    "canalId": "83",
                    "sessionId": "123456",
                    "transactionId": "006355",
                    "consumerRequestId": "8500",
                    "transactionDate": "2024-10-04T08:47:21-05:00"
                },
                "deviceConsumer": {
                    "id": documento,
                    "userAgent": "okhttp/4.9.2",
                    "soVersion": "Android6.3.0",
                    "ipDevice": "181.54.52.102",
                    "appVersion": "6.3.0",
                    "originDevice": "",
                    "idDevice": celular
                },
                "genericData": {
                    "dataItem": [
                        {"key": "tokenFrontend", "value": "2db9a44e-4589-49ba-96a5-b4a3737689e7"},
                        {"key": "br", "value": "true"}
                    ]
                }
            }
        }
        # ... (Tu código para obtener appUrl - No se modifica) ...
        data ={"data": json.dumps(payload), "ttl": 300}
        url = "http://localhost:8076/api/presentacion-cliente?="
        headers = {
            "ufw-channel": "UTF-8",
            "Content-Type": "application/json",
            "User-Agent": "locust/selenium",
            "action": "OPEN_WITHOUT_CIPHER",
            "app-consumer-id": "APP-DAVIPLATA",
            "app-module-id": "krs",
            "Accept": "*/*",
            "x-request-id": f"locust-{int(time.time())}"
        }
        resp = requests.post(url, headers=headers, json=data)   
        if resp.status_code == 200:
            return resp.json()["data"]["appUrl"]

        print("❌ Error", resp.text)
        return None     


        for intento in range(3):
            try:
                resp = requests.post(url, headers=headers, json=data, timeout=10)
                if resp.status_code == 200 and "appUrl" in resp.text:
                    app_url = resp.json()["data"]["appUrl"]
                    print(f"✅ appUrl obtenido correctamente (intento {intento+1}): {app_url}")
                    return app_url
                else:
                    print(f"⚠️ Intento {intento+1}: error HTTP {resp.status_code} o respuesta inválida.")
            except Exception as e:
                print(f"❌ Error al solicitar appUrl: {e}")
            time.sleep(2)

        print("❌ No se pudo obtener un appUrl válido tras varios intentos.")
        return None

    @staticmethod
    def iniciar_navegador(app_url):
        """Abre Chrome y espera que cargue el chatbot"""
        print("🌐 Iniciando navegador...")

        # Inicializa las opciones de Chrome
        options = Options()

        # =========================================================================
        # 🎯 CORRECCIONES PARA EVITAR EL ERROR 'DevToolsActivePort file doesn't exist'
        # =========================================================================

        # 1. Modo Headless: configurable vía variable de entorno `LOCUST_HEADLESS`.
        # Por defecto el script ejecuta en headless (valor por defecto: 'true').
        headless_env = os.environ.get("LOCUST_HEADLESS", "true").lower()
        if headless_env not in ("false", "0", "no"):
            options.add_argument("--headless=new")
        # options.add_argument("--headless") # Opcional: usar esta si la anterior falla

        # 2. Argumentos de Estabilidad (Cruciales en entornos como Docker o CI/CD, pero útiles aquí)
        options.add_argument("--no-sandbox")                  # Desactiva el entorno de seguridad, útil si hay problemas de permisos.
        options.add_argument("--disable-dev-shm-usage")       # Soluciona problemas de memoria compartida en ciertos entornos.
        options.add_argument("--disable-gpu")                # Deshabilita la aceleración por hardware (menos importante en headless).

        # 3. Argumentos de Limpieza y Rendimiento
        options.add_argument("--window-size=1920,1080")      # Establece un tamaño base para el modo headless.
        options.add_argument("--disable-extensions")         # Deshabilita cualquier extensión instalada.
        options.add_argument("--disable-infobars")           # Evita barras de notificación.
        options.add_argument("--disable-notifications")      # Deshabilita notificaciones push.
        options.add_argument("--disable-geolocation")        # Deshabilita geolocalización.
        
        # 4. Argumentos para el Stream (los de tu código original)
        options.add_argument("--use-fake-ui-for-media-stream")  # Acepta micrófono automáticamente
        # Si tienes problemas con el micrófono real, podrías necesitar simularlo:
        # options.add_argument("--use-fake-device-for-media-stream") 

        # NOTA: Se eliminan las líneas de "user-data-dir" y "profile-directory" (que estaban comentadas)
        # para asegurar que no haya un conflicto residual al intentar cargar un perfil de usuario.

        # =========================================================================
        
        try:
            # Si tienes problemas de compatibilidad (Paso 1 de mi respuesta anterior), 
            # es aquí donde podrías pasar el path explícito a tu ChromeDriver si no está en PATH.
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            # Esto imprimirá el error completo si la SessionNotCreatedException persiste.
            print(f"❌ Error iniciando Chrome. VERIFICA LA COMPATIBILIDAD DE CHROME Y CHROMEDRIVER: {e}") 
            raise

        # En modo Headless, maximize_window no hace nada visible, pero se mantiene si se necesita para alguna lógica.
        driver.maximize_window() 
        driver.get(app_url)

        wait = WebDriverWait(driver, 15)
        time.sleep(5)
        print("✅ Navegador iniciado correctamente y listo para interactuar con el asistente.")
        return driver, wait


    @staticmethod
    def abrir_teclado(driver, wait):
        """Hace clic en el icono del teclado"""
        try:
            boton_teclado = wait.until(EC.element_to_be_clickable((By.ID, "keyboard-kairos")))
            boton_teclado.click()
            print("⌨️ Se hizo clic en el icono del teclado.")
        except Exception as e:
            print("⚠️ No se pudo hacer clic en el teclado:", e)