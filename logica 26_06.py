# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 22/06/2026
# Ultima modificacion: 26/06/2026
# Version de Python: 3.11

import pickle
import requests
import qrcode
from fpdf import FPDF
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

# Diccionario global de configuracion del estacionamiento.
# Se llena en la ventana de Configuracion (avance pendiente de logica).
configuracionParqueo = {
    "tamanio": 0,
    "tiempoGracia": 0,
    "montoHora": 0,
    "tieneElectrico": False,
    "espaciosEspeciales": 0,
    "espacioElectrico": None
}

# Lista global de los espacios del estacionamiento.
# Cada elemento es un diccionario con la informacion del espacio.
espaciosParqueo = []
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


# =========================================================
# CONFIGURACION DEL PARQUEO
# =========================================================

def calcularEspaciosEspeciales(tamanio):
    """
    Funcionalidad: Calcula la cantidad de espacios especiales segun la ley
                   costarricense (5% del tamanio), respetando el minimo de 2
                   espacios si el parqueo es pequeno.
    Entradas:
        - tamanio(int): El tamanio total del estacionamiento.
    Salidas:
        - cantidad(int): La cantidad de espacios especiales a reservar.
    """
    cantidadCalculada = tamanio * 0.05
    cantidadRedondeada = int(cantidadCalculada)
    if cantidadCalculada > cantidadRedondeada:
        cantidadRedondeada = cantidadRedondeada + 1
    if cantidadRedondeada < 2:
        cantidadRedondeada = 2
    return cantidadRedondeada


def guardarConfiguracion(tamanio, tiempoGracia, montoHora, tieneElectrico):
    """
    Funcionalidad: Guarda los valores de configuracion en el diccionario
                   global configuracionParqueo, calcula los espacios
                   especiales segun la ley y crea la estructura de espacios.
    Entradas:
        - tamanio(int): El tamanio del estacionamiento.
        - tiempoGracia(int): El tiempo de gracia en minutos.
        - montoHora(int): El monto a cobrar por hora en colones.
        - tieneElectrico(bool): Si el parqueo tiene espacio para electricos.
    Salidas: Ninguna. Modifica configuracionParqueo y espaciosParqueo.
    """
    global configuracionParqueo, espaciosParqueo

    espacialesNecesarios = calcularEspaciosEspeciales(tamanio)

    configuracionParqueo["tamanio"] = tamanio
    configuracionParqueo["tiempoGracia"] = tiempoGracia
    configuracionParqueo["montoHora"] = montoHora
    configuracionParqueo["tieneElectrico"] = tieneElectrico
    configuracionParqueo["espaciosEspeciales"] = espacialesNecesarios

    espaciosParqueo = []
    numeroEspacio = 1
    while numeroEspacio <= tamanio:
        if numeroEspacio <= espacialesNecesarios:
            tipoEspacio = "Especial"
        elif tieneElectrico and numeroEspacio == espacialesNecesarios + 1:
            tipoEspacio = "Electrico"
        else:
            tipoEspacio = "General"

        espaciosParqueo.append({
            "numero": numeroEspacio,
            "tipo": tipoEspacio,
            "ocupado": False,
            "vehiculo": None
        })
        numeroEspacio = numeroEspacio + 1

    guardarConfiguracionDisco()


def guardarConfiguracionDisco():
    """
    Funcionalidad: Guarda la configuracion y los espacios actuales en un
                   archivo binario llamado configuracion.pkl.
    Entradas: Ninguna.
    Salidas: Ninguna. Escribe el archivo configuracion.pkl.
    """
    archivo = open("configuracion.pkl", "wb")
    pickle.dump((configuracionParqueo, espaciosParqueo), archivo)
    archivo.close()


def cargarConfiguracionDisco():
    """
    Funcionalidad: Carga la configuracion y los espacios desde el archivo
                   configuracion.pkl en memoria.
    Entradas: Ninguna.
    Salidas: Retorna True si se cargo correctamente, False si no existia el archivo.
    """
    global configuracionParqueo, espaciosParqueo
    try:
        archivo = open("configuracion.pkl", "rb")
        configuracionParqueo, espaciosParqueo = pickle.load(archivo)
        archivo.close()
        return True
    except:
        return False


# =========================================================
# VOUCHER EN PDF CON CODIGO QR
# =========================================================

def generarCodigoQr(textoQr, rutaImagen):
    """
    Funcionalidad: Genera una imagen de codigo QR a partir de un texto y la
                   guarda en disco en la ruta indicada.
    Entradas:
        - textoQr(str): El texto que se va a codificar en el QR.
        - rutaImagen(str): La ruta donde se va a guardar la imagen generada.
    Salidas: Ninguna. Crea el archivo de imagen del codigo QR.
    """
    imagenQr = qrcode.make(textoQr)
    imagenQr.save(rutaImagen)


