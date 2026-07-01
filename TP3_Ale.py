from tkinter import *
from tkinter import ttk
from FuncionesTP3 import *
import pickle
from datetime import datetime
import qrcode
import os
from reportlab.pdfgen import canvas

nombreArchivo = "memoriaPrincipal"
listaEstacionamiento = lee(nombreArchivo)

#============Botones==============
def visualAmarilla(event=None):
    campo = tamaño.get().strip()
    electrico = electricos.get().strip()

    if campo == "": #Me daba error porque ya buscaba desde que el usuario no habia puesto nada
        visual.config(text="", fg="yellow")

    elif (not campo.isdigit() or int(campo) <= 0 or (electrico != "" and
           (not electrico.isdigit() or int(electrico) < 0 or int(electrico) > int(campo)-2))):
        visual.config(text="Formato de datos erróneo o datos sin lógica.\nPonga números enteros positivos.",fg="red")

    else:
        visual.config(text=previsualizar(campo, electrico), fg="yellow")

def confirmar():
    campo = tamaño.get().strip()
    electrico = electricos.get().strip()
    gracia = tiempoGracia.get().strip()
    monto = montoHora.get().strip()

    if campo == "" or not campo.isdigit() or int(campo) <= 0:
        visual.config(text="Debe ingresar un tamaño válido.", fg="red")

    elif electrico != "" and (not electrico.isdigit() or int(electrico) < 0 or int(electrico) > int(campo)-2):
        visual.config(text="Dato eléctrico inválido.", fg="red")

    elif gracia == "" or not gracia.isdigit() or int(gracia) <= 0:
        visual.config(text="Debe ingresar un tiempo de gracia válido.", fg="red")

    elif monto == "" or not monto.isdigit() or int(monto) <= 0:
        visual.config(text="Debe ingresar un monto por hora válido.", fg="red")

    else:
        cantidadElectricos =0
        if electrico != "":
            cantidadElectricos =int(electrico)
        configuracionInicial = ConfiguracionEstacionamiento(int(campo), cantidadElectricos, int(gracia), int(monto))
        listaEstacionamiento.append(configuracionInicial)
        graba(nombreArchivo, listaEstacionamiento)
        marco1.destroy()
        marco2.place(relx=0.5, rely=0.5, anchor="center")

#Fin Botones Inicio
#Botones Marco2

        
def obtenerVehiculos():
    marco2.place_forget()
    marco3 = Frame(interfaz, bg="gray", padx=30, pady=25, highlightcolor="white", highlightthickness=4)
    marco3.place(relx=0.5, rely=0.5, anchor="center")
    datosEspacios = calcularEspacios(listaEstacionamiento)

    def solicitarDatosApi():
        if len(listaEstacionamiento) > 1:
            textoEstado.config(text="El proceso ya se realizó anteriormente.", fg="red")
            return

        direccionApi = "https://my.api.mockaroo.com/vehiculos_ale.json?key=55f19e80&count="
        datosApi = obtenerVehiculosApi(listaEstacionamiento, direccionApi)
        print(datosApi)
        listaObjetos = convertirApiObjetos(datosApi)
        listaEstacionamiento.append(listaObjetos)
        graba(nombreArchivo, listaEstacionamiento)
        textoEstado.config(text="Objetos guardados desde la API: " + str(len(listaObjetos)), fg="yellow")

    def regresarMenu():
        marco3.destroy()
        marco2.place(relx=0.5, rely=0.5, anchor="center")

    tituloObtener = Label(marco3, text="Obtener vehículos", font=("Arial", 16, "bold"), bg="gray", fg="white")
    tituloObtener.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    textoEstado = Label(marco3, text="Presione el botón para solicitar datos a la API.", font=("Arial", 12, "bold"), bg="gray", fg="yellow")
    textoEstado.grid(row=1, column=0, columnspan=2, pady=(0, 15))

    textoTamaño = Label(marco3, text="Tamaño Estacionamiento: " + str(datosEspacios[0]), font=("Arial", 11), bg="gray", fg="white")
    textoTamaño.grid(row=2, column=0, columnspan=2, pady=3)

    textoEspeciales = Label(marco3, text="Especiales: " + str(datosEspacios[1]), font=("Arial", 11), bg="gray", fg="white")
    textoEspeciales.grid(row=3, column=0, columnspan=2, pady=3)

    textoElectricos = Label(marco3, text="Eléctrico: " + str(datosEspacios[2]), font=("Arial", 11), bg="gray", fg="white")
    textoElectricos.grid(row=4, column=0, columnspan=2, pady=3)

    textoPorAsignar = Label(marco3, text="Por asignar: " + str(datosEspacios[3]), font=("Arial", 11), bg="gray", fg="white")
    textoPorAsignar.grid(row=5, column=0, columnspan=2, pady=3)

    textoTope = Label(marco3, text="Tope máximo masivo: " + str(datosEspacios[4]), font=("Arial", 11), bg="gray", fg="white")
    textoTope.grid(row=6, column=0, columnspan=2, pady=3)

    botonSolicitarApi = Button(marco3, text="Solicitar datos a la API", width=25, bg="green", fg="white", command=solicitarDatosApi)
    botonSolicitarApi.grid(row=7, column=0, padx=8, pady=(20, 0))

    botonRegresar = Button(marco3, text="Regresar", width=25, bg="red", fg="white", command=regresarMenu)
    botonRegresar.grid(row=7, column=1, padx=8, pady=(20, 0))
