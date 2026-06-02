"""
replica.py - Servidor Réplica
Responsable: Integrante 3 y 4
- Recibe mensajes del servidor principal y los almacena
- Responde a señales heartbeat
"""

import socket
import threading
import time

HOST = '127.0.0.1'
PORT_REPLICA = 6001       # Puerto donde escucha la réplica (mensajes)
PORT_HEARTBEAT = 6002     # Puerto donde escucha señales heartbeat
HISTORIAL_REPLICA = 'historial_replica.txt'

historial_lock = threading.Lock()


def guardar_mensaje(mensaje: str):
    """Guarda un mensaje en el historial de la réplica."""
    with historial_lock:
        with open(HISTORIAL_REPLICA, 'a', encoding='utf-8') as f:
            f.write(mensaje + '\n')
    print(f"[RÉPLICA] Mensaje almacenado: {mensaje}")


def manejar_replicacion(conn, addr):
    """Recibe mensajes replicados desde el servidor principal."""
    print(f"[RÉPLICA] Conexión de replicación establecida con {addr}")
    with conn:
        while True:
            try:
                datos = conn.recv(1024)
                if not datos:
                    break
                mensaje = datos.decode('utf-8').strip()
                if mensaje:
                    guardar_mensaje(mensaje)
            except ConnectionResetError:
                break
    print(f"[RÉPLICA] Conexión de replicación cerrada con {addr}")


def servidor_replicacion():
    """Escucha mensajes del servidor principal para replicarlos."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT_REPLICA))
        s.listen()
        print(f"[RÉPLICA] Escuchando replicación en {HOST}:{PORT_REPLICA}")
        while True:
            conn, addr = s.accept()
            hilo = threading.Thread(target=manejar_replicacion, args=(conn, addr), daemon=True)
            hilo.start()


def servidor_heartbeat():
    """Responde a señales heartbeat del servidor principal."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT_HEARTBEAT))
        s.listen()
        print(f"[RÉPLICA] Escuchando heartbeat en {HOST}:{PORT_HEARTBEAT}")
        while True:
            conn, addr = s.accept()
            with conn:
                try:
                    datos = conn.recv(1024)
                    if datos.decode('utf-8').strip() == 'heartbeat':
                        conn.sendall(b'activo')
                        print(f"[RÉPLICA] Heartbeat recibido → respondiendo 'activo'")
                except Exception:
                    pass


if __name__ == '__main__':
    print("=" * 45)
    print("   SERVIDOR RÉPLICA - Sistema de Chat")
    print("=" * 45)

    # Limpiar historial anterior
    open(HISTORIAL_REPLICA, 'w').close()

    hilo_rep = threading.Thread(target=servidor_replicacion, daemon=True)
    hilo_hb  = threading.Thread(target=servidor_heartbeat,  daemon=True)

    hilo_rep.start()
    hilo_hb.start()

    print("[RÉPLICA] En ejecución. Presiona Ctrl+C para detener.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[RÉPLICA] Servidor réplica detenido.")
