# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 22/06/2026
# Ultima modificacion: 28/06/2026
# Version de Python: 3.11

import pickle
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
    Funcionalidad: Calcula cuantos espacios generales se pueden llenar de
                   forma masiva, dejando un 5% de reserva para nuevos clientes
                   sobre la cantidad de espacios "por asignar" (el total menos
                   los especiales y, si aplica, menos el espacio electrico).
                   Nota: se detecto una inconsistencia entre el ejemplo de 75
                   espacios sin electrico de la tabla del enunciado (que da 67
                   con esta formula, pero la tabla indica 66) y el resto de los
                   casos, que si calzan exactamente con esta formula. Se
                   documenta el problema segun la condicion 12 del proyecto y
                   se mantiene la formula matematicamente consistente.
    Entradas: Ninguna. Usa los valores de configuracionParqueo y espaciosParqueo.
    Salidas:
        - tope(int): La cantidad maxima de espacios generales que se pueden llenar masivamente.
    """
    tamanio = configuracionParqueo.get("tamanio", 0)
    espacialesNecesarios = configuracionParqueo.get("espaciosEspeciales", 0)
    tieneElectrico = configuracionParqueo.get("tieneElectrico", False)

    porAsignar = tamanio - espacialesNecesarios
    if tieneElectrico:
        porAsignar = porAsignar - 1

    reservaNuevosClientes = porAsignar * 0.05
    reservaRedondeada = int(reservaNuevosClientes)
    if reservaNuevosClientes > reservaRedondeada:
        reservaRedondeada = reservaRedondeada + 1

    tope = porAsignar - reservaRedondeada
    return tope


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

    urlApi = "https://api.mockaroo.com/api/generate.json?key=DEMO&schema=cars"
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