#Fin botones marco3
#========================
#Botones marco4


def ventanaInfo(numeroCampo, colorCampo, actualizarPagina):
    ventanaDatos = Toplevel(interfaz)
    ventanaDatos.title("Información del campo")
    ventanaDatos.config(bg="gray")

    carroSeleccionado = None
    if len(listaEstacionamiento) > 1:
        for carro in listaEstacionamiento[1]:
            if str(carro.estadia[0]) == str(numeroCampo):
                if str(carro.estadia[2]) == "":
                    carroSeleccionado = carro
                elif str(carro.estadia[2]) == "None":
                    carroSeleccionado = carro

    def pagar():
        salida = datetime.now().strftime("%d/%m/%Y %H:%M")
        tipoPago = tipoPagoCaja.get()
        monto = listaEstacionamiento[0].montoHora
        carroSeleccionado.estadia[2] = salida
        carroSeleccionado.pago = (monto, tipoPago)
        placa = carroSeleccionado.info[0]
        nombreFecha = salida.replace("/", "_").replace(":", "_").replace(" ", "_")
        infoQr = "PLACA=" + placa + " | MARCA=" + carroSeleccionado.info[1] + " | COLOR=" + carroSeleccionado.info[2] + " | TIPO=" + carroSeleccionado.info[3] + " | ENTRADA=" + carroSeleccionado.estadia[1] + " | SALIDA=" + salida + " | PAGO=" + tipoPago + " | MONTO=" + str(monto)
        nombreQr = "qrFactura_" + placa + ".png"
        nombrePdf = "factura_" + placa + "_" + nombreFecha + ".pdf"
        qrcode.make(infoQr).save(nombreQr)
        pdf = canvas.Canvas(nombrePdf)
        pdf.drawString(80, 750, "Factura de estacionamiento")
        pdf.drawString(80, 720, "Campo: " + str(numeroCampo))
        pdf.drawString(80, 700, "Placa: " + placa)
        pdf.drawString(80, 680, "Marca: " + carroSeleccionado.info[1])
        pdf.drawString(80, 660, "Color: " + carroSeleccionado.info[2])
        pdf.drawString(80, 640, "Tipo: " + carroSeleccionado.info[3])
        pdf.drawString(80, 620, "Entrada: " + carroSeleccionado.estadia[1])
        pdf.drawString(80, 600, "Salida: " + salida)
        pdf.drawString(80, 580, "Pago: " + tipoPago)
        pdf.drawString(80, 560, "Monto: " + str(monto))
        pdf.drawImage(nombreQr, 80, 380, width=150, height=150)
        pdf.save()
        os.remove(nombreQr)
        graba(nombreArchivo, listaEstacionamiento)
        actualizarPagina()
        ventanaDatos.destroy()

    if colorCampo == "red" and carroSeleccionado != None:
        Label(ventanaDatos, text="#Campo:", bg="gray", fg="white").grid(row=0, column=0, padx=8, pady=6)
        campoCaja = Entry(ventanaDatos, width=28)
        campoCaja.grid(row=0, column=1, padx=8, pady=6)
        campoCaja.insert(0, numeroCampo)
        campoCaja.config(state="readonly")

        Label(ventanaDatos, text="Placa:", bg="gray", fg="white").grid(row=1, column=0, padx=8, pady=6)
        placaCaja = Entry(ventanaDatos, width=28)
        placaCaja.grid(row=1, column=1, padx=8, pady=6)
        placaCaja.insert(0, carroSeleccionado.info[0])
        placaCaja.config(state="readonly")

        Label(ventanaDatos, text="Marca:", bg="gray", fg="white").grid(row=2, column=0, padx=8, pady=6)
        marcaCaja = Entry(ventanaDatos, width=28)
        marcaCaja.grid(row=2, column=1, padx=8, pady=6)
        marcaCaja.insert(0, carroSeleccionado.info[1])
        marcaCaja.config(state="readonly")

        Label(ventanaDatos, text="Color:", bg="gray", fg="white").grid(row=3, column=0, padx=8, pady=6)
        colorCaja = Entry(ventanaDatos, width=28)
        colorCaja.grid(row=3, column=1, padx=8, pady=6)
        colorCaja.insert(0, carroSeleccionado.info[2])
        colorCaja.config(state="readonly")

        Label(ventanaDatos, text="Hora entrada:", bg="gray", fg="white").grid(row=4, column=0, padx=8, pady=6)
        entradaCaja = Entry(ventanaDatos, width=28)
        entradaCaja.grid(row=4, column=1, padx=8, pady=6)
        entradaCaja.insert(0, carroSeleccionado.estadia[1])
        entradaCaja.config(state="readonly")

        Label(ventanaDatos, text="Tipo pago:", bg="gray", fg="white").grid(row=5, column=0, padx=8, pady=6)
        tipoPagoCaja = ttk.Combobox(ventanaDatos, values=["Efectivo", "SINPE", "Tarjeta"], state="readonly", width=25)
        tipoPagoCaja.grid(row=5, column=1, padx=8, pady=6)
        tipoPagoCaja.set("Efectivo")

        textoEstado = Label(ventanaDatos, text="Monto a pagar: " + str(listaEstacionamiento[0].montoHora), bg="gray", fg="yellow")
        textoEstado.grid(row=6, column=0, columnspan=2, pady=6)

        Button(ventanaDatos, text="Pagar", width=15, bg="green", fg="white", command=pagar).grid(row=7, column=0, padx=8, pady=15)
        Button(ventanaDatos, text="Regresar", width=15, bg="red", fg="white", command=ventanaDatos.destroy).grid(row=7, column=1, padx=8, pady=15)

    else:
        Label(ventanaDatos, text="El campo " + str(numeroCampo) + " está libre.", bg="gray", fg="white").grid(row=0, column=0, padx=20, pady=20)
        Button(ventanaDatos, text="Regresar", width=15, bg="red", fg="white", command=ventanaDatos.destroy).grid(row=1, column=0, pady=10)
        
