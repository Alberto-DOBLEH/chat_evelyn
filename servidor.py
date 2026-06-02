"""
servidor.py - Servidor Principal
Responsable: Integrante 2 y 3
- Acepta conexiones de clientes
- Recibe y distribuye mensajes a todos los clientes
- Replica mensajes al servidor réplica
- Guarda historial local
"""

import socket
import threading
import time
import heartbeat   # Módulo de detección de fallos

HOST            = '127.0.0.1'
PORT_CLIENTES   = 5000   # Puerto para clientes
HOST_REPLICA    = '127.0.0.1'
PORT_REPLICA    = 6001   # Puerto de replicación en la réplica
HISTORIAL       = 'historial.txt'

# ── Estado global ────────────────────────────────────────────────────────────
clientes: dict[socket.socket, str] = {}   # socket -> nombre de usuario
clientes_lock = threading.Lock()
historial_lock = threading.Lock()


# ── Utilidades ───────────────────────────────────────────────────────────────
def timestamp() -> str:
    return time.strftime('%H:%M:%S')


def guardar_historial(mensaje: str):
    with historial_lock:
        with open(HISTORIAL, 'a', encoding='utf-8') as f:
            f.write(mensaje + '\n')


def replicar_mensaje(mensaje: str):
    """Envía una copia del mensaje al servidor réplica."""
    if not heartbeat.get_replica_activa():
        return   # réplica caída, no intentar
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((HOST_REPLICA, PORT_REPLICA))
            s.sendall(mensaje.encode('utf-8'))
    except Exception:
        pass   # Si falla, el heartbeat lo detectará


def broadcast(mensaje: str, excluir: socket.socket | None = None):
    """Envía un mensaje a todos los clientes conectados."""
    with clientes_lock:
        destinatarios = list(clientes.keys())
    for cliente in destinatarios:
        if cliente is excluir:
            continue
        try:
            cliente.sendall(mensaje.encode('utf-8'))
        except Exception:
            pass


# ── Manejo de clientes ───────────────────────────────────────────────────────
def manejar_cliente(conn: socket.socket, addr):
    """Hilo dedicado a un cliente."""
    nombre = None
    try:
        # Paso 1: recibir nombre de usuario
        conn.sendall(b'Ingresa tu nombre de usuario: ')
        nombre = conn.recv(1024).decode('utf-8').strip()
        if not nombre:
            nombre = f"Usuario_{addr[1]}"

        with clientes_lock:
            clientes[conn] = nombre

        bienvenida = f"[{timestamp()}] *** {nombre} se unió al chat ***"
        print(bienvenida)
        guardar_historial(bienvenida)
        broadcast(bienvenida)
        replicar_mensaje(bienvenida)

        # Paso 2: loop de mensajes
        while True:
            datos = conn.recv(1024)
            if not datos:
                break
            texto = datos.decode('utf-8').strip()
            if not texto:
                continue

            mensaje = f"[{timestamp()}] {nombre}: {texto}"
            print(mensaje)
            guardar_historial(mensaje)
            broadcast(mensaje)       # a todos los clientes
            replicar_mensaje(mensaje)  # al servidor réplica

    except ConnectionResetError:
        pass
    finally:
        with clientes_lock:
            clientes.pop(conn, None)
        conn.close()
        if nombre:
            salida = f"[{timestamp()}] *** {nombre} salió del chat ***"
            print(salida)
            guardar_historial(salida)
            broadcast(salida)
            replicar_mensaje(salida)


# ── Callbacks heartbeat ───────────────────────────────────────────────────────
def on_replica_caida():
    aviso = f"[{timestamp()}] ⚠️  ALERTA: Servidor réplica desconectado."
    print(aviso)
    broadcast(aviso)

def on_replica_recuperada():
    aviso = f"[{timestamp()}] ✅  Servidor réplica reconectado."
    print(aviso)
    broadcast(aviso)


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 45)
    print("  SERVIDOR PRINCIPAL - Sistema de Chat")
    print("=" * 45)

    # Limpiar historial anterior
    open(HISTORIAL, 'w').close()

    # Iniciar monitoreo de réplica
    heartbeat.iniciar_heartbeat(
        callback_fallo=on_replica_caida,
        callback_recuperacion=on_replica_recuperada
    )

    # Arrancar servidor de clientes
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT_CLIENTES))
        servidor.listen()
        print(f"[SERVIDOR] Escuchando clientes en {HOST}:{PORT_CLIENTES}")
        print("[SERVIDOR] En ejecución. Presiona Ctrl+C para detener.\n")

        try:
            while True:
                conn, addr = servidor.accept()
                print(f"[SERVIDOR] Nueva conexión desde {addr}")
                hilo = threading.Thread(
                    target=manejar_cliente,
                    args=(conn, addr),
                    daemon=True
                )
                hilo.start()
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor principal detenido.")
