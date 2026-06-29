# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 22/06/2026
# Ultima modificacion: 29/06/2026
# Version de Python: 3.11

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from logica import (
    existeBaseDeDatos, obtenerVehiculosDesdeApi, listaEstacionamiento,
    guardarConfiguracion, cargarConfiguracionDisco, configuracionParqueo,
    espaciosParqueo, obtenerEspaciosLibres, estacionarVehiculo,
    marcasDisponibles, coloresDisponibles, tiposVehiculo, pagarEspacio,
    reservarMasivamente, calcularTopeMasivoGeneral, ejecutarCierreDiario,
    generarCierrePorTipoPagoXml, exportarCierreDiarioCsv
)

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
        command=lambda: abrirVentanaObtenerVehiculos(ventana)
    ).pack(pady=6)

    tk.Button(
        marcoBotones,
        text="2. Ver estacionamiento",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: abrirVentanaVerEstacionamiento(ventana)
    ).pack(pady=6)

    tk.Button(
        marcoBotones,
        text="3. Reportes",
        width=28,
        height=2,
        font=("Arial", 10),
        bg="#2e75b6",
        fg="white",
        command=lambda: abrirVentanaReportes(ventana)
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

    def confirmarGuardado():
        """
        Funcionalidad: Valida los campos del formulario de configuracion y
                       llama a la logica para guardarlos y construir los espacios.
        Entradas: Ninguna. Lee los valores de los campos de la ventana.
        Salidas: Ninguna. Llama a guardarConfiguracion si los datos son validos.
        """
        tamanioTexto = campoTamanio.get().strip()
        tiempoGraciaTexto = campoTiempoGracia.get().strip()
        montoHoraTexto = campoMontoHora.get().strip()

        if not tamanioTexto.isdigit() or int(tamanioTexto) <= 0:
            messagebox.showerror("Error", "El tamano debe ser un numero entero mayor a 0.")
            return
        if not tiempoGraciaTexto.isdigit():
            messagebox.showerror("Error", "El tiempo de gracia debe ser un numero entero.")
            return
        if not montoHoraTexto.isdigit():
            messagebox.showerror("Error", "El monto por hora debe ser un numero entero.")
            return

        guardarConfiguracion(
            int(tamanioTexto),
            int(tiempoGraciaTexto),
            int(montoHoraTexto),
            tieneElectricoVar.get()
        )

        messagebox.showinfo("Exito", "Configuracion guardada correctamente.\nSe crearon " + tamanioTexto + " espacios.")
        ventana.destroy()

    tk.Button(
        marcoBotones,
        text="Guardar",
        width=14,
        bg="#2e8b57",
        fg="white",
        command=confirmarGuardado
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


def abrirVentanaObtenerVehiculos(ventanaPadre):
    """
    Funcionalidad: Abre la ventana que permite solicitar al API una cantidad
                   de vehiculos y muestra el resultado del proceso de carga.
    Entradas:
        - ventanaPadre(tk.Tk): La ventana principal del programa.
    Salidas: Ninguna. Abre la ventana de obtener vehiculos.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Obtener Vehiculos")
    ventana.geometry("460x420")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Obtener Vehiculos desde el API",
        font=("Arial", 14, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=20)

    tk.Label(
        ventana,
        text="Cantidad de vehiculos a solicitar:",
        font=("Arial", 11),
        bg="#eef4fb"
    ).pack(pady=5)

    campoCantidad = tk.Entry(ventana, width=15, font=("Arial", 11), justify="center")
    campoCantidad.pack(pady=5)

    tk.Label(
        ventana,
        text="Resultado:",
        font=("Arial", 11),
        bg="#eef4fb"
    ).pack(pady=(15, 5))

    areaResultado = tk.Text(ventana, height=10, width=48, font=("Courier New", 9))
    areaResultado.pack(pady=5)

    def ejecutarSolicitud():
        """
        Funcionalidad: Lee la cantidad ingresada y llama a la logica que
                       consulta el API, muestra el resultado en pantalla.
        Entradas: Ninguna. Lee el valor del campo campoCantidad.
        Salidas: Ninguna. Modifica el area de texto con el resultado.
        """
        cantidadTexto = campoCantidad.get().strip()
        if not cantidadTexto.isdigit() or int(cantidadTexto) <= 0:
            messagebox.showerror("Error", "Debe ingresar un numero entero mayor a 0.")
            return

        cantidadObtenida = obtenerVehiculosDesdeApi(int(cantidadTexto))

        areaResultado.delete("1.0", tk.END)
        if cantidadObtenida > 0:
            areaResultado.insert(tk.END, "Vehiculos obtenidos exitosamente: " + str(cantidadObtenida) + "\n\n")
            for objeto in listaEstacionamiento:
                placa, marca, color, tipo = objeto.info
                lineaTexto = "ID " + objeto.id + " | Placa: " + placa + " | Marca: " + marca + " | Tipo: " + tipo + "\n"
                areaResultado.insert(tk.END, lineaTexto)
        else:
            areaResultado.insert(tk.END, "No se pudo obtener informacion del API.\nVerifique su conexion e intente de nuevo.")

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=10)

    tk.Button(
        marcoBotones,
        text="Solicitar",
        width=14,
        bg="#2e8b57",
        fg="white",
        command=ejecutarSolicitud
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        marcoBotones,
        text="Regresar",
        width=14,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)


def abrirVentanaVerEstacionamiento(ventanaPadre):
    """
    Funcionalidad: Abre la ventana que muestra la cuadricula visual del
                   estacionamiento, con los espacios en verde (libre) o rojo
                   (ocupado). Al hacer clic en un espacio libre permite estacionar.
    Entradas:
        - ventanaPadre(tk.Tk): La ventana principal del programa.
    Salidas: Ninguna. Abre la ventana de ver estacionamiento.
    """
    cargarConfiguracionDisco()

    if len(espaciosParqueo) == 0:
        messagebox.showwarning("Aviso", "Primero debe configurar el tamano del estacionamiento.")
        return

    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Ver Estacionamiento")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Mapa del Estacionamiento",
        font=("Arial", 14, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).grid(row=0, column=0, columnspan=5, pady=15)

    columnas = 5
    fila = 1
    columna = 0

    for espacio in espaciosParqueo:
        if espacio["ocupado"]:
            colorFondo = "#e74c3c"
        else:
            colorFondo = "#2ecc71"

        etiquetaTipo = espacio["tipo"][0]

        botonEspacio = tk.Button(
            ventana,
            text="#" + str(espacio["numero"]) + "\n" + etiquetaTipo,
            width=8,
            height=4,
            bg=colorFondo,
            fg="white",
            font=("Arial", 9, "bold"),
            command=lambda n=espacio["numero"]: abrirVentanaObservarEspacio(ventana, n)
        )
        botonEspacio.grid(row=fila, column=columna, padx=5, pady=5)

        columna = columna + 1
        if columna == columnas:
            columna = 0
            fila = fila + 1

    tk.Label(
        ventana,
        text="Verde = Libre   |   Rojo = Ocupado   |   E = Especial   G = General   El = Electrico",
        font=("Arial", 9),
        bg="#eef4fb",
        fg="#555555"
    ).grid(row=fila + 1, column=0, columnspan=5, pady=15)

    tk.Button(
        ventana,
        text="Reserva masiva de vehiculos",
        width=30,
        bg="#8e44ad",
        fg="white",
        command=lambda: abrirVentanaReservaMasiva(ventana)
    ).grid(row=fila + 2, column=0, columnspan=5, pady=10)

    tk.Button(
        ventana,
        text="Regresar",
        width=20,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=fila + 3, column=0, columnspan=5, pady=10)


def abrirVentanaObservarEspacio(ventanaPadre, numeroEspacio):
    """
    Funcionalidad: Abre la ventana de un espacio especifico. Si esta ocupado
                   muestra la informacion del vehiculo en modo solo lectura.
                   Si esta libre, abre el formulario para estacionar un vehiculo.
    Entradas:
        - ventanaPadre(tk.Toplevel): La ventana de ver estacionamiento.
        - numeroEspacio(int): El numero del espacio seleccionado.
    Salidas: Ninguna. Abre la ventana correspondiente segun el estado del espacio.
    """
    indiceEspacio = -1
    for i in range(len(espaciosParqueo)):
        if espaciosParqueo[i]["numero"] == numeroEspacio:
            indiceEspacio = i

    if espaciosParqueo[indiceEspacio]["ocupado"]:
        abrirVentanaInformacionVehiculo(ventanaPadre, numeroEspacio)
    else:
        abrirVentanaEstacionarVehiculo(ventanaPadre, numeroEspacio)


def abrirVentanaInformacionVehiculo(ventanaPadre, numeroEspacio):
    """
    Funcionalidad: Muestra la informacion de solo lectura del vehiculo
                   estacionado en el espacio indicado.
    Entradas:
        - ventanaPadre(tk.Toplevel): La ventana de ver estacionamiento.
        - numeroEspacio(int): El numero del espacio ocupado a observar.
    Salidas: Ninguna. Abre la ventana con la informacion del vehiculo.
    """
    objetoEncontrado = None
    for objeto in listaEstacionamiento:
        if objeto.estadia[0] == numeroEspacio and objeto.estadia[2] is None:
            objetoEncontrado = objeto

    if objetoEncontrado is None:
        messagebox.showerror("Error", "No se encontro informacion para este espacio.")
        return

    placa, marca, color, tipo = objetoEncontrado.info
    fechaEntrada = objetoEncontrado.estadia[1]

    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Observar Espacio #" + str(numeroEspacio))
    ventana.geometry("400x400")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Espacio #" + str(numeroEspacio),
        font=("Arial", 14, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=15)

    marcoInfo = tk.Frame(ventana, bg="#eef4fb")
    marcoInfo.pack(pady=10)

    camposInfo = [
        ("Placa:", placa),
        ("Marca:", marca),
        ("Color:", color),
        ("Tipo:", tipo),
        ("Hora de entrada:", fechaEntrada.strftime("%d/%m/%Y %H:%M"))
    ]

    fila = 0
    for etiqueta, valor in camposInfo:
        tk.Label(marcoInfo, text=etiqueta, font=("Arial", 11, "bold"), bg="#eef4fb").grid(row=fila, column=0, sticky="w", pady=5, padx=5)
        campoSoloLectura = tk.Entry(marcoInfo, width=22, font=("Arial", 11))
        campoSoloLectura.insert(0, valor)
        campoSoloLectura.config(state="readonly")
        campoSoloLectura.grid(row=fila, column=1, pady=5, padx=5)
        fila = fila + 1

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=20)

    def abrirVentanaConfirmarPago():
        """
        Funcionalidad: Abre una pequena ventana para seleccionar el tipo de
                       pago y confirmar el cobro del espacio.
        Entradas: Ninguna.
        Salidas: Ninguna. Abre la ventana de seleccion de tipo de pago.
        """
        ventanaPago = tk.Toplevel(ventana)
        ventanaPago.title("Tipo de Pago")
        ventanaPago.geometry("320x220")
        ventanaPago.resizable(False, False)
        ventanaPago.config(bg="#eef4fb")

        tk.Label(
            ventanaPago,
            text="Seleccione el tipo de pago:",
            font=("Arial", 11, "bold"),
            bg="#eef4fb"
        ).pack(pady=15)

        tipoPagoVar = tk.StringVar()
        tipoPagoVar.set("Efectivo")
        opcionesPago = ["Efectivo", "SINPE", "Tarjeta"]
        tk.OptionMenu(ventanaPago, tipoPagoVar, *opcionesPago).pack(pady=5)

        def confirmarPago():
            """
            Funcionalidad: Llama a la logica para cobrar el espacio, muestra
                           el monto y el nombre de la factura generada.
            Entradas: Ninguna. Lee el tipo de pago seleccionado.
            Salidas: Ninguna. Cierra las ventanas relacionadas al pagar.
            """
            nombreFactura, montoAPagar = pagarEspacio(numeroEspacio, tipoPagoVar.get())
            if nombreFactura is None:
                messagebox.showerror("Error", "No se encontro informacion activa para este espacio.")
                return

            messagebox.showinfo(
                "Pago realizado",
                "Monto cobrado: ₡" + str(montoAPagar) + "\nFactura generada: " + nombreFactura
            )
            ventanaPago.destroy()
            ventana.destroy()
            ventanaPadre.destroy()

        tk.Button(
            ventanaPago,
            text="Confirmar Pago",
            width=18,
            bg="#2e8b57",
            fg="white",
            command=confirmarPago
        ).pack(pady=15)

        tk.Button(
            ventanaPago,
            text="Cancelar",
            width=18,
            bg="#c00000",
            fg="white",
            command=ventanaPago.destroy
        ).pack()

    tk.Button(
        marcoBotones,
        text="Pagar",
        width=14,
        bg="#2e8b57",
        fg="white",
        command=abrirVentanaConfirmarPago
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        marcoBotones,
        text="Regresar",
        width=14,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)


def abrirVentanaEstacionarVehiculo(ventanaPadre, numeroEspacio):
    """
    Funcionalidad: Abre el formulario para registrar un nuevo vehiculo en el
                   espacio indicado, con cajas de seleccion para marca, color
                   y tipo, y genera el voucher en PDF al confirmar.
    Entradas:
        - ventanaPadre(tk.Toplevel): La ventana de ver estacionamiento.
        - numeroEspacio(int): El numero del espacio libre seleccionado.
    Salidas: Ninguna. Abre el formulario para estacionar el vehiculo.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Estacionar Vehiculo - Espacio #" + str(numeroEspacio))
    ventana.geometry("420x440")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Estacionar en Espacio #" + str(numeroEspacio),
        font=("Arial", 13, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=15)

    marcoFormulario = tk.Frame(ventana, bg="#eef4fb")
    marcoFormulario.pack(pady=10)

    tk.Label(marcoFormulario, text="Placa:", bg="#eef4fb", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8, padx=5)
    campoPlaca = tk.Entry(marcoFormulario, width=20, font=("Arial", 11))
    campoPlaca.grid(row=0, column=1, pady=8, padx=5)

    listaMarcas = marcasDisponibles if len(marcasDisponibles) > 0 else ["Toyota", "Hyundai", "Kia", "Nissan"]
    tk.Label(marcoFormulario, text="Marca:", bg="#eef4fb", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8, padx=5)
    marcaVar = tk.StringVar()
    marcaVar.set(listaMarcas[0])
    tk.OptionMenu(marcoFormulario, marcaVar, *listaMarcas).grid(row=1, column=1, pady=8, padx=5, sticky="w")

    tk.Label(marcoFormulario, text="Color:", bg="#eef4fb", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=8, padx=5)
    colorVar = tk.StringVar()
    colorVar.set(coloresDisponibles[0])
    tk.OptionMenu(marcoFormulario, colorVar, *coloresDisponibles).grid(row=2, column=1, pady=8, padx=5, sticky="w")

    tk.Label(marcoFormulario, text="Tipo:", bg="#eef4fb", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=8, padx=5)
    tipoVar = tk.StringVar()
    tipoVar.set(tiposVehiculo[0])
    tk.OptionMenu(marcoFormulario, tipoVar, *tiposVehiculo).grid(row=3, column=1, pady=8, padx=5, sticky="w")

    tk.Label(marcoFormulario, text="Hora de entrada:", bg="#eef4fb", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=8, padx=5)
    horaActual = datetime.now().strftime("%d/%m/%Y %H:%M")
    campoHora = tk.Entry(marcoFormulario, width=20, font=("Arial", 11))
    campoHora.insert(0, horaActual)
    campoHora.config(state="readonly")
    campoHora.grid(row=4, column=1, pady=8, padx=5)

    tk.Label(
        ventana,
        text="Costo por hora: ₡" + str(configuracionParqueo.get("montoHora", 0)),
        font=("Arial", 10, "italic"),
        bg="#eef4fb",
        fg="#555555"
    ).pack(pady=5)

    def confirmarEstacionar():
        """
        Funcionalidad: Valida los datos del formulario, pide confirmacion al
                       usuario y llama a la logica para reservar el espacio y
                       generar el voucher correspondiente.
        Entradas: Ninguna. Lee los valores de los campos del formulario.
        Salidas: Ninguna. Llama a estacionarVehiculo si el usuario confirma.
        """
        placa = campoPlaca.get().strip().upper()
        if placa == "":
            messagebox.showerror("Error", "Debe ingresar la placa del vehiculo.")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar",
            "Se reservara el espacio #" + str(numeroEspacio) + " para la placa " + placa + ".\n¿Desea continuar?"
        )
        if not confirmacion:
            return

        nombreVoucher = estacionarVehiculo(placa, marcaVar.get(), colorVar.get(), tipoVar.get(), numeroEspacio)

        messagebox.showinfo("Exito", "Vehiculo estacionado correctamente.\nVoucher generado: " + nombreVoucher)
        ventana.destroy()
        ventanaPadre.destroy()

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=20)

    tk.Button(
        marcoBotones,
        text="Estacionar",
        width=14,
        bg="#2e8b57",
        fg="white",
        command=confirmarEstacionar
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        marcoBotones,
        text="Regresar",
        width=14,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)


