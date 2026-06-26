# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 22/06/2026
# Ultima modificacion: 25/06/2026
# Version de Python: 3.11

import pickle
import requests
from datetime import datetime

# =========================================================
# Lista global que funciona como la base de datos del estacionamiento.
# Cada elemento es un objeto de la clase Estacionamiento.
listaEstacionamiento = []

# Lista global con los colores disponibles para los vehiculos.
# Se inicia con estos valores y se pueden agregar nuevos si el API trae otros.
coloresDisponibles = ["Rojo", "Azul", "Blanco", "Negro", "Gris", "Verde"]

# Lista global con las marcas disponibles para los vehiculos.
# Se llena dinamicamente al consultar el API.
marcasDisponibles = []

# Lista global con los tipos de vehiculo disponibles.
tiposVehiculo = ["Sedan", "SUV", "Pickup", "Hatchback", "Motocicleta"]
# =========================================================


class Estacionamiento:
    """
    Funcionalidad: Representa un registro de estacionamiento de un vehiculo,
                   con su informacion, estadia y datos de pago.
    Entradas:
        - id(str): Identificador unico del registro.
        - info(tuple): Tupla con (placa, marca, color, tipo).
        - estadia(list): Lista con [ubicacion, fechaHoraEntrada, fechaHoraSalida].
        - pago(tuple): Tupla con (monto, tipoPago).
    Salidas: Ninguna. Es una clase que almacena los atributos indicados.
    """

    def __init__(self, idRegistro, info, estadia, pago):
        """
        Funcionalidad: Inicializa un nuevo objeto Estacionamiento con sus
                       atributos de identificacion, informacion del vehiculo,
                       estadia y pago.
        Entradas:
            - idRegistro(str): Identificador unico del registro.
            - info(tuple): Tupla con (placa, marca, color, tipo).
            - estadia(list): Lista con [ubicacion, fechaHoraEntrada, fechaHoraSalida].
            - pago(tuple): Tupla con (monto, tipoPago).
        Salidas: Ninguna.
        """
        self.id = idRegistro
        self.info = info
        self.estadia = estadia
        self.pago = pago


def existeBaseDeDatos():
    """
    Funcionalidad: Verifica si ya existe un archivo de base de datos guardado
                   en memoria secundaria para el estacionamiento.
    Entradas: Ninguna.
    Salidas: Retorna True si el archivo existe y se pudo cargar, False si no.
    """
    try:
        archivo = open("estacionamiento.pkl", "rb")
        archivo.close()
        return True
    except:
        return False


def cargarBaseDeDatos():
    """
    Funcionalidad: Carga la lista de objetos del estacionamiento desde el
                   archivo binario estacionamiento.pkl en memoria.
    Entradas: Ninguna.
    Salidas: Retorna True si se cargo correctamente, False si no existia el archivo.
    """
    global listaEstacionamiento
    try:
        archivo = open("estacionamiento.pkl", "rb")
        listaEstacionamiento = pickle.load(archivo)
        archivo.close()
        return True
    except:
        listaEstacionamiento = []
        return False


def guardarBaseDeDatos():
    """
    Funcionalidad: Guarda la lista de objetos del estacionamiento en el
                   archivo binario estacionamiento.pkl.
    Entradas: Ninguna.
    Salidas: Ninguna. Escribe el archivo estacionamiento.pkl en la carpeta del programa.
    """
    archivo = open("estacionamiento.pkl", "wb")
    pickle.dump(listaEstacionamiento, archivo)
    archivo.close()


def consultarApiVehiculos(urlApi, cantidad):
    """
    Funcionalidad: Consulta la API de Mockaroo y obtiene una cantidad de
                   registros de vehiculos simulados en formato JSON.
    Entradas:
        - urlApi(str): La URL de la API de Mockaroo a consultar.
        - cantidad(int): La cantidad de registros que se desean obtener.
    Salidas:
        - resultado(list): Lista de diccionarios con los datos crudos del API,
                            o una lista vacia si la consulta falla.
    """
    try:
        respuesta = requests.get(urlApi, params={"count": cantidad})
        if respuesta.status_code == 200:
            return respuesta.json()
        return []
    except:
        return []


def construirDiccionarioVehiculos(datosApi):
    """
    Funcionalidad: Toma los datos crudos del API y construye el diccionario
                   solicitado por el proyecto, donde la llave es la placa y
                   el valor contiene marca, color, tipo, ubicacion y demas
                   datos de la estadia con valores iniciales vacios.
    Entradas:
        - datosApi(list): Lista de diccionarios con la informacion cruda del API.
    Salidas:
        - diccionarioVehiculos(dict): Diccionario con llave = placa, valor = datos del vehiculo.
    """
    diccionarioVehiculos = {}
    for registro in datosApi:
        placa = registro.get("vehicle_id", "SIN-PLACA")
        marca = registro.get("vehicle_make", "Desconocida")
        tipo = registro.get("vehicle_model", "Desconocido")

        if marca not in marcasDisponibles:
            marcasDisponibles.append(marca)

        diccionarioVehiculos[str(placa)] = {
            "marca": marca,
            "color": "",
            "tipo": tipo,
            "ubicacion": "",
            "fechaHoraEntrada": "",
            "fechaHoraSalida": "",
            "monto": 0,
            "tipoPago": 0
        }
    return diccionarioVehiculos


def crearListaDeObjetos(diccionarioVehiculos):
    """
    Funcionalidad: Convierte el diccionario de vehiculos en una lista de
                   objetos Estacionamiento, que es la estructura oficial
                   de la base de datos del proyecto.
    Entradas:
        - diccionarioVehiculos(dict): Diccionario con llave = placa, valor = datos del vehiculo.
    Salidas:
        - listaObjetos(list): Lista de objetos Estacionamiento.
    """
    listaObjetos = []
    contador = 1
    for placa, datos in diccionarioVehiculos.items():
        info = (placa, datos["marca"], datos["color"], datos["tipo"])
        estadia = [datos["ubicacion"], datos["fechaHoraEntrada"], datos["fechaHoraSalida"]]
        pago = (datos["monto"], datos["tipoPago"])
        nuevoObjeto = Estacionamiento(str(contador), info, estadia, pago)
        listaObjetos.append(nuevoObjeto)
        contador = contador + 1
    return listaObjetos


def obtenerVehiculosDesdeApi(cantidad):
    """
    Funcionalidad: Funcion principal que consulta el API, construye el
                   diccionario de vehiculos, lo convierte a la lista oficial
                   de objetos Estacionamiento y la respalda en memoria secundaria.
    Entradas:
        - cantidad(int): La cantidad de vehiculos a solicitar al API.
    Salidas:
        - cantidadObtenida(int): La cantidad de vehiculos que se lograron procesar.
    """
    global listaEstacionamiento
    urlApi = "https://api.mockaroo.com/api/generate.json?key=DEMO&schema=cars"
    datosApi = consultarApiVehiculos(urlApi, cantidad)
    diccionarioVehiculos = construirDiccionarioVehiculos(datosApi)
    listaEstacionamiento = crearListaDeObjetos(diccionarioVehiculos)
    guardarBaseDeDatos()
    return len(listaEstacionamiento)
