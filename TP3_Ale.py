from tkinter import *
from tkinter import ttk
from FuncionesTP3 import *
import pickle
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

    if campo == "" or not campo.isdigit() or int(campo) <= 0:
        visual.config(text="Debe ingresar un tamaño válido.", fg="red")

    elif electrico != "" and (not electrico.isdigit() or int(electrico) < 0 or int(electrico) > int(campo)-2):
        visual.config(text="Dato eléctrico inválido.", fg="red")

    else:
        cantidadElectricos =0
        if electrico != "":
            cantidadElectricos =int(electrico)
        listaEstacionamiento.append([int(campo), cantidadElectricos])
        graba(nombreArchivo, listaEstacionamiento)
        marco1.destroy()
        marco2.place(relx=0.5, rely=0.5, anchor="center")

#Fin Botones Inicio
#Botones Marco1

def





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
tamañoEntrada.grid(row=1, pady=(0, 35))
tamañoEntrada.focus()

titulo2 = Label(marco1, text="Ingrese la cantidad de espacios destinados a vehiculos electricos:",
                    font=("Arial", 14,"bold"),bg="lime green",fg="white")
titulo2.grid(row=2,pady=(0, 15))

electricos =StringVar()
electricosEntrada = ttk.Entry(marco1, width=10, textvariable=electricos)
electricosEntrada.grid(row=3, pady=(0, 35))

visual = Label(marco1,text="No se encontró una base de datos,\ningrese los datos iniciales.", font=("Arial", 12, "bold"),bg="lime green",fg="yellow",justify="left")
visual.grid(row=4, pady=(20, 0),)

tamañoEntrada.bind("<KeyRelease>", visualAmarilla)
electricosEntrada.bind("<KeyRelease>", visualAmarilla)

botonConfirmar = Button(marco1, text="Confirmar", font=("Arial", 11, "bold"), bg="green", fg="white", command=confirmar)
botonConfirmar.grid(row=5, pady=(20, 0))
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

botonObtenerVehiculos = Button(marco2, text="1) Obtener vehículos", width=30, bg="green", fg="white", command=None)
botonObtenerVehiculos.grid(row=1, column=0, padx=8, pady=8)

botonObservarEspacio = Button(marco2, text="2.1) Observar espacio", width=30, bg="green", fg="white", command=None)
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
