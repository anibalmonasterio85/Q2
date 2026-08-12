# 📖 MANUAL DEL USUARIO - QR ACCESS PRO

Bienvenido a **QR Access Control PRO**, el sistema profesional de control de acceso mediante códigos QR y panel web administrativo. Este manual está diseñado para explicarte paso a paso cómo iniciar y detener el sistema en tu entorno de desarrollo en Windows 11 usando PowerShell.

---

## 1. ¿Qué es QR Access Pro?
Es una plataforma completa que permite gestionar permisos de entrada a instalaciones o eventos. Consiste en varios componentes, destacando su **Panel Web** (donde administras los usuarios, ves los logs y el empleado visualiza su QR) y el sistema de **Escáner** (la cámara que lee los códigos físicamente).

---

## 2. Encendido y Apagado del Panel Web

Para operar el sistema completo necesitas encender un entorno de terminal nativo de Windows (`PowerShell`).

### **Para Encender el Panel Web**
1. Abre una ventana de **PowerShell**.
2. Navega a la carpeta principal de tu sistema usando el comando `cd`:
   ```powershell
   cd C:\QR_Access_PRO
   ```
3. Antes de iniciar la aplicación, es OBLIGATORIO encender el entorno virtual de Python:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Ejecuta el script de arranque principal de la interfaz web:
   ```powershell
   python web_panel\app.py
   ```

*Tip: La consola te mostrará un mensaje verde o de información indicando que el servidor está corriendo en la red local (`Running on http://0.0.0.0:5000/`). Deja esta pestaña abierta, es el motor web de la plataforma.*

### **Para Entrar al Panel de Administración**
1. Abre tu navegador web favorito (Chrome, Edge, Firefox).
2. Visita la dirección: `http://localhost:5000`
3. Ingresa con tus credenciales. Recuerda que la interfaz cambiará dependiendo si entras como **Admin**, **Guardia** o **Usuario** básico.

### **Para Apagar el Sistema**
En la misma consola negra (PowerShell) donde inició el servidor web, asegúrate de seleccionarla y presiona la combinación de teclas: **`Ctrl + C`**. Esto detendrá de forma limpia el servidor de Flask.

---

## 3. ¿Cómo funciona la Base de Datos?

QR Access Pro utiliza una base de datos **MySQL** robusta en segundo plano para persistir los usuarios y todos los historiales de acceso.

> **⚠️ Importante:** Como se especificó en el archivo `.env`, el sistema está configurado de forma nativa para conectarse al puerto `3307`. Antes de iniciar tu Panel Web (Paso 2), tu servidor MySQL local debe estar encendido en dicho puerto. Si la base de datos no está corriendo, el sistema arrojará un error de conexión al abrirse o al logearte.

---

## 4. Uso del Escáner Físico

El escáner funciona de forma independiente al panel web. Es el componente que está junto a la puerta y valida los códigos QR con MySQL.

1. Abre **una NUEVA** ventana de PowerShell (sin cerrar la del panel web).
2. Navega a la carpeta raíz del proyecto, activa el entorno virtual e inicia el escáner:
   ```powershell
   cd C:\QR_Access_PRO
   .\venv\Scripts\Activate.ps1
   python scanner\scanner_fisico.py
   ```
3. Si necesitas cambiar de cámara, añade el índice:
   ```powershell
   python scanner\scanner_fisico.py 1
   ```
4. El escáner mostrará una ventana con el feed de la cámara. Señala un código QR desde el celular y el sistema lo validará automáticamente.

### Controles del escáner
- `q`: salir del escáner.
- `s`: guardar una captura de pantalla en el directorio actual.

### Comportamiento de lectura
- Se pueden detectar múltiples códigos en el mismo frame.
- El mismo QR no se procesa más de una vez mientras dure el cooldown.
- Si el QR no existe, el sistema mostrará `ACCESO DENEGADO` y lo registrará en los accesos.
