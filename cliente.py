"""
cliente.py - Cliente de Chat
Responsable: Integrante 1
- Interfaz gráfica con tkinter
- Conexión al servidor principal
- Envío y recepción de mensajes en tiempo real
"""

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import random

HOST   = '127.0.0.1'
PORT   = 5000
BUFFER = 2048


class ClienteChat:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chat Distribuido")
        self.root.resizable(False, False)
        self.conn: socket.socket | None = None
        self.nombre = ''

        self._construir_ui()
        self._conectar()

    # ── Interfaz ─────────────────────────────────────────────────────────────
    def _construir_ui(self):
        self.root.configure(bg='#1e1e2e')

        # Título
        tk.Label(
            self.root, text="💬 Chat Distribuido",
            font=('Helvetica', 14, 'bold'),
            bg='#1e1e2e', fg='#cdd6f4'
        ).pack(pady=(10, 0))

        # Área de mensajes
        self.area = scrolledtext.ScrolledText(
            self.root, state='disabled',
            width=55, height=20,
            bg='#181825', fg='#cdd6f4',
            font=('Courier', 10),
            insertbackground='white',
            relief='flat', bd=0
        )
        self.area.pack(padx=10, pady=8)

        # Frame inferior
        frame = tk.Frame(self.root, bg='#1e1e2e')
        frame.pack(fill='x', padx=10, pady=(0, 10))

        self.entrada = tk.Entry(
            frame,
            font=('Helvetica', 11),
            bg='#313244', fg='#cdd6f4',
            insertbackground='white',
            relief='flat', bd=4
        )
        self.entrada.pack(side='left', fill='x', expand=True, ipady=6)
        self.entrada.bind('<Return>', self._enviar_mensaje)

        tk.Button(
            frame, text='Enviar',
            command=self._enviar_mensaje,
            bg='#89b4fa', fg='#1e1e2e',
            font=('Helvetica', 10, 'bold'),
            relief='flat', padx=10
        ).pack(side='left', padx=(6, 0))

    def _log(self, texto: str):
        """Muestra un mensaje en el área de chat (hilo-seguro)."""
        def _insert():
            self.area.config(state='normal')
            self.area.insert('end', texto + '\n')
            self.area.see('end')
            self.area.config(state='disabled')
        self.root.after(0, _insert)

    # ── Conexión ─────────────────────────────────────────────────────────────
    def _conectar(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((HOST, PORT))
        except ConnectionRefusedError:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar al servidor {HOST}:{PORT}\n"
                "Asegúrate de que servidor.py esté corriendo."
            )
            self.root.destroy()
            return

        # El servidor pide el nombre
        prompt = self.conn.recv(BUFFER).decode('utf-8')
        self.nombre = simpledialog.askstring(
            "Nombre de usuario", prompt,
            initialvalue="", parent=self.root
        ) or "Anónimo"
        self.conn.sendall(self.nombre.encode('utf-8'))

        self.root.title(f"Chat — {self.nombre}")
        self._log(f"Conectado como {self.nombre}. ¡Escribe y presiona Enter!")

        # Hilo receptor
        hilo = threading.Thread(target=self._recibir, daemon=True)
        hilo.start()

    # ── Envío y recepción ─────────────────────────────────────────────────────
    def _enviar_mensaje(self, event=None):
        if not self.conn:
            return
        texto = self.entrada.get().strip()
        if not texto:
            return
        try:
            self.conn.sendall(texto.encode('utf-8'))
            self.entrada.delete(0, 'end')
        except Exception:
            self._log("[ERROR] No se pudo enviar el mensaje.")

    def _recibir(self):
        while True:
            try:
                datos = self.conn.recv(BUFFER)
                if not datos:
                    break
                self._log(datos.decode('utf-8').strip())
            except Exception:
                break
        self._log("[Sistema] Conexión cerrada con el servidor.")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    root = tk.Tk()

    x = random.randint(50,300)
    y = random.randint(50, 300)

    root.geometry(f"600x500+{x}+{y}")

    app = ClienteChat(root)
    root.mainloop()
