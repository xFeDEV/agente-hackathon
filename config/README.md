# Configuración de Google Cloud Service Account

## Ubicación de la Llave

Coloca tu archivo de llave de servicio de Google Cloud en este directorio:

```
config/primeval-falcon-474622-h1-d5121477addc.json
```

## Seguridad

⚠️ **IMPORTANTE**: 
- Este directorio está en `.gitignore` para evitar subir credenciales al repositorio
- Nunca compartas o subas archivos `.json` de credenciales
- El archivo se monta en el contenedor Docker en modo solo lectura (`:ro`)

## Verificación

Para verificar que la llave está correctamente ubicada, ejecuta:

```bash
ls -la config/primeval-falcon-474622-h1-d5121477addc.json
```

El archivo debe existir y tener permisos de lectura.

## Uso en la Aplicación

El contenedor Docker automáticamente configurará las siguientes variables de entorno:

- `GOOGLE_APPLICATION_CREDENTIALS=/app/config/gcloud-key.json`
- `GOOGLE_GENAI_USE_VERTEXAI=True`
- `GOOGLE_CLOUD_PROJECT=primeval-falcon-474622-h1`
- `GOOGLE_CLOUD_LOCATION=us-central1`

No es necesario modificar el código de la aplicación para la autenticación.