def verEstacionamiento():
    marco2.place_forget()
    marco4 = Frame(interfaz, bg="gray", padx=30, pady=25, highlightcolor="white", highlightthickness=4)
    marco4.place(relx=0.5, rely=0.5, anchor="center")
    paginaActual = [0]
    totalCampos = listaEstacionamiento[0].cantidadCampos
    posicionesCampos = [(0,0), (0,1), (0,2), (0,3), (0,4), (1,5), (2,5), (3,0), (3,1), (3,2), (3,3), (3,4)]

    def regresarMenu():
        marco4.destroy()
        marco2.place(relx=0.5, rely=0.5, anchor="center")

    def mostrarPagina():
        for widget in marcoCampos.winfo_children():#devuelve una lista con todos los Wdgts de la ventana/marco
            widget.destroy()
        inicio = paginaActual[0]*12+1
        for i in range(12):
            numeroCampo = inicio + i
            fila = posicionesCampos[i][0]
            columna = posicionesCampos[i][1]
            if numeroCampo <= totalCampos:
                colorCampo = "green"
                if len(listaEstacionamiento) > 1:
                    for carro in listaEstacionamiento[1]:
                        if str(carro.estadia[0]) == str(numeroCampo):
                            if str(carro.estadia[2]) == "":
                                colorCampo = "red"
                            elif str(carro.estadia[2]) == "None":
                                colorCampo = "red"

                botonCampo = Button(marcoCampos, text=str(numeroCampo), width=8, height=4, bg=colorCampo, fg="white", command=lambda numeroCampo=numeroCampo, colorCampo=colorCampo: ventanaInfo(numeroCampo, colorCampo, mostrarPagina))
                botonCampo.grid(row=fila, column=columna, padx=6, pady=6)

            else:
                botonCampo = Button(marcoCampos, text="", width=9, height=5, bg="light gray", state="disabled")
                botonCampo.grid(row=fila, column=columna, padx=6, pady=6)
        flechaIzquierda.config(state="normal" if paginaActual[0] > 0 else "disabled")
        flechaDerecha.config(state="normal" if inicio + 11 < totalCampos else "disabled")
        textoPagina.config(text="Campos " + str(inicio) + " - " + str(min(inicio + 11, totalCampos)) + " de " + str(totalCampos))

    def paginaAnterior():
        paginaActual[0] -= 1
        mostrarPagina()

    def paginaSiguiente():
        paginaActual[0] += 1
        mostrarPagina()

    tituloEstacionamiento = Label(marco4, text="Ver estacionamiento", font=("Arial", 16, "bold"), bg="gray", fg="white")
    tituloEstacionamiento.grid(row=0, column=0, columnspan=3, pady=(0, 15))

    textoPagina = Label(marco4, text="", font=("Arial", 11, "bold"), bg="gray", fg="yellow")
    textoPagina.grid(row=1, column=0, columnspan=3, pady=(0, 10))

    flechaIzquierda = Button(marco4, text="<", width=3, bg="white", fg="black", command=paginaAnterior)
    flechaIzquierda.grid(row=2, column=0, padx=5)

    marcoCampos = Frame(marco4, bg="gray")
    marcoCampos.grid(row=2, column=1, padx=5)

    flechaDerecha = Button(marco4, text=">", width=3, bg="white", fg="black", command=paginaSiguiente)
    flechaDerecha.grid(row=2, column=2, padx=5)

    botonRegresar = Button(marco4, text="Regresar", width=20, bg="red", fg="white", command=regresarMenu)
    botonRegresar.grid(row=3, column=0, columnspan=3, pady=(20, 0))

    mostrarPagina()

