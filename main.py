"""
Toda documentación en PDF (tablas) de la seguridad social sacada de
https://www.seg-social.es/wps/portal/wss/internet/InformacionUtil/5300/1889/39740/3383/3389
Todo campo con "reservado" debería de ser un empty string a no ser que se indique
lo contrario (rellenar con 0 por ejemplo)
Si algun enlace a alguna tabla se rompe por actualizaciones de la seguridad social,
mirar el numero de tabla en el enlace y buscar
(i.e. T02-R%C3%A9gimen+Sector+2019-06.pdf?MOD=AJPERES refiere a la tabla T02)
"""

import os
from afi_archivo import AfiArchivo
from validaciones import LongitudLineaError


def cargar_afi_desde_carpeta(ruta_carpeta="afi"):
    """
    Carga todos los archivos con extensión '.afi' desde una carpeta especificada.

    Args:
        ruta_carpeta (str, optional): Ruta de la carpeta donde buscar los archivos '.afi'.
            Por defecto es "afi".

    Returns:
        dict: Un diccionario donde las claves son los nombres de archivo y los valores
        son listas de líneas del archivo, sin el carácter de nueva línea.
    """
    afi_files = {}
    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith(".afi"):
            ruta = os.path.join(ruta_carpeta, archivo)
            with open(ruta, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            afi_files[archivo] = [linea.rstrip("\n") for linea in lineas]
    return afi_files


def main():
    """
    Ejecuta el proceso principal:
    carga archivos, valida longitudes, parsea y muestra errores y resultados.
    """
    afi_data = cargar_afi_desde_carpeta()
    errores_longitud = {}
    errores_parseo = {}
    resultados = {}

    for archivo, lineas in afi_data.items():
        afi = AfiArchivo(archivo, lineas)

        # Validación de longitud
        try:
            afi.validar_longitud()
        except LongitudLineaError as e:
            errores_longitud[archivo] = [str(e)]
            continue  # Saltar este archivo

        # Intentar parsear todo el archivo
        afi.parsear()

        # Guardar resultados y errores
        resultados[archivo] = afi.resultados
        if afi.errores_parseo:
            errores_parseo[archivo] = afi.errores_parseo

    # Mostrar errores de longitud
    if errores_longitud:
        print("Errores de longitud encontrados:")
        for archivo, lista in errores_longitud.items():
            print(f"Archivo: {archivo}")
            for err in lista:
                print("  ", err)
    else:
        print("No se encontraron errores de longitud.")

    # Mostrar errores de parseo
    if errores_parseo:
        print("\nErrores de parseo encontrados:")
        for archivo, lista in errores_parseo.items():
            print(f"Archivo: {archivo}")
            for err in lista:
                print("  ", err)
    else:
        print("\nNo se encontraron errores de parseo.")

    # Mostrar resultados parseados (opcional)
    # for archivo, datos in resultados.items():
    #     print(f"\nDatos parseados para archivo: {archivo}")
    #     for item in datos:
    #         print(item)


if __name__ == "__main__":
    main()
