#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Vertex AI con ADC.
Este script se ejecuta dentro del contenedor Docker.
"""

import os
import sys

def print_section(title):
    """Imprime un título de sección formateado."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def check_environment():
    """Verifica las variables de entorno necesarias."""
    print_section("1. Variables de Entorno")
    
    env_vars = {
        "GOOGLE_GENAI_USE_VERTEXAI": os.getenv("GOOGLE_GENAI_USE_VERTEXAI"),
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "GOOGLE_CLOUD_LOCATION": os.getenv("GOOGLE_CLOUD_LOCATION"),
        "GOOGLE_API_KEY": "***" if os.getenv("GOOGLE_API_KEY") else None,
    }
    
    all_good = True
    for var, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"{status} {var:35s} = {value or '(no configurada)'}")
        if var != "GOOGLE_API_KEY" and not value:
            all_good = False
    
    return all_good

def check_credentials_file():
    """Verifica que el archivo de credenciales exista y sea accesible."""
    print_section("2. Archivo de Credenciales")
    
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS no está configurada")
        return False
    
    print(f"📁 Ruta: {creds_path}")
    
    if not os.path.exists(creds_path):
        print(f"❌ El archivo no existe en la ruta especificada")
        return False
    
    print(f"✅ El archivo existe")
    
    if not os.access(creds_path, os.R_OK):
        print(f"❌ El archivo no es legible")
        return False
    
    print(f"✅ El archivo es legible")
    
    # Intentar leer y validar el JSON
    try:
        import json
        with open(creds_path, 'r') as f:
            data = json.load(f)
        
        if "type" in data and data["type"] == "service_account":
            print(f"✅ JSON válido (tipo: service_account)")
            print(f"   📧 Service Account: {data.get('client_email', 'N/A')}")
            print(f"   🆔 Project ID: {data.get('project_id', 'N/A')}")
            return True
        else:
            print(f"⚠️  JSON válido pero no parece ser una cuenta de servicio")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_vertex_ai_connection():
    """Intenta conectarse a Vertex AI y hacer una petición de prueba."""
    print_section("3. Conexión con Vertex AI")
    
    try:
        from google import genai
        from google.genai.types import HttpOptions
        
        print("📦 Importación de google.genai: ✅")
        
        # Crear el cliente (usa automáticamente las credenciales de ADC)
        client = genai.Client(http_options=HttpOptions(api_version="v1"))
        print("🔧 Cliente creado: ✅")
        
        # Intentar una petición simple
        print("\n🚀 Intentando generar contenido con Gemini...")
        print("   (esto puede tardar unos segundos)\n")
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Responde solo con: '¡Conexión exitosa!'",
        )
        
        print(f"📨 Respuesta recibida:")
        print(f"   {response.text.strip()}")
        print("\n✅ ¡Conexión con Vertex AI exitosa!")
        return True
        
    except ImportError as e:
        print(f"❌ Error al importar bibliotecas: {e}")
        print("   Asegúrate de que google-genai está instalado")
        return False
    except Exception as e:
        print(f"❌ Error al conectar con Vertex AI: {e}")
        print(f"   Tipo: {type(e).__name__}")
        return False

def main():
    """Función principal que ejecuta todas las verificaciones."""
    print("\n" + "🔐 VERIFICACIÓN DE CONFIGURACIÓN VERTEX AI + ADC ".center(60, "="))
    
    # 1. Verificar variables de entorno
    env_ok = check_environment()
    
    # 2. Verificar archivo de credenciales
    creds_ok = check_credentials_file()
    
    # 3. Si todo está bien, probar la conexión
    if env_ok and creds_ok:
        connection_ok = test_vertex_ai_connection()
    else:
        print_section("⚠️ Verificaciones Previas Fallidas")
        print("No se puede probar la conexión hasta que se corrijan los errores anteriores.")
        connection_ok = False
    
    # Resumen final
    print_section("📊 Resumen")
    
    print(f"Variables de Entorno:  {'✅' if env_ok else '❌'}")
    print(f"Archivo de Credenciales: {'✅' if creds_ok else '❌'}")
    print(f"Conexión Vertex AI:    {'✅' if connection_ok else '❌'}")
    
    if env_ok and creds_ok and connection_ok:
        print("\n" + "🎉 ¡TODO CONFIGURADO CORRECTAMENTE! ".center(60, "=") + "\n")
        print("Tu aplicación está lista para usar Vertex AI con ADC.")
        print("Puedes empezar a hacer peticiones a Gemini desde tu código.\n")
        return 0
    else:
        print("\n" + "⚠️  CONFIGURACIÓN INCOMPLETA ".center(60, "=") + "\n")
        print("Revisa los errores anteriores y consulta VERTEX_AI_SETUP.md")
        print("para instrucciones detalladas.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
