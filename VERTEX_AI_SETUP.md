# 🔐 Configuración de Vertex AI con ADC (Application Default Credentials)

Esta guía explica cómo configurar tu proyecto para usar Google Vertex AI con autenticación mediante credenciales de cuenta de servicio.

## 📋 Resumen de Cambios

### 1. Estructura de Directorios

Se ha creado el directorio `config/` para almacenar las credenciales:

```
agente-hackathon/
├── config/
│   ├── .gitignore                                    # Protege las credenciales
│   ├── README.md                                     # Documentación del directorio
│   └── primeval-falcon-474622-h1-d5121477addc.json  # ⬅️ TU ARCHIVO DE CREDENCIALES (colócalo aquí)
├── backend/
├── docker-compose.yml                                # ✅ Actualizado con configuración ADC
├── .env                                             # ✅ Actualizado con variables de GCloud
└── setup-credentials.sh                             # Script de ayuda para mover el archivo
```

### 2. Archivos Modificados

#### ✅ `docker-compose.yml`

Se agregaron las siguientes configuraciones al servicio `backend`:

- **Volume mount**: Monta el archivo de credenciales dentro del contenedor
  ```yaml
  - ./config/primeval-falcon-474622-h1-d5121477addc.json:/app/config/gcloud-key.json:ro
  ```

- **Variables de entorno** para Vertex AI:
  ```yaml
  - GOOGLE_GENAI_USE_VERTEXAI=True
  - GOOGLE_APPLICATION_CREDENTIALS=/app/config/gcloud-key.json
  - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
  - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
  ```

#### ✅ `.env`

Se agregaron las variables de configuración de Google Cloud:

```properties
GOOGLE_CLOUD_PROJECT=primeval-falcon-474622-h1
GOOGLE_CLOUD_LOCATION=us-central1
```

#### ✅ `backend/app/llm_service.py`

Se actualizó la función `get_gemini_model()` para soportar ambos métodos de autenticación:
- **Vertex AI con ADC** (recomendado para producción)
- **API Key** (fallback o desarrollo)

El código automáticamente detecta qué método usar basándose en `GOOGLE_GENAI_USE_VERTEXAI`.

#### ✅ `.gitignore`

Se agregaron reglas para proteger las credenciales:

```gitignore
# Google Cloud Service Account Keys
config/*.json
!config/example.json
```

## 🚀 Pasos para Configurar

### Paso 1: Ubicar tu Archivo de Credenciales

Encuentra el archivo descargado de Google Cloud:
```
primeval-falcon-474622-h1-d5121477addc.json
```

Probablemente está en `~/Downloads/` o `~/Descargas/`.

### Paso 2: Mover el Archivo (Opción A - Script Automático)

Ejecuta el script de configuración:

```bash
./setup-credentials.sh
```

Este script:
- Busca el archivo en ubicaciones comunes
- Lo copia a `config/`
- Configura los permisos correctos
- Valida que sea un JSON válido

### Paso 2: Mover el Archivo (Opción B - Manual)

```bash
# Copiar el archivo
cp ~/Downloads/primeval-falcon-474622-h1-d5121477addc.json config/

# Establecer permisos restrictivos (solo lectura para el propietario)
chmod 600 config/primeval-falcon-474622-h1-d5121477addc.json

# Verificar
ls -lh config/primeval-falcon-474622-h1-d5121477addc.json
```

### Paso 3: Verificar Variables de Entorno

Asegúrate de que tu archivo `.env` contiene:

```properties
# Google Cloud - Vertex AI Configuration
GOOGLE_CLOUD_PROJECT=primeval-falcon-474622-h1
GOOGLE_CLOUD_LOCATION=us-central1

# Google Gemini API Key (fallback)
GOOGLE_API_KEY=tu_api_key_actual
```

### Paso 4: Reconstruir y Iniciar los Contenedores

```bash
# Detener contenedores actuales
docker-compose down

# Reconstruir con la nueva configuración
docker-compose up -d --build

# Ver los logs para verificar la autenticación
docker-compose logs -f backend
```

### Paso 5: Verificar la Configuración

Deberías ver en los logs del backend:

```
🔐 Usando Vertex AI con ADC - Proyecto: primeval-falcon-474622-h1, Ubicación: us-central1
```

Si ves esto, ¡la autenticación está funcionando correctamente! 🎉

## 🔍 Cómo Funciona

### En el Código Python

Gracias a las variables de entorno, **no necesitas modificar nada en tu código**:

```python
from google import genai
from google.genai.types import HttpOptions

# El cliente se autentica automáticamente usando las variables de entorno
client = genai.Client(http_options=HttpOptions(api_version="v1"))

# Ya está listo para hacer peticiones a Vertex AI
response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="¡Hola desde Docker con Vertex AI!",
)

print(response.text)
```

### Variables de Entorno Automáticas

El SDK de Google automáticamente lee:
- `GOOGLE_APPLICATION_CREDENTIALS` → Ruta al archivo JSON
- `GOOGLE_GENAI_USE_VERTEXAI` → Activa el modo Vertex AI
- `GOOGLE_CLOUD_PROJECT` → ID del proyecto
- `GOOGLE_CLOUD_LOCATION` → Región del servicio

## 🔄 Alternancia entre API Key y Vertex AI

Para cambiar entre métodos de autenticación, modifica en `docker-compose.yml`:

### Usar Vertex AI (ADC)
```yaml
environment:
  - GOOGLE_GENAI_USE_VERTEXAI=True  # ⬅️ True para Vertex AI
```

### Usar API Key
```yaml
environment:
  - GOOGLE_GENAI_USE_VERTEXAI=False  # ⬅️ False para API Key
```

## 🛡️ Seguridad

### ✅ Buenas Prácticas Implementadas

1. **`.gitignore`**: Las credenciales NO se suben al repositorio
2. **Permisos restrictivos**: `chmod 600` en el archivo JSON
3. **Montaje read-only**: El contenedor monta el archivo como `:ro` (solo lectura)
4. **Variables de entorno**: Configuración sensible en `.env` (también ignorado por Git)

### ⚠️ NUNCA Hagas Esto

- ❌ No subas el archivo JSON a Git/GitHub
- ❌ No compartas el archivo en chats o emails
- ❌ No incluyas las credenciales directamente en el código
- ❌ No des permisos 777 al archivo

## 🧪 Prueba de Funcionamiento

Ejecuta un test rápido:

```bash
docker-compose exec backend python -c "
from google import genai
from google.genai.types import HttpOptions
import os

print('Configuración:')
print(f'  Vertex AI: {os.getenv(\"GOOGLE_GENAI_USE_VERTEXAI\")}')
print(f'  Proyecto: {os.getenv(\"GOOGLE_CLOUD_PROJECT\")}')
print(f'  Credenciales: {os.getenv(\"GOOGLE_APPLICATION_CREDENTIALS\")}')

client = genai.Client(http_options=HttpOptions(api_version='v1'))
response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents='Di hola en una línea'
)
print(f'\\nRespuesta: {response.text}')
"
```

## 📚 Recursos Adicionales

- [Documentación de Vertex AI](https://cloud.google.com/vertex-ai/docs)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [Gemini API Reference](https://ai.google.dev/api)

## ❓ Troubleshooting

### Error: "Could not automatically determine credentials"

**Solución**: Verifica que:
1. El archivo JSON existe en `config/`
2. `GOOGLE_APPLICATION_CREDENTIALS` apunta a la ruta correcta dentro del contenedor
3. El volume está correctamente montado en `docker-compose.yml`

### Error: "Invalid credentials"

**Solución**: 
1. Verifica que el archivo JSON sea válido
2. Asegúrate de que la cuenta de servicio tenga los permisos necesarios
3. Verifica que el proyecto en `.env` coincida con el del archivo JSON

### El contenedor no encuentra el archivo

**Solución**:
```bash
# Verificar que el archivo existe
ls -la config/primeval-falcon-474622-h1-d5121477addc.json

# Reconstruir el contenedor
docker-compose up -d --build --force-recreate backend

# Ver los logs
docker-compose logs backend
```

## 📝 Checklist de Configuración

- [ ] Archivo `primeval-falcon-474622-h1-d5121477addc.json` en `config/`
- [ ] Permisos `600` en el archivo JSON
- [ ] Variables en `.env` configuradas correctamente
- [ ] `docker-compose.yml` tiene el volume mount
- [ ] Variables de entorno en `docker-compose.yml`
- [ ] `.gitignore` protege las credenciales
- [ ] Contenedores reconstruidos (`docker-compose up -d --build`)
- [ ] Logs muestran "Usando Vertex AI con ADC"
- [ ] Prueba de conexión exitosa

---

**¡Listo!** Tu aplicación ahora está configurada para usar Vertex AI con autenticación segura mediante ADC. 🎊
