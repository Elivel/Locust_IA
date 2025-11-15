# Locust IA - Pruebas de Carga y Desempeño para Asistente IA

Herramienta para medir tiempos y desempeño de flujos de voz (reconocimiento de voz) y texto contra un frontend de asistente IA usando **Locust** + **Selenium**.

## 📋 Requisitos

- **Python 3.11+** (recomendado; gevent es más estable con esta versión)
- **Chrome** instalado (compatible con ChromeDriver)
- **Virtualenv** (`python -m venv`)

## 🚀 Instalación Rápida

### 1. Clonar o descargar el repositorio
```bash
cd C:\Users\[tu_usuario]\Performance\Locust_IA
```

### 2. Crear e activar el entorno virtual
```powershell
# Crear venv
python -m venv .venv

# Activar (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activar (CMD)
.\.venv\Scripts\activate.bat
```

### 3. Instalar dependencias
```powershell
python -m pip install --upgrade pip
pip install -r .\requirements.txt
```

**Dependencias principales:**
- `locust` — herramienta de pruebas de carga
- `selenium` — automatización del navegador
- `gtts` — síntesis de voz (Google Text-To-Speech)
- `playsound` — reproducción de audio
- `flask` — stub local para métricas
- `requests` — cliente HTTP

## 📊 Arquitectura del Proyecto

```
performanceIA/
├── selenium_locust.py          # Usuario Locust para flujos de voz
├── flujo_selenium_locust.py    # Alternativa (flujos simplificados)
├── metrics_stub.py             # Servidor Flask para registrar métricas
├── services/
│   └── session_service.py      # Gestión de sesiones y Chrome
└── flows/
    └── voice_flow.py           # Lógica de flujos de voz
```

## 🎯 Flujos Disponibles

### Flujo de Voz (Reconocimiento por Voz)

Ejecuta transferencias bancarias usando comandos de voz:

1. **Paso 1:** "pasar plata al número 300 401 10 16 por valor de 1000 pesos"
2. **Paso 2:** "confirmar transferencia"
3. **Validación:** Espera respuesta "¡Listo! Pasaste" u otra confirmación

**Métricas registradas en Locust:**
- `flujo_voz:pasar_plata_numero_monto` — tiempo de reconocimiento e intención
- `flujo_voz:confirmar` — tiempo de confirmación
- `flujo_voz:flujo_completo` — tiempo total del flujo

## 🏃 Cómo Ejecutar

### Opción 1: Con Interfaz Web (UI)

**Terminal 1 — Stub de Métricas** (escucha peticiones de métricas):
```powershell
.\.venv\Scripts\Activate.ps1
python .\performanceIA\metrics_stub.py
```
Salida esperada:
```
 * Running on http://127.0.0.1:5005
```

