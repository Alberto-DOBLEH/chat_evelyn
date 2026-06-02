# Chat Distribuido — Proyecto Final Sistemas Distribuidos

Sistema de chat con replicación de mensajes y detección de fallos.

---

## Estructura de archivos

```
ProyectoFinal/
├── cliente.py        # Interfaz gráfica + conexión al servidor
├── servidor.py       # Servidor principal (distribuye mensajes)
├── replica.py        # Servidor réplica (almacena respaldo)
├── heartbeat.py      # Módulo de detección de fallos
├── historial.txt     # Historial del servidor principal (auto-generado)
├── historial_replica.txt  # Historial de la réplica (auto-generado)
└── README.md
```

---

## Requisitos

- Python 3.10 o superior (sin librerías externas)
- tkinter incluido con Python (si no: `sudo apt install python3-tk` en Linux)

---

## Cómo ejecutar (orden obligatorio)

Abre **3 terminales diferentes** en la carpeta del proyecto.

### Terminal 1 — Servidor Réplica
```bash
python replica.py
```

### Terminal 2 — Servidor Principal
```bash
python servidor.py
```

### Terminal 3 (y más) — Clientes
```bash
python cliente.py
```
Ejecuta este comando varias veces para abrir múltiples clientes.

---

## Casos de prueba

| Prueba | Pasos | Resultado esperado |
|--------|-------|--------------------|
| 1 | Conectar 3 clientes | Todos aparecen en el chat |
| 2 | Enviar mensajes | Todos los clientes reciben los mensajes |
| 3 | Revisar `historial.txt` y `historial_replica.txt` | Ambos tienen los mismos mensajes |
| 4 | Cerrar `replica.py` con Ctrl+C | Aparece alerta "Servidor réplica desconectado" en todos los clientes |

---

## División de trabajo

| Integrante | Archivo | Responsabilidad |
|------------|---------|-----------------|
| 1 | `cliente.py` | Interfaz, conexión, envío de mensajes |
| 2 | `servidor.py` | Aceptar conexiones, recibir y distribuir mensajes |
| 3 | `replica.py` + replicación en `servidor.py` | Enviar mensajes al servidor réplica, guardar historial |
| 4 | `heartbeat.py` | Heartbeat cada 5s, detección de fallos, alertas |

---

## Conceptos de Sistemas Distribuidos aplicados

| Función | Tema |
|---------|------|
| Chat multiusuario | Comunicación distribuida |
| Varios clientes simultáneos | Concurrencia (threading) |
| Servidor réplica | Replicación |
| Heartbeat cada 5s | Tolerancia a fallas |
| historial.txt | Consistencia |
| cliente ↔ servidor | Arquitectura cliente-servidor |