def generarNombreVoucher(placa, fechaHoraEntrada):
    """
    Funcionalidad: Construye el nombre del archivo del voucher con el formato
                   voucher_#PLACA_DD-MM-AAAA_HH-mm.pdf indicado en el proyecto.
    Entradas:
        - placa(str): La placa del vehiculo.
        - fechaHoraEntrada(datetime): La fecha y hora de entrada del vehiculo.
    Salidas:
        - nombreArchivo(str): El nombre del archivo PDF a generar.
    """
    selloTiempo = fechaHoraEntrada.strftime("%d-%m-%Y_%H-%M")
    return "voucher_" + placa + "_" + selloTiempo + ".pdf"


def generarVoucherPdf(placa, marca, tipo, ubicacion, fechaHoraEntrada):
    """
    Funcionalidad: Genera un voucher en formato PDF con la informacion del
                   vehiculo recien estacionado y un codigo QR que contiene
                   esos mismos datos.
    Entradas:
        - placa(str): La placa del vehiculo.
        - marca(str): La marca del vehiculo.
        - tipo(str): El tipo de vehiculo.
        - ubicacion(int): El numero de espacio asignado.
        - fechaHoraEntrada(datetime): La fecha y hora de entrada.
    Salidas:
        - nombreArchivo(str): El nombre del archivo PDF generado.
    """
    textoQr = placa + "-" + marca + "-" + tipo + "-" + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M")
    rutaImagenQr = "qr_temporal_" + placa + ".png"
    generarCodigoQr(textoQr, rutaImagenQr)

    nombreArchivo = generarNombreVoucher(placa, fechaHoraEntrada)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Voucher de Estacionamiento", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(8)
    pdf.cell(0, 8, "Placa: " + placa, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Marca: " + marca, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Tipo: " + tipo, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Ubicacion: Espacio #" + str(ubicacion), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Hora de entrada: " + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.image(rutaImagenQr, x=75, w=60)

    pdf.output(nombreArchivo)
    return nombreArchivo


# =========================================================
# ESTACIONAR UN VEHICULO
# =========================================================

def buscarEspacioPorNumero(numeroEspacio):
    """
    Funcionalidad: Busca un espacio en la lista global espaciosParqueo segun
                   su numero.
    Entradas:
        - numeroEspacio(int): El numero del espacio a buscar.
    Salidas:
        - indice(int): El indice del espacio en la lista, o -1 si no existe.
    """
    for i in range(len(espaciosParqueo)):
        if espaciosParqueo[i]["numero"] == numeroEspacio:
            return i
    return -1


def obtenerEspaciosLibres(tipoRequerido):
    """
    Funcionalidad: Retorna la lista de numeros de espacio libres que coincidan
                   con el tipo requerido (General, Especial o Electrico).
    Entradas:
        - tipoRequerido(str): El tipo de espacio que se necesita.
    Salidas:
        - numeros(list): Lista de numeros de espacio disponibles de ese tipo.
    """
    numeros = []
    for espacio in espaciosParqueo:
        if espacio["tipo"] == tipoRequerido and not espacio["ocupado"]:
            numeros.append(espacio["numero"])
    return numeros


def estacionarVehiculo(placa, marca, color, tipo, numeroEspacio):
    """
    Funcionalidad: Reserva el espacio indicado, crea el objeto Estacionamiento
                   correspondiente, lo agrega a la base de datos, respalda en
                   memoria secundaria y genera el voucher en PDF con su QR.
    Entradas:
        - placa(str): La placa del vehiculo.
        - marca(str): La marca del vehiculo.
        - color(str): El color del vehiculo.
        - tipo(str): El tipo de vehiculo.
        - numeroEspacio(int): El numero de espacio donde se va a estacionar.
    Salidas:
        - nombreVoucher(str): El nombre del archivo de voucher generado.
    """
    global listaEstacionamiento

    indiceEspacio = buscarEspacioPorNumero(numeroEspacio)
    espaciosParqueo[indiceEspacio]["ocupado"] = True
    espaciosParqueo[indiceEspacio]["vehiculo"] = placa

    fechaHoraEntrada = datetime.now()

    info = (placa, marca, color, tipo)
    estadia = [numeroEspacio, fechaHoraEntrada, None]
    pago = (0, 0)

    nuevoId = str(len(listaEstacionamiento) + 1)
    nuevoObjeto = Estacionamiento(nuevoId, info, estadia, pago)
    listaEstacionamiento.append(nuevoObjeto)

    guardarBaseDeDatos()
    guardarConfiguracionDisco()

    nombreVoucher = generarVoucherPdf(placa, marca, tipo, numeroEspacio, fechaHoraEntrada)
    return nombreVoucher
