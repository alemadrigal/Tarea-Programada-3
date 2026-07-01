import pickle
import json
import urllib.request
import qrcode
from reportlab.pdfgen import canvas
import os
import random
from datetime import datetime, timedelta

def traducirMarca(marca):
    marcas = {1:"Toyota", 2:"Nissan", 3:"Hyundai", 4:"Kia", 5:"Honda", 6:"Suzuki", 7:"Mitsubishi", 8:"BMW", 9:"Mercedes Benz", 10:"Ford"}
    return marcas.get(int(marca), "Otra marca")

def traducirColor(color):
    colores = {1:"Blanco", 2:"Negro", 3:"Gris", 4:"Rojo", 5:"Azul", 6:"Verde", 7:"Plateado", 8:"Café"}
    return colores.get(int(color), "Otro color")

def traducirTipo(tipo):
    tipos = {1:"Sedán", 2:"SUV", 3:"Pick up", 4:"Hatchback", 5:"Microbús", 6:"Camión", 7:"Deportivo", 8:"Eléctrico"}
    return tipos.get(int(tipo), "Otro tipo")

def traducirPago(tipoPago):
    pagos = {1:"Efectivo", 2:"SINPE", 3:"Tarjeta"}
    return pagos.get(int(tipoPago), "Pendiente")

class Estacionamiento:
    def __init__(self, idVeiculo, info, estadia, pago):
        self.id = idVeiculo
        self.info = info
        self.estadia = estadia
        self.pago = pago
        
class ConfiguracionEstacionamiento:
    def __init__(self, cantidadCampos, cantidadElectricos, tiempoGracia, montoHora):
        self.cantidadCampos = cantidadCampos
        self.cantidadElectricos = cantidadElectricos
        self.tiempoGracia = tiempoGracia
        self.montoHora = montoHora

def calcularEspacios(listaEstacionamiento):
    campos = listaEstacionamiento[0].cantidadCampos
    camposElectricos = listaEstacionamiento[0].cantidadElectricos

    especiales = campos * 0.05
    if especiales % 1 != 0:
        especiales = int(especiales) + 1
    else:
        especiales = int(especiales)

    if especiales < 2:
        especiales = 2

    porAsignar = campos - especiales - camposElectricos

    libres = porAsignar * 0.05
    if libres % 1 != 0:
        libres = int(libres) + 1
    else:
        libres = int(libres)

    maxCampo = porAsignar - libres

    return [campos, especiales, camposElectricos, porAsignar, maxCampo]

def obtenerVehiculosApi(listaEstacionamiento, direccionApi):
    datosEspacios = calcularEspacios(listaEstacionamiento)
    maxCampo = datosEspacios[4]
    respuesta = urllib.request.urlopen(direccionApi + str(maxCampo))
    datosApi = json.loads(respuesta.read().decode())
    return datosApi

def generarFechaEntrada():
    ahora = datetime.now()
    inicio = ahora.replace(hour=7, minute=0, second=0, microsecond=0)
    if ahora < inicio:
        return inicio.strftime("%d/%m/%Y %H:%M")
    minutos = int((ahora - inicio).total_seconds() // 60)
    fechaEntrada = inicio + timedelta(minutes=random.randint(0, minutos))
    return fechaEntrada.strftime("%d/%m/%Y %H:%M")

def convertirApiObjetos(datosApi):
    listaObjetos = []
    for vehiculo in datosApi:
        placa = str(vehiculo["placa"])
        marca = traducirMarca(vehiculo["marca"])
        color = traducirColor(vehiculo["color"])
        tipo = traducirTipo(vehiculo["tipo"])
        tipoPago = traducirPago(vehiculo["tipoPago"])
        monto = str(vehiculo["monto"])
        fechaEntrada = generarFechaEntrada()
        nombreArchivo = fechaEntrada.replace("/", "_").replace(":", "_").replace(" ", "_")
        infoQr = "PLACA=" + placa + " | MARCA=" + marca + " | TIPO=" + tipo + " | ENTRADA=" + fechaEntrada
        nombreQr = "qr_" + placa + "_" + nombreArchivo + ".png"
        nombrePdf = "voucher_" + placa + "_" + nombreArchivo + ".pdf"
        qrcode.make(infoQr).save(nombreQr)
        pdf = canvas.Canvas(nombrePdf)
        pdf.drawString(80, 750, "Voucher de estacionamiento")
        pdf.drawString(80, 720, "Placa: " + placa)
        pdf.drawString(80, 700, "Marca: " + marca)
        pdf.drawString(80, 680, "Color: " + color)
        pdf.drawString(80, 660, "Tipo: " + tipo)
        pdf.drawString(80, 640, "Fecha y hora de entrada: " + fechaEntrada)
        pdf.drawImage(nombreQr, 80, 480, width=120, height=120)
        pdf.save()
        os.remove(nombreQr)
        objetoEstacionamiento = Estacionamiento(vehiculo["id"], (placa, marca, color, tipo), [str(vehiculo["ubicacion"]), fechaEntrada, str(vehiculo["fechaHoraSalida"])], (monto, tipoPago))
        listaObjetos.append(objetoEstacionamiento)
    return listaObjetos


def graba(nombreArchivo, lista):
    try:
        archivo = open(nombreArchivo, "wb")
        pickle.dump(lista, archivo)
        archivo.close()
    except:
        print("Error al grabar el archivo:", nombreArchivo)

def lee(nombreArchivo):
    lista = []
    try:
        archivo = open(nombreArchivo, "rb")
        lista = pickle.load(archivo)
        archivo.close()
    except:
        print("No se encontró el archivo:", nombreArchivo,"\n\n")
    return lista

def previsualizar(tamaño, electricos):
    tamañoTotal = int(tamaño)
    
    if tamañoTotal<3:
        return "El estacionamiento debe tener al menos 3 espacios."
    elif electricos == "":
        cantidadElectricos = 0
    else:
        cantidadElectricos = int(electricos)

    especiales = tamañoTotal * 0.05
    if especiales%1 != 0:
        especiales = int(especiales)+1
    else:
        especiales = int(especiales)
    if especiales < 2:
        especiales = 2
    
    texto = ("Tamaño estacionamiento: " + str(tamañoTotal) + "\n"
        "Especiales: " + str(especiales) + "\n"
        "Eléctrico: " + str(cantidadElectricos) + "\n")
    return texto
