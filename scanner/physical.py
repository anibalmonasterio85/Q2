"""QR Access Control PRO physical scanner.

Este módulo encapsula la lógica de detección de códigos QR y la validación de
usuarios en la base de datos.
"""

import argparse
import os
import sys
import time
from datetime import datetime

import cv2
import numpy as np

try:
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except Exception:
    HAS_PYZBAR = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.settings import config
from web_panel.models import user as user_model, access_log

DEFAULT_CAMERA_INDEX = 0
DEFAULT_SCAN_COOLDOWN = 3
WINDOW_NAME = 'QR Access Control PRO - Scanner'

COLOR_SUCCESS = (128, 222, 74)
COLOR_DENIED = (113, 113, 248)
COLOR_INFO = (250, 165, 96)
COLOR_WHITE = (255, 255, 255)
COLOR_BG = (26, 26, 42)


def draw_overlay(frame, text, color, user_name='', timestamp=''):
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 100), (w, h), COLOR_BG, -1)
    frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)

    cv2.putText(frame, text, (20, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

    if user_name:
        cv2.putText(frame, user_name, (20, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 1)

    if timestamp:
        cv2.putText(frame, timestamp, (w - 220, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_INFO, 1)

    cv2.rectangle(frame, (0, 0), (w, 45), COLOR_BG, -1)
    cv2.putText(frame, 'QR Access Control PRO', (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_INFO, 2)

    return frame


def draw_qr_boxes(frame, qr_records):
    for qr in qr_records:
        points = qr.get('points')
        if not points:
            continue

        pts = np.array(points, dtype=np.int32).reshape((-1, 2))
        if pts.size > 0:
            cv2.polylines(frame, [pts], True, COLOR_INFO, 2)
            text_position = (int(pts[0][0]), int(pts[0][1]) - 10)
            cv2.putText(frame, qr['data'], text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_WHITE, 1)


def decode_with_pyzbar(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    decoded = pyzbar.decode(gray)
    records = []

    for qr in decoded:
        data = qr.data.decode('utf-8', errors='ignore').strip()
        if not data:
            continue

        points = [(point.x, point.y) for point in qr.polygon] if qr.polygon else None
        records.append({'data': data, 'points': points, 'source': 'pyzbar'})

    return records


def decode_with_opencv(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.QRCodeDetector()
    records = []

    try:
        retval, decoded_info, points, _ = detector.detectAndDecodeMulti(gray)
    except Exception:
        retval, decoded_info, points = False, None, None

    if retval and decoded_info:
        for index, data in enumerate(decoded_info):
            if not data:
                continue

            pts = None
            if points is not None and len(points) > index:
                pts = [(int(x), int(y)) for x, y in points[index].reshape(-1, 2)]
            records.append({'data': data.strip(), 'points': pts, 'source': 'opencv'})

    if not records:
        data, pts, _ = detector.detectAndDecode(gray)
        if data:
            pts_list = None
            if pts is not None and pts.size:
                pts_list = [(int(x), int(y)) for x, y in pts.reshape(-1, 2)]
            records.append({'data': data.strip(), 'points': pts_list, 'source': 'opencv_single'})

    return records


def decode_qr_frame(frame):
    if HAS_PYZBAR:
        try:
            decoded = decode_with_pyzbar(frame)
            if decoded:
                return decoded
        except Exception:
            pass

    return decode_with_opencv(frame)


def validate_qr(qr_data):
    try:
        user = user_model.get_by_qr(qr_data)

        if user and user['activo']:
            if user.get('fecha_expiracion') and user['fecha_expiracion'] < datetime.now():
                access_log.create_log(qr_data, 'denegado', user['id'])
                return 'denegado', user['nombre'], 'QR expirado'

            access_log.create_log(qr_data, 'permitido', user['id'])
            return 'permitido', user['nombre'], ''

        if user and not user['activo']:
            access_log.create_log(qr_data, 'denegado', user['id'])
            return 'denegado', user['nombre'], 'Usuario desactivado'

        access_log.create_log(qr_data, 'denegado')
        return 'denegado', 'Desconocido', 'QR no registrado'

    except Exception as exc:
        print(f"[ERROR] Error validando QR: {exc}")
        return 'error', 'Error', str(exc)


def create_parser():
    parser = argparse.ArgumentParser(description='Ejecuta el scanner físico de QR.')
    parser.add_argument('camera_index', nargs='?', type=int, default=DEFAULT_CAMERA_INDEX,
                        help='Índice de la cámara (0 por defecto).')
    parser.add_argument('--cooldown', '-c', type=float, default=DEFAULT_SCAN_COOLDOWN,
                        help='Segundos mínimos entre lecturas del mismo QR.')
    parser.add_argument('--width', type=int, default=640, help='Ancho de la captura de la cámara.')
    parser.add_argument('--height', type=int, default=480, help='Alto de la captura de la cámara.')
    return parser


def main(camera_index=DEFAULT_CAMERA_INDEX, cooldown=DEFAULT_SCAN_COOLDOWN, width=640, height=480):
    print('\n' + '=' * 54)
    print('  🔐 QR ACCESS CONTROL PRO - SCANNER')
    print('=' * 54)
    print(f'  📷 Cámara: {camera_index}')
    print(f'  💾 BD: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}')
    print(f'  🔄 Cooldown: {cooldown}s')
    print('  ⌨️  Controles: q = Salir | s = Captura')
    print('=' * 54 + '\n')

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f'[ERROR] No se pudo abrir la cámara {camera_index}.')
        print('  Prueba con otro índice: python scanner\\scanner_fisico.py [0|1|2]')
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    print('[INFO] Cámara abierta. Esperando códigos QR...\n')

    last_scanned = {}
    last_result = ('Esperando QR...', COLOR_INFO, '', '')

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('[ERROR] No se pudo leer frame de la cámara.')
                break

            qr_records = decode_qr_frame(frame)
            if qr_records:
                draw_qr_boxes(frame, qr_records)

            for qr in qr_records:
                qr_data = qr['data']
                now = time.time()

                if qr_data in last_scanned and (now - last_scanned[qr_data]) < cooldown:
                    continue

                last_scanned[qr_data] = now
                timestamp = datetime.now().strftime('%H:%M:%S')
                resultado, nombre, detalle = validate_qr(qr_data)

                if resultado == 'permitido':
                    color = COLOR_SUCCESS
                    status = 'ACCESO PERMITIDO'
                    print(f'  ✅ [{timestamp}] PERMITIDO - {nombre}')
                else:
                    color = COLOR_DENIED
                    status = 'ACCESO DENEGADO'
                    print(f'  ❌ [{timestamp}] DENEGADO - {nombre} ({detalle})')

                last_result = (status, color, nombre, timestamp)

            display_frame = draw_overlay(frame, last_result[0], last_result[1], last_result[2], last_result[3])
            cv2.imshow(WINDOW_NAME, display_frame)

            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                print('\n[INFO] Scanner detenido por el usuario.')
                break
            elif key == ord('s'):
                filename = f'captura_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                cv2.imwrite(filename, frame)
                print(f'  📸 Captura guardada: {filename}')

    except KeyboardInterrupt:
        print('\n[INFO] Scanner detenido (Ctrl+C).')
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print('[INFO] Recursos liberados. Hasta luego!')


if __name__ == '__main__':
    args = create_parser().parse_args()
    main(camera_index=args.camera_index, cooldown=args.cooldown, width=args.width, height=args.height)
