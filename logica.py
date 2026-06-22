# Elaborado por: Alejandro Madrigal y Brandon Meza
# Fecha de creacion: 21/06/2026
# Ultima modificacion: 22/06/2026
# Version de Python: 3.11

import pickle

# =========================================================
# Lista global que funciona como la base de datos del estacionamiento.
# Cada elemento es un objeto de la clase Estacionamiento (se agrega en
# avances posteriores).
listaEstacionamiento = []
# =========================================================


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