**Terminal 2 — Locust** (abre UI en http://localhost:8089):
```powershell
.\.venv\Scripts\Activate.ps1
$env:LOCUST_HEADLESS = "false"
locust -f .\performanceIA\selenium_locust.py
```

Luego:
1. Abre navegador en **http://localhost:8089**
2. Configura:
   - **Number of users:** 1 (o el número deseado)
   - **Spawn rate:** 1 (usuarios por segundo)
3. Pulsa **Start** para iniciar
4. Observa la pestaña **Statistics** para ver tiempos

### Opción 2: Sin Interfaz (Headless)

```powershell
.\.venv\Scripts\Activate.ps1

# Terminal 1
python .\performanceIA\metrics_stub.py

# Terminal 2
$env:LOCUST_HEADLESS = "false"
locust -f .\performanceIA\selenium_locust.py --headless -u 1 -r 1 -t 5m
```

**Parámetros útiles:**
- `-u 1` — 1 usuario
- `-r 1` — spawn rate de 1 usuario/segundo
- `-t 5m` — duración de 5 minutos
- `--stop-timeout 30` — timeout al parar (segundos)

### Opción 3: Modo Visual (Chrome Abierto)

```powershell
$env:LOCUST_HEADLESS = "false"
locust -f .\performanceIA\selenium_locust.py
```

Chrome se abrirá en ventana visible para ver el flujo en tiempo real. Útil para debugging.

## 📈 Interpretar Resultados en la UI de Locust

### Pestaña "Statistics"

Muestra una tabla con:

| Columna | Significado |
|---------|------------|
| **Type** | Tipo de request (p. ej. `flujo_voz:pasar_plata_numero_monto`) |
| **Name** | Nombre del paso o endpoint |
| **Count** | Número de veces que se ejecutó |
| **Median** | Tiempo mediano (ms) |
| **95%** | Percentil 95 (tiempo bajo el cual está el 95% de los requests) |
| **99%** | Percentil 99 |
| **Min** | Tiempo mínimo (ms) |
| **Max** | Tiempo máximo (ms) |
| **Requests/s** | Throughput (requests por segundo) |
| **Failures** | Número de fallos |

### Ejemplo de Salida

```
Type           Name                          Count  Median  95%   99%   Min   Max   Requests/s  Failures
─────────────────────────────────────────────────────────────────────────────────────────────────────
flujo_voz      pasar_plata_numero_monto      10     28000   35000 40000 25000 42000 0.5         0
flujo_voz      confirmar                     10     15000   18000 20000 14000 21000 0.5         0
flujo_voz      flujo_completo                10     43000   50000 55000 40000 60000 0.5         0
```

**Interpretación:**
- El primer paso ("pasar plata...") toma ~28 segundos (mediana)
- El segundo paso ("confirmar") toma ~15 segundos
- El flujo completo toma ~43 segundos
- Ninguno falló (Failures = 0)

## 🎛️ Configuración Avanzada

### Desactivar Headless (Ver Navegador)

Por defecto, Chrome corre en headless. Para verlo:

```powershell
$env:LOCUST_HEADLESS = "false"
locust -f .\performanceIA\selenium_locust.py
```

El navegador se abrirá automáticamente al iniciar el primer usuario.

### Cambiar Tiempos de Espera

En `performanceIA/flows/voice_flow.py`, método `reproducir_voz`:

```python
def reproducir_voz(self, texto, espera_ia=12):  # 12 segundos de espera
```

Reduce este valor si la IA responde más rápido.

### Aumentar Timeout de Validación

En `voice_flow.py`, método `validar_respuesta`:

```python
def validar_respuesta(self, posibles_textos, timeout=35):  # 35 segundos máximo
```

Incrementa si la IA tarda más en responder.

## 📊 Exportar Resultados

### Desde la UI de Locust

1. Pulsa el botón **CSV** en la pestaña **Statistics**
2. Se descarga un archivo `results.csv`
3. Abre en Excel para análisis

### Script de Ejemplo

Para extraer métricas programáticamente tras una prueba:

```python
import requests
import json

# Locust expone métricas en http://localhost:8089/stats
response = requests.get("http://localhost:8089/stats/requests")
stats = response.json()

for stat in stats:
    print(f"{stat['name']}: median={stat['median']}ms, 95%={stat['95%']}ms")
```

## 🐛 Troubleshooting

### Chrome no se abre
- Verifica que `$env:LOCUST_HEADLESS = "false"` esté establecido
- Comprueba que Chrome esté instalado: `wmic logicaldisk get name` → verifica versión en `chrome://version`
- Asegúrate de que ChromeDriver sea compatible

### Gevent error "DLL load failed"
- Solución: Crear nuevo venv con Python 3.11
  ```powershell
  py -3.11 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r .\requirements.txt
  ```

### La IA no responde a los comandos de voz
- Verifica que el micrófono esté activado (click en el botón dentro de Chrome)
- Aumenta `espera_ia` en `voice_flow.py` si la IA es lenta
- Incrementa `timeout` en `validar_respuesta` para esperas más largas

### Stub local (metrics_stub.py) no responde
- Verifica que esté corriendo: `http://127.0.0.1:5005`
- Revisa logs: debe mostrar `Running on http://127.0.0.1:5005`
- Si falla, puede ser por puerto ocupado; cambia en `metrics_stub.py`: `app.run(host='127.0.0.1', port=5006)`

## 📝 Personalización para el Cliente

### 1. Cambiar Valores de Transferencia
En `performanceIA/flows/voice_flow.py`, línea ~70:
```python
self.reproducir_voz("pasar plata al numero 300 401 10 16 por valor de 1000 pesos")
```

Reemplaza `300 401 10 16` y `1000 pesos` con valores deseados.

### 2. Cambiar Respuestas Esperadas
En `voice_flow.py`, línea ~72:
```python
respuesta = self.validar_respuesta([
    "¿Deseas confirmar la transferencia?", "¿Confirmas el envío?", "¡Listo! Pasaste"
])
```

Añade/quita las respuestas que la IA pueda devolver.

### 3. Agregar Más Pasos
En `ejecutar_flujo()`, añade un nuevo bloque:
```python
# Paso 3 - Nuevo paso
inicio_paso = time.time()
try:
    self.reproducir_voz("nuevo comando")
    respuesta = self.validar_respuesta(["respuesta esperada"])
    duracion_paso = round((time.time() - inicio_paso) * 1000, 2)
    pasos.append({
        "name": "nuevo_paso",
        "success": bool(respuesta),
        "duration_ms": duracion_paso,
        "detail": respuesta or "No validada"
    })
except Exception as e:
    # Error handling...
```

## 📞 Soporte

Para preguntas o cambios:
1. Revisa los logs de Locust (consola)
2. Habilita modo debug en `session_service.py`
3. Abre una issue en el repositorio

---

**Versión:** 1.0  
**Última actualización:** Noviembre 2025  
**Mantenedor:** Equipo de QA
