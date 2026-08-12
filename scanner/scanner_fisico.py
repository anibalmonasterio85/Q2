"""Legacy wrapper for the QR scanner entrypoint.

This file keeps compatibility with the historical command:
    python scanner\\scanner_fisico.py
"""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scanner.physical import main


def create_parser():
    parser = argparse.ArgumentParser(description='Ejecuta el scanner físico de QR.')
    parser.add_argument('camera_index', nargs='?', type=int, default=0,
                        help='Índice de la cámara (0 por defecto).')
    parser.add_argument('--cooldown', '-c', type=float, default=3,
                        help='Segundos mínimos entre lecturas del mismo QR.')
    parser.add_argument('--width', type=int, default=640, help='Ancho de la captura de la cámara.')
    parser.add_argument('--height', type=int, default=480, help='Alto de la captura de la cámara.')
    return parser


if __name__ == '__main__':
    args = create_parser().parse_args()
    main(camera_index=args.camera_index,
         cooldown=args.cooldown,
         width=args.width,
         height=args.height)