def abrirVentanaReservaMasiva(ventanaPadre):
    """
    Funcionalidad: Abre la ventana de reserva masiva de vehiculos. Muestra
                   el tope maximo permitido segun la regla del 5% de reserva
                   y pide confirmacion antes de ejecutar el llenado dinamico.
    Entradas:
        - ventanaPadre(tk.Toplevel): La ventana de ver estacionamiento.
    Salidas: Ninguna. Abre la ventana de confirmacion de reserva masiva.
    """
    topeMasivo = calcularTopeMasivoGeneral()

    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Reserva Masiva de Vehiculos")
    ventana.geometry("440x320")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Reserva Masiva de Vehiculos",
        font=("Arial", 14, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=20)

    tk.Label(
        ventana,
        text="Este proceso llenara dinamicamente solo los\nespacios de tipo General, dejando un 5% libre\npara nuevos clientes.",
        font=("Arial", 10),
        bg="#eef4fb",
        fg="#555555",
        justify="center"
    ).pack(pady=10)

    tk.Label(
        ventana,
        text="Cantidad maxima permitida: " + str(topeMasivo) + " vehiculos",
        font=("Arial", 11, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=15)

    areaResultado = tk.Text(ventana, height=5, width=48, font=("Courier New", 9))
    areaResultado.pack(pady=5)

    def ejecutarReservaMasiva():
        """
        Funcionalidad: Pide confirmacion al usuario y ejecuta la reserva
                       masiva de vehiculos llamando a la logica correspondiente.
        Entradas: Ninguna.
        Salidas: Ninguna. Muestra el resultado de la reserva en el area de texto.
        """
        confirmacion = messagebox.askyesno(
            "Confirmar",
            "Se llenaran hasta " + str(topeMasivo) + " espacios generales con vehiculos del API.\n¿Desea continuar?"
        )
        if not confirmacion:
            return

        cantidadReservada = reservarMasivamente()

        areaResultado.delete("1.0", tk.END)
        if cantidadReservada > 0:
            areaResultado.insert(
                tk.END,
                "Reserva completada.\nVehiculos estacionados: " + str(cantidadReservada) +
                "\nSe generaron sus vouchers en PDF."
            )
        else:
            areaResultado.insert(tk.END, "No hay espacios generales disponibles\npara la reserva masiva.")

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=10)

    tk.Button(
        marcoBotones,
        text="Ejecutar Reserva",
        width=16,
        bg="#8e44ad",
        fg="white",
        command=ejecutarReservaMasiva
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        marcoBotones,
        text="Regresar",
        width=16,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)


