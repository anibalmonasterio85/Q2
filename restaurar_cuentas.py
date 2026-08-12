import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import secrets

# Cargar las credenciales de tu archivo .env
load_dotenv()

def restaurar_usuarios():
    # Encriptación fuerte requerida por el sistema Flask
    password_encriptada = generate_password_hash("Admin123!")
    
    usuarios_semilla = [
        {
            "nombre": "Aníbal Admin",
            "correo": "anibalmonas124@gmail.com",
            "rol": "admin",
            "qr": secrets.token_urlsafe(16)
        },
        {
            "nombre": "Aníbal Guardia",
            "correo": "anibalmj090@gmail.com",
            "rol": "guardia",
            "qr": secrets.token_urlsafe(16)
        }
    ]

    query = """
    INSERT INTO usuarios (nombre, correo, password_hash, rol, activo, qr_code) 
    VALUES (%s, %s, %s, %s, 1, %s)
    """

    print("Iniciando inyección de cuentas maestras...")
    
    try:
        # Nos conectamos directamente para asegurar el COMMIT
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""), # Tomará la clave de tu .env
            database=os.getenv("DB_NAME", "qr_access_db"),
            port=int(os.getenv("DB_PORT", 3307))
        )
        cursor = conn.cursor()

        for u in usuarios_semilla:
            try:
                cursor.execute(query, (u["nombre"], u["correo"], password_encriptada, u["rol"], u["qr"]))
                print(f"✅ Cuenta insertada con éxito: {u['correo']} (Rol: {u['rol']})")
            except mysql.connector.Error as err:
                print(f"⚠️ Omitido {u['correo']} - Posiblemente ya existe.")

        # ESTO ES VITAL: Guarda los cambios permanentemente en el disco
        conn.commit()
        print("💾 ¡Cambios guardados permanentemente en la base de datos!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error conectando a la base de datos: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    restaurar_usuarios()