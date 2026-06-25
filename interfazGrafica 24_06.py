# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 22/06/2026
# Ultima modificacion: 24/06/2026
# Version de Python: 3.11

import tkinter as tk
from tkinter import messagebox
from logica import existeBaseDeDatos

# =========================================================


def abrirVentanaPrincipal():
    """
    Funcionalidad: Crea y muestra la ventana principal del sistema de
                   estacionamiento con los 5 botones del menu. Si no existe
                   una base de datos previa, primero pide la configuracion
                   inicial al administrador.
    Entradas: Ninguna.
    Salidas: Ninguna. Abre la ventana principal del programa.
    """
    ventana = tk.Tk()
    ventana.title("Sistema de Estacionamiento")
    ventana.geometry("420x480")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Sistema de Estacionamiento",
        font=("Arial", 18, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=25)

    tk.Label(
        ventana,
        text="Seleccione una opcion del menu",
        font=("Arial", 11),
        bg="#eef4fb",
        fg="#555555"
    ).pack(pady=5)

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=20)

    tk.Button(
        marcoBotones,
        text="1. Obtener vehiculos",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: messagebox.showinfo("Aviso", "Funcionalidad en desarrollo.")
    ).pack(pady=6)

    tk.Button(
        marcoBotones,
        text="2. Ver estacionamiento",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: messagebox.showinfo("Aviso", "Funcionalidad en desarrollo.")
    ).pack(pady=6)

    tk.Button(
        marcoBotones,
        text="3. Reportes",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: messagebox.showinfo("Aviso", "Funcionalidad en desarrollo.")
    ).pack(pady=6)

    tk.Button(
        marcoBotones,
        text="4. Configuracion",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: abrirVentanaConfiguracion(ventana)
    ).pack(pady=6)

    tk.Button(
        marcoBotones,
        text="5. Acerca de",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: abrirVentanaAcercaDe(ventana)
    ).pack(pady=6)

    tk.Button(
        ventana,
        text="Salir",
        width=28,
        height=1,
        font=("Arial", 10),
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).pack(pady=15)

    if not existeBaseDeDatos():
        tk.Label(
            ventana,
            text="* No hay base de datos. Configure el parqueo primero.",
            font=("Arial", 8),
            bg="#eef4fb",
            fg="gray"
        ).pack()

    ventana.mainloop()


def abrirVentanaConfiguracion(ventanaPadre):
    """
    Funcionalidad: Abre la ventana de configuracion del estacionamiento.
                   Si no hay base de datos pide tamano, tiempo de gracia y
                   monto por hora. Si ya existe, permite actualizar esos datos.
    Entradas:
        - ventanaPadre(tk.Tk): La ventana principal del programa.
    Salidas: Ninguna. Abre la ventana de configuracion.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Configuracion")
    ventana.geometry("420x420")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Configuracion del Estacionamiento",
        font=("Arial", 14, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=20)

    marcoFormulario = tk.Frame(ventana, bg="#eef4fb")
    marcoFormulario.pack(pady=10)

    tk.Label(
        marcoFormulario,
        text="Tamano del estacionamiento:",
        font=("Arial", 11),
        bg="#eef4fb"
    ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    campoTamanio = tk.Entry(marcoFormulario, width=15, font=("Arial", 11))
    campoTamanio.grid(row=0, column=1, padx=10)

    tk.Label(
        marcoFormulario,
        text="Tiempo de gracia (minutos):",
        font=("Arial", 11),
        bg="#eef4fb"
    ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    campoTiempoGracia = tk.Entry(marcoFormulario, width=15, font=("Arial", 11))
    campoTiempoGracia.grid(row=1, column=1, padx=10)

    tk.Label(
        marcoFormulario,
        text="Monto por hora (colones):",
        font=("Arial", 11),
        bg="#eef4fb"
    ).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    campoMontoHora = tk.Entry(marcoFormulario, width=15, font=("Arial", 11))
    campoMontoHora.grid(row=2, column=1, padx=10)

    tk.Label(
        marcoFormulario,
        text="Estacionamiento electrico:",
        font=("Arial", 11),
        bg="#eef4fb"
    ).grid(row=3, column=0, padx=10, pady=10, sticky="w")
    tieneElectricoVar = tk.BooleanVar()
    tieneElectricoVar.set(False)
    tk.Radiobutton(marcoFormulario, text="Si", variable=tieneElectricoVar, value=True, bg="#eef4fb").grid(row=3, column=1, sticky="w")
    tk.Radiobutton(marcoFormulario, text="No", variable=tieneElectricoVar, value=False, bg="#eef4fb").grid(row=4, column=1, sticky="w")

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=25)

    tk.Button(
        marcoBotones,
        text="Guardar",
        width=14,
        bg="#2e8b57",
        fg="white",
        command=lambda: messagebox.showinfo("Aviso", "Funcionalidad en desarrollo.")
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        marcoBotones,
        text="Regresar",
        width=14,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)


def abrirVentanaAcercaDe(ventanaPadre):
    """
    Funcionalidad: Abre la ventana "Acerca de" con la informacion del equipo
                   de desarrollo del sistema de estacionamiento.
    Entradas:
        - ventanaPadre(tk.Tk): La ventana principal del programa.
    Salidas: Ninguna. Abre la ventana Acerca de.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Acerca de")
    ventana.geometry("420x420")
    ventana.resizable(False, False)
    ventana.config(bg="#1f4e79")

    tk.Label(
        ventana,
        text="🚗",
        font=("Arial", 40),
        bg="#1f4e79",
        fg="white"
    ).pack(pady=15)

    tk.Label(
        ventana,
        text="Sistema de Estacionamiento",
        font=("Arial", 16, "bold"),
        bg="#1f4e79",
        fg="white"
    ).pack(pady=5)

    tk.Label(
        ventana,
        text="Tarea Programada #3",
        font=("Arial", 11),
        bg="#1f4e79",
        fg="#cfe2f3"
    ).pack(pady=2)

    marcoInfo = tk.Frame(ventana, bg="white")
    marcoInfo.pack(pady=20, padx=30, fill="both", expand=True)

    tk.Label(
        marcoInfo,
        text="Desarrollado por:",
        font=("Arial", 11, "bold"),
        bg="white",
        fg="#1f4e79"
    ).pack(pady=(15, 5))

    tk.Label(
        marcoInfo,
        text="Alejandro Madrigal",
        font=("Arial", 11),
        bg="white"
    ).pack(pady=2)

    tk.Label(
        marcoInfo,
        text="Brandon Meza",
        font=("Arial", 11),
        bg="white"
    ).pack(pady=2)

    tk.Label(
        marcoInfo,
        text="Taller de Programacion - I Semestre 2026",
        font=("Arial", 9, "italic"),
        bg="white",
        fg="#777777"
    ).pack(pady=(15, 5))

    tk.Label(
        marcoInfo,
        text="Instituto Tecnologico de Costa Rica",
        font=("Arial", 9, "italic"),
        bg="white",
        fg="#777777"
    ).pack()

    tk.Button(
        ventana,
        text="Regresar",
        width=20,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).pack(pady=15)


# =========================================================
# Punto de entrada del programa
abrirVentanaPrincipal()
