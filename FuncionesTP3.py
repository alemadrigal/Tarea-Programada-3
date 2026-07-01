import pickle

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
        print("Error al leer el archivo:", nombreArchivo)
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
