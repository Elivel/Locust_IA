# performanceIA/services/session_service.py
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SessionService:

    @staticmethod
    def obtener_appurl():
        """Llama al backend y obtiene un appUrl con token nuevo"""
        print("📡 Solicitando appUrl al servicio...")
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
        data = {
    "data": "{\"client\":{\"firstName\":\"Armando\",\"secondName\":\"\",\"lastName\":\"Bronca\",\"secondLastName\":\"Segura\",\"balance\":9442350.99,\"documentClient\":{\"number\":\"1100114\",\"type\":\"01\"},\"phoneNumber\":{\"countryId\":\"+57\",\"number\":\"3004011014\"},\"email\":\"xxx@gmail.com\",\"userId\":\"763b9bf753fb9fa56a90a091baa4fcf03c21687bef637ccb4d2e333bc724e5b5\",\"authenticationType\":\"DAVIPLATA\"},\"module\":{\"id\":\"KRS\",\"country\":\"CO\"},\"consumer\":{\"appConsumer\":{\"id\":\"APP_DAVIPLATA\",\"platformType\":\"APP_DAVIPLATAMOVIL\",\"canalId\":\"83\",\"sessionId\":\"17280492576755584902345352747985\",\"transactionId\":\"006355\",\"consumerRequestId\":\"8500\",\"transactionDate\":\"2024-10-04T08:47:21-05:00\"},\"deviceConsumer\":{\"id\":\"199066910afd18aed979359520eb9e30e8e2a07673806bc0607cf1e99bfc1876\",\"userAgent\":\"okhttp/4.9.2\",\"soVersion\":\"Android6.3.0\",\"ipDevice\":\"181.54.52.102\",\"appVersion\":\"6.3.0\",\"originDevice\":\"\",\"idDevice\":\"3004011015\"},\"genericData\":{\"dataItem\":[{\"key\":\"tokenFrontend\",\"value\":\"2db9a44e-4589-49ba-96a5-b4a3737689e7\"}]}}}",
    "ttl": 300
}

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
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(app_url)
        wait = WebDriverWait(driver, 10)
        time.sleep(5)
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
