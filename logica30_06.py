# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 22/06/2026
# Ultima modificacion: 29/06/2026
# Version de Python: 3.11

import pickle
import math
import requests
import qrcode
import random
from fpdf import FPDF
from datetime import datetime, timedelta



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
    "tamaño": 0,
    "tiempoGracia": 0,
    "montoHora": 0,
    "tieneElectrico": False,
    "espaciosEspeciales": 0,
    
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
    """
    global listaEstacionamiento
    try:
        archivo = open("estacionamiento.pkl", "rb")
        tempLista = pickle.load(archivo)
        archivo.close()
        
        # Actualizamos sin romper la referencia
        listaEstacionamiento.clear()
        listaEstacionamiento.extend(tempLista)
        return True
    except:
        listaEstacionamiento.clear()
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
    urlApi = "https://api.mockaroo.com/api/5d28e7d0?count=100&key=32bdcb90"
    datosApi = consultarApiVehiculos(urlApi, cantidad)
    diccionarioVehiculos = construirDiccionarioVehiculos(datosApi)
    listaEstacionamiento.clear()
    listaEstacionamiento.extend(crearListaDeObjetos(diccionarioVehiculos))
    guardarBaseDeDatos()
    return len(listaEstacionamiento)


# =========================================================
# CONFIGURACION DEL PARQUEO
# =========================================================

def calcularEspaciosEspeciales(tamaño):
    """
    Funcionalidad: Calcula la cantidad de espacios especiales segun la ley
                   costarricense (5% del tamaño), respetando el minimo de 2
                   espacios si el parqueo es pequeno.
    Entradas:
        - tamaño(int): El tamaño total del estacionamiento.
    Salidas:
        - cantidad(int): La cantidad de espacios especiales a reservar.
    """
    cantidadCalculada = tamaño * 0.05
    cantidadRedondeada = int(cantidadCalculada)
    if cantidadCalculada > cantidadRedondeada:
        cantidadRedondeada = cantidadRedondeada + 1
    if cantidadRedondeada < 2:
        cantidadRedondeada = 2
    return cantidadRedondeada


def guardarConfiguracion(tamaño, tiempoGracia, montoHora, tieneElectrico):
    """
    Funcionalidad: Guarda los valores de configuracion en el diccionario
                   global configuracionParqueo, calcula los espacios
                   especiales segun la ley y crea la estructura de espacios.
    Entradas:
        - tamaño(int): El tamaño del estacionamiento.
        - tiempoGracia(int): El tiempo de gracia en minutos.
        - montoHora(int): El monto a cobrar por hora en colones.
        - tieneElectrico(bool): Si el parqueo tiene espacio para electricos.
    Salidas: Ninguna. Modifica configuracionParqueo y espaciosParqueo.
    """
    global configuracionParqueo, espaciosParqueo

    espacialesNecesarios = calcularEspaciosEspeciales(tamaño)

    configuracionParqueo["tamaño"] = tamaño
    configuracionParqueo["tiempoGracia"] = tiempoGracia
    configuracionParqueo["montoHora"] = montoHora
    configuracionParqueo["tieneElectrico"] = tieneElectrico
    configuracionParqueo["espaciosEspeciales"] = espacialesNecesarios

    espaciosParqueo.clear()
    numeroEspacio = 1
    while numeroEspacio <= tamaño:
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
    Funcionalidad: Carga la configuración y los espacios desde el archivo pkl 
                   sin romper la referencia de memoria.
    Entradas: Ninguna.
    Salidas: 
    - exito(bool): True si cargó, False si falló.
    """
    global configuracionParqueo, espaciosParqueo
    try:
        import pickle
        with open("configuracion.pkl", "rb") as archivo:
            tempConfig, tempEspacios = pickle.load(archivo)
        
        configuracionParqueo.clear()
        configuracionParqueo.update(tempConfig)
        
        espaciosParqueo.clear()
        espaciosParqueo.extend(tempEspacios)
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


