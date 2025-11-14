# Instrucciones para agentes AI que colaboran en este repositorio

Estas instrucciones ayudan a un agente a ser productivo rápidamente en este proyecto de pruebas de carga con Locust y Selenium.

**Contexto general:**
- **Propósito:** scripts para medir flujos conversacionales (voz y texto) contra un frontend de asistente IA usando Locust + Selenium.
- **Estructura principal:** el código relevante está en `performanceIA/` y contiene:
  - `performanceIA/services/session_service.py` — centraliza la obtención de `appUrl` y la creación del `webdriver`.
  - `performanceIA/flows/voice_flow.py` — encapsula el flujo por voz (reproducción de audio y validación de respuestas).
  - `performanceIA/flujo_selenium_locust.py` y `performanceIA/flujo_locust_texto.py` — usuarios Locust para voz y texto.
  - `test_set.json` — pares entrada/resultado esperable para los flujos de prueba.

**Patrones y convenciones del proyecto:**
- Centralización de sesión: siempre usar `SessionService.obtener_appurl()` para obtener la URL y `SessionService.iniciar_navegador(...)` para abrir Chrome.
- Encapsulación de flujos: las interacciones (voz/texto) están en clases (`VoiceFlow`, `FlujoTexto`) y los `User` de Locust delegan en ellas.
- Métricas: reportar éxito/fallo usando `self.environment.events.request_success.fire(...)` y `request_failure.fire(...)` con `request_type` y `name` descriptivos (ver `flujo_selenium_locust.py`).
- Logs: el repo usa impresiones con emojis para depuración (ej. `print("🎙️ Enviando comando de voz: ...")`). Mantener ese estilo facilita lectura manual de logs.
- Imports inconsistentes: algunos módulos importan `services.session_service`, otros `performanceIA.services.session_service`. Tenlo en cuenta al editar/renombrar módulos.

**Dependencias detectadas (no todas están en `requirements.txt`):**
- `locust`, `selenium`, `gtts`, `requests`.
Instalación sugerida (PowerShell):
```
python -m pip install locust selenium gtts requests
```

**Comandos útiles para desarrollo / pruebas rápidas:**
- Ejecutar Locust (interfaz web):
```
locust -f performanceIA/flujo_selenium_locust.py
```
Luego abrir `http://localhost:8089` y arrancar usuarios.
- Ejecutar Locust en modo headless (1 usuario, spawn-rate 1):
```
locust -f performanceIA/flujo_selenium_locust.py --headless -u 1 -r 1
```
- Si trabajas con el flujo de texto:
```
locust -f performanceIA/flujo_locust_texto.py --headless -u 1 -r 1
```

**Consideraciones Selenium / entorno:**
- `SessionService.iniciar_navegador` configura `ChromeOptions` con `--headless=new`, `--use-fake-ui-for-media-stream` y varios flags de estabilidad; cualquier cambio en estas opciones puede afectar la detección del micrófono.
- Verifica que la versión de `chromedriver` sea compatible con Chrome instalado. Si falla la creación del driver, la excepción se imprime en `SessionService.iniciar_navegador`.
- Para debugging local visual, quita `--headless=new` o coméntalo temporalmente.

**Formas habituales de interacción con la app bajo prueba:**
- Voz: se genera un MP3 con `gTTS`, se reproduce con `start` (Windows) y se espera un tiempo configurable. La validación usa XPaths con `contains(text(), ...)` en `VoiceFlow.validar_respuesta`.
- Texto: se usa `textarea[data-testid='chat-input']` y `button[data-testid='btn-send']` en `flujo_locust_texto.py`.

**Ejemplos concretos a usar o modificar:**
- Registrar una métrica manualmente (ejemplo tomado del repo):
```py
self.environment.events.request_success.fire(
    request_type="flujo_voz",
    name="pasar_plata",
    response_time=duracion_paso,
    response_length=0
)
```
- Validación típica de respuesta (XPath parcial):
```py
elemento = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '¿A quién')]") ) )
```

**Qué revisar antes de editar:**
- Comprueba si el archivo que vas a cambiar importa `services.session_service` o `performanceIA.services.session_service` y actualiza las referencias de forma consistente.
- Si añades nuevas dependencias, sugiere o crea `requirements.txt` para que otros desarrolladores puedan reproducir el entorno.

**Limitaciones / no automáticas:**
- No hay `requirements.txt` ni CI detectado en el repositorio; no asumas entornos reproducibles.
- Los endpoints (p. ej. `http://localhost:8076/api/presentacion-cliente`) son locales; el agente no debe llamar a servicios remotos reales sin permiso. Para pruebas unitarias, maqueta `SessionService.obtener_appurl`.

Si algo de lo anterior no es claro o falta: indícame qué parte del flujo quieres que amplíe (por ejemplo: más ejemplos de import/exports, formas de mockear `appUrl`, o añadir `requirements.txt` y un README de ejecución). Gracias.