def abrirVentanaReportes(ventanaPadre):
    """
    Funcionalidad: Abre el submenu de reportes con las opciones de cierre
                   diario, cierre por tipo de pago y exportar a CSV.
    Entradas:
        - ventanaPadre(tk.Tk): La ventana principal del programa.
    Salidas: Ninguna. Abre la ventana del submenu de reportes.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Reportes")
    ventana.geometry("380x320")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Reportes",
        font=("Arial", 14, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=20)

    def ejecutarCierrePorTipoPago():
        """
        Funcionalidad: Llama a la logica para generar el archivo XML del
                       cierre por tipo de pago y muestra el resultado al usuario.
        Entradas: Ninguna.
        Salidas: Ninguna. Muestra un mensaje con el nombre del archivo generado.
        """
        nombreArchivo = generarCierrePorTipoPagoXml()
        messagebox.showinfo("Exito", "Cierre por tipo de pago generado:\n" + nombreArchivo)

    def ejecutarExportarCsv():
        """
        Funcionalidad: Llama a la logica para exportar el cierre diario a un
                       archivo CSV y muestra el resultado al usuario.
        Entradas: Ninguna.
        Salidas: Ninguna. Muestra un mensaje con el nombre del archivo generado.
        """
        nombreArchivo = exportarCierreDiarioCsv()
        messagebox.showinfo("Exito", "Cierre diario exportado a CSV:\n" + nombreArchivo)

    tk.Button(
        ventana,
        text="a. Cierre diario",
        width=28,
        height=2,
        bg="#2e75b6",
        fg="white",
        command=lambda: abrirVentanaCierreDiario(ventana)
    ).pack(pady=6)

    tk.Button(
        ventana,
        text="b. Cierre por tipo de pago",
        width=28,
        height=2,
        bg="#2e75b6",
        fg="white",
        command=ejecutarCierrePorTipoPago
    ).pack(pady=6)

    tk.Button(
        ventana,
        text="c. Exportar cierre diario a CSV",
        width=28,
        height=2,
        bg="#2e75b6",
        fg="white",
        command=ejecutarExportarCsv
    ).pack(pady=6)

    tk.Button(
        ventana,
        text="Regresar",
        width=28,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).pack(pady=15)


def abrirVentanaCierreDiario(ventanaPadre):
    """
    Funcionalidad: Abre la ventana de cierre diario, que al confirmar factura
                   automaticamente todos los pendientes y muestra el resumen
                   del reporte generado.
    Entradas:
        - ventanaPadre(tk.Toplevel): La ventana del submenu de reportes.
    Salidas: Ninguna. Abre la ventana de cierre diario.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Cierre Diario")
    ventana.geometry("440x340")
    ventana.resizable(False, False)
    ventana.config(bg="#eef4fb")

    tk.Label(
        ventana,
        text="Cierre Diario del Estacionamiento",
        font=("Arial", 13, "bold"),
        bg="#eef4fb",
        fg="#1f4e79"
    ).pack(pady=15)

    tk.Label(
        ventana,
        text="Este proceso facturara automaticamente todos\nlos vehiculos pendientes con un tipo de pago\naleatorio y generara el reporte del dia.",
        font=("Arial", 10),
        bg="#eef4fb",
        fg="#555555",
        justify="center"
    ).pack(pady=10)

    areaResultado = tk.Text(ventana, height=6, width=48, font=("Courier New", 9))
    areaResultado.pack(pady=10)

    def ejecutarCierre():
        """
        Funcionalidad: Pide confirmacion al usuario y ejecuta el cierre diario
                       llamando a la logica correspondiente, muestra el resultado.
        Entradas: Ninguna.
        Salidas: Ninguna. Muestra el resultado del cierre en el area de texto.
        """
        confirmacion = messagebox.askyesno(
            "Confirmar",
            "Se facturaran todos los vehiculos pendientes y se cerrara el dia.\n¿Desea continuar?"
        )
        if not confirmacion:
            return

        nombreArchivo, cantidadFacturada, totalGeneral = ejecutarCierreDiario()

        areaResultado.delete("1.0", tk.END)
        areaResultado.insert(
            tk.END,
            "Cierre diario completado.\n\n"
            "Vehiculos facturados automaticamente: " + str(cantidadFacturada) + "\n"
            "Monto total acumulado del dia: " + str(totalGeneral) + " colones\n\n"
            "Reporte generado: " + nombreArchivo
        )

    marcoBotones = tk.Frame(ventana, bg="#eef4fb")
    marcoBotones.pack(pady=10)

    tk.Button(
        marcoBotones,
        text="Ejecutar Cierre",
        width=16,
        bg="#2e8b57",
        fg="white",
        command=ejecutarCierre
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        marcoBotones,
        text="Regresar",
        width=16,
        bg="#c00000",
        fg="white",
        command=ventana.destroy
    ).grid(row=0, column=1, padx=10)


# =========================================================
# Punto de entrada del programa
abrirVentanaPrincipal()
