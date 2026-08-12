# Scanner del Proyecto

Este paquete contiene el escáner físico del sistema, responsable de leer los
códigos QR desde una cámara, validar el usuario en la base de datos y registrar
el acceso.

## Archivos clave

- `scanner/physical.py`: Lógica principal del escáner con detección de QR y
  validación de usuarios.
- `scanner/scanner_fisico.py`: Wrapper histórico compatible para ejecutar el
  escáner desde la ruta heredada.

## Uso

1. Activa el entorno virtual:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. Ejecuta el escáner desde la raíz del proyecto:
   ```powershell
   python scanner\scanner_fisico.py
   ```
3. Si necesitas seleccionar otra cámara, pasa el índice como argumento:
   ```powershell
   python scanner\scanner_fisico.py 1
   ```

## Controles en pantalla

- `q`: salir del escáner.
- `s`: guardar captura de imagen.

## Detalle

El motor principal usa pyzbar cuando está disponible y OpenCV `QRCodeDetector`
como respaldo. El escáner está diseñado para leer múltiples códigos en el mismo
frame, aplicar un cooldown por QR y mantener la ventana clara y fácil de usar.