#==========================
#Paso inicial
def marcoInicial():
    if listaEstacionamiento == []:
        marco1.place(relx=0.5, rely=0.5, anchor="center")
    else:
        marco2.place(relx=0.5, rely=0.5, anchor="center")
#==============================================================================
#Creacion de la interfaz y Marco1
interfaz = Tk() #Ventana principal
interfaz.title("Sistema de administracion de estacionamientos")
interfaz.geometry("700x500")
interfaz.resizable(False, False)
interfaz.config(bg="dim gray")
marco1 = Frame(interfaz, bg="lime green", padx=30, pady=25,highlightcolor="white",highlightthickness=4)
#marco1.place(relx=0.5, rely=0.5, anchor="center")


titulo1 = Label(marco1, text="Ingrese la cantidad total de espacios del estacionamiento:",
                    font=("Arial", 14,"bold"),bg="lime green",fg="white")
titulo1.grid(row=0, pady=(0, 15))

tamaño = StringVar()
tamañoEntrada = ttk.Entry(marco1, width=10, textvariable=tamaño)
tamañoEntrada.grid(row=1, pady=(0, 15))
tamañoEntrada.focus()

titulo2 = Label(marco1, text="Ingrese la cantidad de espacios destinados a vehiculos electricos:",
                    font=("Arial", 14,"bold"),bg="lime green",fg="white")
titulo2.grid(row=2,pady=(0, 15))

electricos =StringVar()
electricosEntrada = ttk.Entry(marco1, width=10, textvariable=electricos)
electricosEntrada.grid(row=3, pady=(0, 15))

visual = Label(marco1,text="No se encontró una base de datos,\ningrese los datos iniciales.", font=("Arial", 12, "bold"),bg="lime green",fg="yellow",justify="left")
visual.grid(row=8, pady=(20, 0),)

tamañoEntrada.bind("<KeyRelease>", visualAmarilla)
electricosEntrada.bind("<KeyRelease>", visualAmarilla)

