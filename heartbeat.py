"""
heartbeat.py - Módulo de Detección de Fallos
Responsable: Integrante 4
- Envía señales heartbeat al servidor réplica cada 5 segundos
- Detecta cuando la réplica no responde y lanza alerta
"""

import socket
import time
import threading

HOST_REPLICA    = '127.0.0.1'
PORT_HEARTBEAT  = 6002
INTERVALO       = 5          # segundos entre cada heartbeat
TIMEOUT         = 3          # tiempo máximo de espera por respuesta

# Estado compartido (accesible desde servidor.py)
replica_activa = True
_lock = threading.Lock()


def get_replica_activa() -> bool:
    with _lock:
        return replica_activa


def _set_replica_activa(valor: bool):
    global replica_activa
    with _lock:
        replica_activa = valor


def _enviar_heartbeat() -> bool:
    """
    Envía un heartbeat a la réplica.
    Retorna True si responde 'activo', False en caso contrario.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            s.connect((HOST_REPLICA, PORT_HEARTBEAT))
            s.sendall(b'heartbeat')
            respuesta = s.recv(1024).decode('utf-8').strip()
            return respuesta == 'activo'
    except Exception:
        return False


def iniciar_heartbeat(callback_fallo=None, callback_recuperacion=None):
    """
    Lanza el loop de heartbeat en un hilo daemon.

    callback_fallo        : función() llamada cuando la réplica falla
    callback_recuperacion : función() llamada cuando la réplica vuelve
    """
    estaba_activa = True   # estado previo, para detectar cambios

    def loop():
        nonlocal estaba_activa
        print(f"[HEARTBEAT] Iniciado — verificando réplica cada {INTERVALO}s")
        while True:
            time.sleep(INTERVALO)
            responde = _enviar_heartbeat()

            if responde:
                _set_replica_activa(True)
                if not estaba_activa:
                    print("[HEARTBEAT] ✅  Servidor réplica reconectado.")
                    if callback_recuperacion:
                        callback_recuperacion()
                estaba_activa = True
            else:
                _set_replica_activa(False)
                if estaba_activa:
                    print("[HEARTBEAT] ❌  Servidor réplica desconectado.")
                    if callback_fallo:
                        callback_fallo()
                estaba_activa = False

    hilo = threading.Thread(target=loop, daemon=True)
    hilo.start()
    return hilo


# ── Uso independiente para pruebas ──────────────────────────────────────────
if __name__ == '__main__':
    def on_fallo():
        print("[ALERTA] ¡La réplica no responde!")

    def on_ok():
        print("[INFO] La réplica volvió a responder.")

    iniciar_heartbeat(callback_fallo=on_fallo, callback_recuperacion=on_ok)

    print("Monitoreando réplica. Presiona Ctrl+C para salir.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[HEARTBEAT] Monitor detenido.")