# =========================================================
# PAGAR UN ESPACIO
# =========================================================

def buscarObjetoActivoPorEspacio(numeroEspacio):
    """
    Funcionalidad: Busca en listaEstacionamiento el objeto cuya estadia
                   corresponda al espacio indicado y que aun no tenga fecha
                   de salida registrada.
    Entradas:
        - numeroEspacio(int): El numero de espacio que se quiere buscar.
    Salidas:
        - objeto(Estacionamiento): El objeto encontrado, o None si no existe.
    """
    for objeto in listaEstacionamiento:
        if objeto.estadia[0] == numeroEspacio and objeto.estadia[2] is None:
            return objeto
    return None


def calcularTiempoEstacionado(fechaHoraEntrada, fechaHoraSalida):
    """
    Funcionalidad: Calcula la cantidad de horas y minutos transcurridos entre
                   la entrada y la salida de un vehiculo.
    Entradas:
        - fechaHoraEntrada(datetime): El momento en que entro el vehiculo.
        - fechaHoraSalida(datetime): El momento en que sale el vehiculo.
    Salidas:
        - horas(int): La cantidad de horas completas transcurridas.
        - minutos(int): Los minutos restantes despues de las horas completas.
    """
    diferencia = fechaHoraSalida - fechaHoraEntrada
    totalMinutos = int(diferencia.total_seconds() // 60)
    horas = totalMinutos // 60
    minutos = totalMinutos % 60
    return horas, minutos


def calcularMontoAPagar(fechaHoraEntrada, fechaHoraSalida, montoHora, tiempoGraciaMinutos):
    """
    Funcionalidad: Calcula el monto a pagar segun el tiempo estacionado.
                   Si el tiempo total es menor o igual al tiempo de gracia,
                   el monto es 0. Cualquier fraccion de hora se cobra como
                   una hora completa adicional.
    Entradas:
        - fechaHoraEntrada(datetime): El momento en que entro el vehiculo.
        - fechaHoraSalida(datetime): El momento en que sale el vehiculo.
        - montoHora(int): El monto que se cobra por cada hora completa.
        - tiempoGraciaMinutos(int): Los minutos de gracia sin cobro.
    Salidas:
        - monto(int): El monto total a pagar en colones.
    """
    diferencia = fechaHoraSalida - fechaHoraEntrada
    totalMinutos = int(diferencia.total_seconds() // 60)

    if totalMinutos <= tiempoGraciaMinutos:
        return 0

    horas = totalMinutos // 60
    minutosRestantes = totalMinutos % 60
    if minutosRestantes > 0:
        horas = horas + 1
    if horas == 0:
        horas = 1

    return horas * montoHora


def obtenerCodigoTipoPago(nombreTipoPago):
    """
    Funcionalidad: Convierte el nombre del tipo de pago a su codigo numerico
                   segun lo indicado en el proyecto (1 efectivo, 2 SINPE, 3 tarjeta).
    Entradas:
        - nombreTipoPago(str): El nombre del tipo de pago elegido por el usuario.
    Salidas:
        - codigo(int): El codigo numerico del tipo de pago.
    """
    codigosTipoPago = {"Efectivo": 1, "SINPE": 2, "Tarjeta": 3}
    return codigosTipoPago.get(nombreTipoPago, 0)


def obtenerNombreTipoPago(codigoTipoPago):
    """
    Funcionalidad: Convierte el codigo numerico de tipo de pago a su nombre legible.
    Entradas:
        - codigoTipoPago(int): El codigo del tipo de pago (1, 2 o 3).
    Salidas:
        - nombre(str): El nombre legible del tipo de pago.
    """
    nombresTipoPago = {1: "Efectivo", 2: "SINPE", 3: "Tarjeta"}
    return nombresTipoPago.get(codigoTipoPago, "Desconocido")


def generarNombreFactura(placa, fechaHoraSalida):
    """
    Funcionalidad: Construye el nombre del archivo de factura con el formato
                   factura_#PLACA_DD-MM-AAAA_HH-mm.pdf indicado en el proyecto.
    Entradas:
        - placa(str): La placa del vehiculo.
        - fechaHoraSalida(datetime): La fecha y hora de salida del vehiculo.
    Salidas:
        - nombreArchivo(str): El nombre del archivo PDF a generar.
    """
    selloTiempo = fechaHoraSalida.strftime("%d-%m-%Y_%H-%M")
    return "factura_" + placa + "_" + selloTiempo + ".pdf"


def generarFacturaPdf(objeto, montoAPagar, nombreTipoPago):
    """
    Funcionalidad: Genera la factura en formato PDF con la informacion
                   completa de la estadia del vehiculo, incluyendo su codigo QR.
    Entradas:
        - objeto(Estacionamiento): El objeto con la informacion completa del vehiculo.
        - montoAPagar(int): El monto final que se cobro por la estadia.
        - nombreTipoPago(str): El nombre del tipo de pago utilizado.
    Salidas:
        - nombreArchivo(str): El nombre del archivo PDF generado.
    """
    placa, marca, color, tipo = objeto.info
    numeroEspacio, fechaHoraEntrada, fechaHoraSalida = objeto.estadia
    horas, minutos = calcularTiempoEstacionado(fechaHoraEntrada, fechaHoraSalida)

    textoQr = placa + "-" + marca + "-" + tipo + "-" + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M")
    rutaImagenQr = "qr_temporal_factura_" + placa + ".png"
    generarCodigoQr(textoQr, rutaImagenQr)

    nombreArchivo = generarNombreFactura(placa, fechaHoraSalida)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Factura de Estacionamiento", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(8)
    pdf.cell(0, 8, "Placa: " + placa, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Marca: " + marca, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Color: " + color, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Tipo: " + tipo, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Ubicacion: Espacio #" + str(numeroEspacio), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Hora de entrada: " + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Hora de salida: " + fechaHoraSalida.strftime("%d/%m/%Y %H:%M"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Tiempo estacionado: " + str(horas) + "h " + str(minutos) + "min", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Tipo de pago: " + nombreTipoPago, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Monto a pagar: " + str(montoAPagar) + " colones", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.image(rutaImagenQr, x=75, w=60)

    pdf.output(nombreArchivo)
    return nombreArchivo


def pagarEspacio(numeroEspacio, nombreTipoPago):
    """
    Funcionalidad: Funcion principal para pagar un espacio. Calcula el monto
                   segun el tiempo estacionado, registra la fecha de salida,
                   el tipo de pago y el monto en el objeto correspondiente,
                   libera el espacio, respalda la base de datos y genera la
                   factura en PDF.
    Entradas:
        - numeroEspacio(int): El numero de espacio que se va a liberar.
        - nombreTipoPago(str): El tipo de pago elegido (Efectivo, SINPE o Tarjeta).
    Salidas:
        - resultado(tuple): Tupla con (nombreFactura, montoAPagar).
    """
    objeto = buscarObjetoActivoPorEspacio(numeroEspacio)
    if objeto is None:
        return None, 0

    fechaHoraSalida = datetime.now()
    fechaHoraEntrada = objeto.estadia[1]

    montoAPagar = calcularMontoAPagar(
        fechaHoraEntrada,
        fechaHoraSalida,
        configuracionParqueo.get("montoHora", 0),
        configuracionParqueo.get("tiempoGracia", 0)
    )

    codigoTipoPago = obtenerCodigoTipoPago(nombreTipoPago)

    objeto.estadia[2] = fechaHoraSalida
    objeto.pago = (montoAPagar, codigoTipoPago)

    indiceEspacio = buscarEspacioPorNumero(numeroEspacio)
    espaciosParqueo[indiceEspacio]["ocupado"] = False
    espaciosParqueo[indiceEspacio]["vehiculo"] = None

    guardarBaseDeDatos()
    guardarConfiguracionDisco()

    nombreFactura = generarFacturaPdf(objeto, montoAPagar, nombreTipoPago)
    return nombreFactura, montoAPagar


# =========================================================
# RESERVA MASIVA DE VEHICULOS
# =========================================================

def calcularTopeMasivoGeneral():
    """
    Funcionalidad: Calcula la cantidad de espacios generales disponibles para llenado masivo 
                   respetando las leyes vigentes (especiales, eléctricos y margen de seguridad).
    Entradas: Ninguna.
    Salidas: 
    - n(int): Tope máximo de espacios generales a llenar.
    """
    total = configuracionParqueo['tamaño']
    
    # Ley: 5% especiales, min 2
    esp_especiales = max(2, math.ceil(total * 0.05))
    
    # Ley: Restar eléctrico si existe
    esp_electrico = 1 if configuracionParqueo.get('tieneElectrico', False) else 0
    
    # Disponibles reales para alquilar
    disponibles_alquiler = total - esp_especiales - esp_electrico
    
    # Ley: 5% de reserva obligatoria para clientes nuevos
    margen_seguridad = math.ceil(disponibles_alquiler * 0.05)
    
    tope = disponibles_alquiler - margen_seguridad
    return max(0, tope)


def generarHoraAleatoriaEntrada():
    """
    Funcionalidad: Genera una fecha y hora de entrada aleatoria entre las
                   7:00am del dia actual y la hora actual del sistema.
    Entradas: Ninguna.
    Salidas:
        - fechaHoraEntrada(datetime): La fecha y hora aleatoria generada.
    """
    ahora = datetime.now()
    aperturaParqueo = ahora.replace(hour=7, minute=0, second=0, microsecond=0)

    if ahora <= aperturaParqueo:
        return aperturaParqueo

    segundosDisponibles = int((ahora - aperturaParqueo).total_seconds())
    segundosAleatorios = random.randint(0, segundosDisponibles)
    return aperturaParqueo + timedelta(seconds=segundosAleatorios)


def reservarMasivamente():
    """
    Funcionalidad: Funcion principal de la reserva masiva. Calcula el tope
                   de espacios generales que se pueden llenar, solicita esa
                   cantidad de vehiculos al API, asigna cada uno a un espacio
                   general libre con hora de entrada aleatoria, genera su
                   voucher y respalda la base de datos.
    Entradas: Ninguna. Usa los valores globales de configuracion y espacios.
    Salidas:
        - cantidadReservada(int): La cantidad de vehiculos que se lograron reservar.
    """
    global listaEstacionamiento

    topeMasivo = calcularTopeMasivoGeneral()
    espaciosLibresGenerales = obtenerEspaciosLibres("General")

    cantidadAReservar = min(topeMasivo, len(espaciosLibresGenerales))
    if cantidadAReservar <= 0:
        return 0

    urlApi = "https://api.mockaroo.com/api/5d28e7d0?count=100&key=32bdcb90"
    datosApi = consultarApiVehiculos(urlApi, cantidadAReservar)
    diccionarioVehiculos = construirDiccionarioVehiculos(datosApi)

    listaPlacas = list(diccionarioVehiculos.keys())
    cantidadReservada = 0

    for i in range(cantidadAReservar):
        if i >= len(listaPlacas):
            break

        placa = listaPlacas[i]
        datosVehiculo = diccionarioVehiculos[placa]
        numeroEspacio = espaciosLibresGenerales[i]
        colorAsignado = random.choice(coloresDisponibles)

        indiceEspacio = buscarEspacioPorNumero(numeroEspacio)
        espaciosParqueo[indiceEspacio]["ocupado"] = True
        espaciosParqueo[indiceEspacio]["vehiculo"] = placa

        fechaHoraEntrada = generarHoraAleatoriaEntrada()

        info = (placa, datosVehiculo["marca"], colorAsignado, datosVehiculo["tipo"])
        estadia = [numeroEspacio, fechaHoraEntrada, None]
        pago = (0, 0)

        nuevoId = str(len(listaEstacionamiento) + 1)
        nuevoObjeto = Estacionamiento(nuevoId, info, estadia, pago)
        listaEstacionamiento.append(nuevoObjeto)

        generarVoucherPdf(placa, datosVehiculo["marca"], datosVehiculo["tipo"], numeroEspacio, fechaHoraEntrada)
        cantidadReservada = cantidadReservada + 1

    guardarBaseDeDatos()
    guardarConfiguracionDisco()
    return cantidadReservada


# =========================================================
# CIERRE DIARIO
# =========================================================

def obtenerObjetosPendientes():
    """
    Funcionalidad: Retorna la lista de objetos Estacionamiento que aun no
                   tienen registrada su fecha de salida (vehiculos pendientes
                   de pago al momento del cierre).
    Entradas: Ninguna. Usa la lista global listaEstacionamiento.
    Salidas:
        - pendientes(list): Lista de objetos Estacionamiento sin fecha de salida.
    """
    pendientes = []
    for objeto in listaEstacionamiento:
        if objeto.estadia[2] is None:
            pendientes.append(objeto)
    return pendientes


def facturarPendientes():
    """
    Funcionalidad: Cobra automaticamente todos los vehiculos pendientes al
                   momento del cierre diario, asignandoles un tipo de pago
                   aleatorio y liberando sus espacios.
    Entradas: Ninguna. Usa las listas globales listaEstacionamiento y espaciosParqueo.
    Salidas:
        - cantidadFacturada(int): La cantidad de vehiculos que se lograron facturar.
    """
    opcionesTipoPago = ["Efectivo", "SINPE", "Tarjeta"]
    pendientes = obtenerObjetosPendientes()
    cantidadFacturada = 0

    for objeto in pendientes:
        numeroEspacio = objeto.estadia[0]
        tipoPagoAleatorio = random.choice(opcionesTipoPago)
        nombreFactura, monto = pagarEspacio(numeroEspacio, tipoPagoAleatorio)
        if nombreFactura is not None:
            cantidadFacturada = cantidadFacturada + 1

    return cantidadFacturada


def obtenerVehiculosDelDia():
    """
    Funcionalidad: Retorna la lista de objetos Estacionamiento que ya tienen
                   registrada su fecha de salida (ya pagaron), para construir
                   el reporte de cierre diario.
    Entradas: Ninguna. Usa la lista global listaEstacionamiento.
    Salidas:
        - vehiculosDelDia(list): Lista de objetos con estadia completa.
    """
    vehiculosDelDia = []
    for objeto in listaEstacionamiento:
        if objeto.estadia[2] is not None:
            vehiculosDelDia.append(objeto)
    return vehiculosDelDia


def calcularTotalesPorTipoPago(vehiculosDelDia):
    """
    Funcionalidad: Calcula el monto total recaudado para cada tipo de pago
                   (efectivo, SINPE, tarjeta) y el monto total general del dia.
    Entradas:
        - vehiculosDelDia(list): Lista de objetos Estacionamiento ya pagados.
    Salidas:
        - totales(dict): Diccionario con los totales por tipo de pago y el total general.
    """
    totales = {1: 0, 2: 0, 3: 0}
    for objeto in vehiculosDelDia:
        monto, codigoTipoPago = objeto.pago
        if codigoTipoPago in totales:
            totales[codigoTipoPago] = totales[codigoTipoPago] + monto

    totalGeneral = totales[1] + totales[2] + totales[3]
    return totales, totalGeneral


def generarReporteCierreDiarioHtml(vehiculosDelDia, totales, totalGeneral):
    """
    Funcionalidad: Genera el reporte de cierre diario en formato HTML, usando
                   3 colores y 3 tamanos de letra distintos como exige el
                   proyecto. Incluye titulo, fecha, tabla de movimientos y
                   los totales por tipo de pago.
    Entradas:
        - vehiculosDelDia(list): Lista de objetos Estacionamiento ya pagados.
        - totales(dict): Diccionario con los totales por tipo de pago.
        - totalGeneral(int): El monto total recaudado en el dia.
    Salidas:
        - nombreArchivo(str): El nombre del archivo HTML generado.
    """
    fechaHoraReporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    filasTabla = ""
    for objeto in vehiculosDelDia:
        placa, marca, color, tipo = objeto.info
        numeroEspacio, fechaHoraEntrada, fechaHoraSalida = objeto.estadia
        monto, codigoTipoPago = objeto.pago
        nombreTipoPago = obtenerNombreTipoPago(codigoTipoPago)

        filasTabla = filasTabla + "<tr>"
        filasTabla = filasTabla + "<td>" + str(numeroEspacio) + "</td>"
        filasTabla = filasTabla + "<td>" + placa + "</td>"
        filasTabla = filasTabla + "<td>" + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M") + "</td>"
        filasTabla = filasTabla + "<td>" + fechaHoraSalida.strftime("%d/%m/%Y %H:%M") + "</td>"
        filasTabla = filasTabla + "<td>" + nombreTipoPago + "</td>"
        filasTabla = filasTabla + "<td>" + str(monto) + "</td>"
        filasTabla = filasTabla + "</tr>"

    htmlReporte = "<!DOCTYPE html>\n"
    htmlReporte = htmlReporte + "<html lang=\"es\">\n<head>\n"
    htmlReporte = htmlReporte + "<meta charset=\"utf-8\"/>\n"
    htmlReporte = htmlReporte + "<title>Cierre Diario</title>\n"
    htmlReporte = htmlReporte + "<style>\n"
    htmlReporte = htmlReporte + "body { font-family: Arial, sans-serif; margin: 30px; }\n"
    htmlReporte = htmlReporte + "h1 { color: #1f4e79; font-size: 26px; }\n"
    htmlReporte = htmlReporte + "h2 { color: #555555; font-size: 16px; }\n"
    htmlReporte = htmlReporte + "table { border-collapse: collapse; width: 100%; margin-top: 20px; }\n"
    htmlReporte = htmlReporte + "th { background-color: #c0392b; color: white; padding: 8px; font-size: 13px; }\n"
    htmlReporte = htmlReporte + "td { border: 1px solid #ddd; padding: 6px; text-align: center; font-size: 12px; }\n"
    htmlReporte = htmlReporte + ".totalTipo { color: #2e8b57; font-size: 14px; font-weight: bold; }\n"
    htmlReporte = htmlReporte + ".totalGeneral { color: #c0392b; font-size: 20px; font-weight: bold; }\n"
    htmlReporte = htmlReporte + "</style>\n</head>\n<body>\n"
    htmlReporte = htmlReporte + "<h1>Cierre Diario - Estacionamiento</h1>\n"
    htmlReporte = htmlReporte + "<h2>Fecha de generacion: " + fechaHoraReporte + "</h2>\n"
    htmlReporte = htmlReporte + "<table>\n"
    htmlReporte = htmlReporte + "<tr><th>Ubicacion</th><th>Placa</th><th>Hora Entrada</th><th>Hora Salida</th><th>Tipo de Pago</th><th>Monto</th></tr>\n"
    htmlReporte = htmlReporte + filasTabla + "\n"
    htmlReporte = htmlReporte + "</table>\n"
    htmlReporte = htmlReporte + "<p class=\"totalTipo\">Total Efectivo: " + str(totales[1]) + " colones</p>\n"
    htmlReporte = htmlReporte + "<p class=\"totalTipo\">Total SINPE: " + str(totales[2]) + " colones</p>\n"
    htmlReporte = htmlReporte + "<p class=\"totalTipo\">Total Tarjeta: " + str(totales[3]) + " colones</p>\n"
    htmlReporte = htmlReporte + "<p class=\"totalGeneral\">Monto Total Acumulado del Dia: " + str(totalGeneral) + " colones</p>\n"
    htmlReporte = htmlReporte + "</body>\n</html>"

    ahora = datetime.now()
    nombreArchivo = "cierre_diario_" + ahora.strftime("%d-%m-%Y_%H-%M-%S") + ".html"
    archivo = open(nombreArchivo, "w", encoding="utf-8")
    archivo.write(htmlReporte)
    archivo.close()

    return nombreArchivo


def ejecutarCierreDiario():
    """
    Funcionalidad: Funcion principal del cierre diario. Factura todos los
                   vehiculos pendientes, calcula los totales por tipo de pago
                   y genera el reporte HTML correspondiente.
    Entradas: Ninguna.
    Salidas:
        - resultado(tuple): Tupla con (nombreArchivo, cantidadFacturada, totalGeneral).
    """
    cantidadFacturada = facturarPendientes()
    vehiculosDelDia = obtenerVehiculosDelDia()
    totales, totalGeneral = calcularTotalesPorTipoPago(vehiculosDelDia)
    nombreArchivo = generarReporteCierreDiarioHtml(vehiculosDelDia, totales, totalGeneral)
    return nombreArchivo, cantidadFacturada, totalGeneral


# =========================================================
# CIERRE POR TIPO DE PAGO (XML)
# =========================================================

def escaparTextoXml(texto):
    """
    Funcionalidad: Reemplaza los caracteres especiales de un texto para que
                   sea valido dentro de un documento XML.
    Entradas:
        - texto(str): El texto original que se va a escribir en el XML.
    Salidas:
        - textoEscapado(str): El texto con los caracteres especiales reemplazados.
    """
    textoEscapado = texto.replace("&", "&amp;")
    textoEscapado = textoEscapado.replace("<", "&lt;")
    textoEscapado = textoEscapado.replace(">", "&gt;")
    return textoEscapado


def construirSeccionXml(nombreSeccion, vehiculosDeEseTipo):
    """
    Funcionalidad: Construye el bloque XML de una sola sección de tipo de
                   pago, con un elemento por cada vehiculo en forma plana.
    Entradas:
        - nombreSeccion(str): El nombre de la etiqueta de la seccion (efectivo, sinpe o tarjeta).
        - vehiculosDeEseTipo(list): Lista de objetos Estacionamiento de ese tipo de pago.
    Salidas:
        - bloqueXml(str): El texto XML correspondiente a esa seccion.
    """
    bloqueXml = "  <" + nombreSeccion + ">\n"

    for objeto in vehiculosDeEseTipo:
        placa, marca, color, tipo = objeto.info
        numeroEspacio, fechaHoraEntrada, fechaHoraSalida = objeto.estadia
        monto, codigoTipoPago = objeto.pago

        bloqueXml = bloqueXml + "    <registro>\n"
        bloqueXml = bloqueXml + "      <id>" + escaparTextoXml(objeto.id) + "</id>\n"
        bloqueXml = bloqueXml + "      <placa>" + escaparTextoXml(placa) + "</placa>\n"
        bloqueXml = bloqueXml + "      <marca>" + escaparTextoXml(marca) + "</marca>\n"
        bloqueXml = bloqueXml + "      <color>" + escaparTextoXml(color) + "</color>\n"
        bloqueXml = bloqueXml + "      <tipo>" + escaparTextoXml(tipo) + "</tipo>\n"
        bloqueXml = bloqueXml + "      <ubicacion>" + str(numeroEspacio) + "</ubicacion>\n"
        bloqueXml = bloqueXml + "      <fechaHoraEntrada>" + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M") + "</fechaHoraEntrada>\n"
        bloqueXml = bloqueXml + "      <fechaHoraSalida>" + fechaHoraSalida.strftime("%d/%m/%Y %H:%M") + "</fechaHoraSalida>\n"
        bloqueXml = bloqueXml + "      <monto>" + str(monto) + "</monto>\n"
        bloqueXml = bloqueXml + "    </registro>\n"

    bloqueXml = bloqueXml + "  </" + nombreSeccion + ">\n"
    return bloqueXml


def generarCierrePorTipoPagoXml():
    """
    Funcionalidad: Genera un archivo XML con 3 secciones (efectivo, sinpe,
                   tarjeta), cada una con la informacion completa y plana de
                   los vehiculos pagados con ese tipo de pago.
    Entradas: Ninguna. Usa la lista global listaEstacionamiento.
    Salidas:
        - nombreArchivo(str): El nombre del archivo XML generado.
    """
    vehiculosDelDia = obtenerVehiculosDelDia()

    vehiculosEfectivo = []
    vehiculosSinpe = []
    vehiculosTarjeta = []

    for objeto in vehiculosDelDia:
        monto, codigoTipoPago = objeto.pago
        if codigoTipoPago == 1:
            vehiculosEfectivo.append(objeto)
        elif codigoTipoPago == 2:
            vehiculosSinpe.append(objeto)
        elif codigoTipoPago == 3:
            vehiculosTarjeta.append(objeto)

    contenidoXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    contenidoXml = contenidoXml + "<cierrePorTipoPago>\n"
    contenidoXml = contenidoXml + construirSeccionXml("efectivo", vehiculosEfectivo)
    contenidoXml = contenidoXml + construirSeccionXml("sinpe", vehiculosSinpe)
    contenidoXml = contenidoXml + construirSeccionXml("tarjeta", vehiculosTarjeta)
    contenidoXml = contenidoXml + "</cierrePorTipoPago>"

    ahora = datetime.now()
    nombreArchivo = "cierre_tipo_pago_" + ahora.strftime("%d-%m-%Y_%H-%M-%S") + ".xml"
    archivo = open(nombreArchivo, "w", encoding="utf-8")
    archivo.write(contenidoXml)
    archivo.close()

    return nombreArchivo


# =========================================================
# EXPORTAR CIERRE DIARIO A CSV
# =========================================================

def exportarCierreDiarioCsv():
    """
    Funcionalidad: Exporta la tabla de movimientos del cierre diario a un
                   archivo CSV sin titulos, para abrirlo en Excel. Cada fila
                   tiene: ubicacion, placa, hora de entrada, hora de salida,
                   tipo de pago y monto.
    Entradas: Ninguna. Usa la lista global listaEstacionamiento.
    Salidas:
        - nombreArchivo(str): El nombre del archivo CSV generado.
    """
    vehiculosDelDia = obtenerVehiculosDelDia()

    contenidoCsv = ""
    for objeto in vehiculosDelDia:
        placa, marca, color, tipo = objeto.info
        numeroEspacio, fechaHoraEntrada, fechaHoraSalida = objeto.estadia
        monto, codigoTipoPago = objeto.pago
        nombreTipoPago = obtenerNombreTipoPago(codigoTipoPago)

        fila = str(numeroEspacio) + ","
        fila = fila + placa + ","
        fila = fila + fechaHoraEntrada.strftime("%d/%m/%Y %H:%M") + ","
        fila = fila + fechaHoraSalida.strftime("%d/%m/%Y %H:%M") + ","
        fila = fila + nombreTipoPago + ","
        fila = fila + str(monto) + "\n"

        contenidoCsv = contenidoCsv + fila

    ahora = datetime.now()
    nombreArchivo = "cierre_diario_" + ahora.strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
    archivo = open(nombreArchivo, "w", encoding="utf-8")
    archivo.write(contenidoCsv)
    archivo.close()

    return nombreArchivo