botonConfirmar = Button(marco1, text="Confirmar", font=("Arial", 11, "bold"), bg="green", fg="white", command=confirmar)
botonConfirmar.grid(row=9, pady=(10, 0))

titulo3 = Label(marco1, text="Ingrese el tiempo de gracia en minutos:", font=("Arial", 14,"bold"), bg="lime green", fg="white")
titulo3.grid(row=4, pady=(0, 15))

tiempoGracia = StringVar()
tiempoGraciaEntrada = ttk.Entry(marco1, width=10, textvariable=tiempoGracia)
tiempoGraciaEntrada.grid(row=5, pady=(0, 15))

titulo4 = Label(marco1, text="Ingrese el monto por hora en colones:", font=("Arial", 14,"bold"), bg="lime green", fg="white")
titulo4.grid(row=6, pady=(0, 15))

montoHora = StringVar()
montoHoraEntrada = ttk.Entry(marco1, width=10, textvariable=montoHora)
montoHoraEntrada.grid(row=7, pady=(0, 15))

#Fin del marco1 y configuracion de ventana



#=================================================
#Marco2
marco2 = Frame(interfaz, bg="gray", padx=30, pady=25, highlightcolor="white", highlightthickness=4)   

tituloMenu = Label(marco2, text="Menú principal", font=("Arial", 16, "bold"), bg="gray", fg="black")
tituloMenu.grid(row=0, column=0, columnspan=3, pady=(0, 20))

tituloVehiculos = Label(marco2, text="2) Ver estacionamiento", font=("Arial", 13, "bold"), bg="gray", fg="white")
tituloVehiculos.grid(row=2, column=0, padx=8, pady=(0, 8))

tituloReportes = Label(marco2, text="3) Reportes", font=("Arial", 13, "bold"), bg="gray", fg="white")
tituloReportes.grid(row=1, column=1, padx=8, pady=(0, 8))

tituloConfiguracion = Label(marco2, text="4) Configuración", font=("Arial", 13, "bold"), bg="gray", fg="white")
tituloConfiguracion.grid(row=1, column=2, padx=8, pady=(0, 8))

#========================================
#Botones
botonObtenerVehiculos = Button(marco2, text="1) Obtener vehículos", width=30, bg="green", fg="white", command=obtenerVehiculos)
botonObtenerVehiculos.grid(row=1, column=0, padx=8, pady=8)

botonObservarEspacio = Button(marco2, text="2.1) Observar espacio", width=30, bg="green", fg="white", command=verEstacionamiento)
botonObservarEspacio.grid(row=3, column=0, padx=8, pady=8)

botonEstacionarVehiculo = Button(marco2, text="2.2) Estacionar un vehículo", width=30, bg="green", fg="white", command=None)
botonEstacionarVehiculo.grid(row=4, column=0, padx=8, pady=8)

botonCierreDiario = Button(marco2, text="3.1) Cierre diario", width=30, bg="yellow", fg="black", command=None)
botonCierreDiario.grid(row=2, column=1, padx=8, pady=8)

botonCierreTipoPago = Button(marco2, text="3.2) Cierre por tipo de pago", width=30, bg="yellow", fg="black", command=None)
botonCierreTipoPago.grid(row=3, column=1, padx=8, pady=8)

botonExportarCsv = Button(marco2, text="3.3) Exportar cierre diario a CSV", width=30, bg="yellow", fg="black", command=None)
botonExportarCsv.grid(row=4, column=1, padx=8, pady=8)

botonTamañoEstacionamiento = Button(marco2, text="4.1) Tamaño del estacionamiento", width=30, bg="red", fg="white", command=None)
botonTamañoEstacionamiento.grid(row=2, column=2, padx=8, pady=8)

botonTiempoGracia = Button(marco2, text="4.2) Tiempo de gracia en minutos", width=30, bg="red", fg="white", command=None)
botonTiempoGracia.grid(row=3, column=2, padx=8, pady=8)

botonModificarMonto = Button(marco2, text="4.3) Modificar monto por hora", width=30, bg="red", fg="white", command=None)
botonModificarMonto.grid(row=4, column=2, padx=8, pady=8)

botonAcercaDe = Button(marco2, text="5) Acerca de", width=30, bg="sky blue", fg="black", command=None)
botonAcercaDe.grid(row=5, column=1, padx=8, pady=(20, 0))




marcoInicial()
interfaz.mainloop()
