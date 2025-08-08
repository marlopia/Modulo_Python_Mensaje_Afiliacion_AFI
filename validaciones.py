"""Módulo de validaciones de datos"""  # TODO agregar atributo obligatorio booleano y comprobar en el resto del codigo

import re
from stdnum.es import cif


class AfiError(Exception):
    """Excepción base para errores relacionados con archivos .afi."""


class ValidacionError(AfiError):
    """Excepción personalizada para errores de validación de datos."""


class LongitudLineaError(AfiError):
    """Excepción lanzada cuando una línea no cumple con la longitud esperada."""


class Validaciones:
    """Contiene métodos estáticos para realizar validaciones comunes sobre datos."""

    @staticmethod
    def validar_numeros(archivo, seccion, nombre_seccion, fila, columna):
        """
        Valida que la sección sea un número (dígitos únicamente).

        Args:
            archivo (str): Nombre del archivo que se está procesando.
            seccion (str): Texto de la sección a validar.
            nombre_seccion (str): Nombre legible de la sección.
            fila (int): Número de fila en el archivo.
            columna (int): Índice de la sección dentro de la línea.

        Raises:
            ValidacionError: Si la sección no es un número.

        Returns:
            str: La sección validada.
        """
        if not seccion.isdigit():
            raise ValidacionError(
                f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                f"(pos {columna + 1}): '{seccion}' no es un número válido."
            )
        return seccion

    @staticmethod
    def validar_letras(archivo, seccion, nombre_seccion, fila, columna):
        """
        Valida que la sección sea un string estríctamente alfabético (string vacío es false).

        Args:
            archivo (str): Nombre del archivo que se está procesando.
            seccion (str): Texto de la sección a validar.
            nombre_seccion (str): Nombre legible de la sección.
            fila (int): Número de fila en el archivo.
            columna (int): Índice de la sección dentro de la línea.

        Raises:
            ValidacionError: Si la sección contiene algo que no sea caracteres alfabéticos.

        Returns:
            str: La sección validada.
        """
        if not seccion.isalpha():
            raise ValidacionError(
                f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                f"(pos {columna + 1}): '{seccion}' no es una cadena exclusivamente alfabética."
            )
        return seccion

    @staticmethod
    def validar_tipo_documento(archivo, seccion, nombre_seccion, fila, columna, tipo):
        """
        Valida que el tipo de documento de la seccion concuerde con el documento introducido.
        No valida los casos de gente sin documento (L,M)

        Args:
            archivo (str): Nombre del archivo que se está procesando.
            seccion (str): Texto de la sección a validar.
            nombre_seccion (str): Nombre legible de la sección.
            fila (int): Número de fila en el archivo.
            columna (int): Índice de la sección dentro de la línea.
            tipo (str): Tipo de documento (consultar diccionarios en caso de duda)

        Raises:
            ValidacionError: Si la sección no es del tipo de documento correcto.

        Returns:
            str: La sección validada.
        """
        seccion = seccion.lstrip("0")  # Limpiar padding de ceros
        tipo = tipo[0]  # Ignorar texto de tipo
        regex_dni = r"^[0-9]{8}[A-Z]$"
        regex_nie = r"^[XYZ][0-9]{7}[A-Z]$"
        regex_pasaporte = (
            r"^[A-Z0-9]{6,9}$"  # Algo generalista, cubre pasaportes internacionales
        )
        if tipo == "1":  # DNI
            if not re.match(regex_dni, seccion):
                raise ValidacionError(
                    f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                    f"(pos {columna + 1}): '{seccion}' no es un número de DNI válido."
                )
        elif tipo == "2":  # Pasaporte
            if not re.match(regex_pasaporte, seccion):
                raise ValidacionError(
                    f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                    f"(pos {columna + 1}): '{seccion}' no es un número de pasaporte válido."
                )
        elif tipo == "6":  # NIE
            if not re.match(regex_nie, seccion):
                raise ValidacionError(
                    f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                    f"(pos {columna + 1}): '{seccion}' no es un número de NIE válido."
                )
        elif tipo == "9":  # CIF
            if not cif.is_valid(seccion):
                raise ValidacionError(
                    f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                    f"(pos {columna + 1}): '{seccion}' no es un número de CIF válido."
                )
        return seccion

    @staticmethod
    def validar_diccionario(
        archivo, seccion, nombre_seccion, fila, columna, diccionario, nullable=False
    ):
        """
        Valida que la sección exista como clave en un diccionario de referencia.
        Si es una cadena vacía no valida (para las secciones opcionales)

        Args:
            archivo (str): Nombre del archivo que se está procesando.
            seccion (str): Texto de la sección a validar.
            nombre_seccion (str): Nombre legible de la sección.
            fila (int): Número de fila en el archivo.
            columna (int): Índice de la sección dentro de la línea.
            diccionario (dict): Diccionario con claves válidas.
            nullable (bool): Si True permite que la seccion esté vacía para secciones condicionales

        Raises:
            ValidacionError: Si la sección está vacía o no está en el diccionario.

        Returns:
            str: La sección validada, concatenada con la etiqueta del diccionario.
        """
        if nullable and (seccion is None or seccion.strip() == ""):
            return seccion

        if seccion.strip() == "" or seccion not in diccionario:
            raise ValidacionError(
                f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                f"(pos {columna + 1}): '{seccion}' no coincide con ninguno de los siguientes "
                f"valores: {list(diccionario.keys())}"
            )
        etiqueta = diccionario[seccion]
        return seccion + f"('{etiqueta}')"

    @staticmethod
    def validar_obligatorio(archivo, seccion, nombre_seccion, fila, columna):
        """
        Valida que la sección no esté vacía.

        Args:
            archivo (str): Nombre del archivo que se está procesando.
            seccion (str): Texto de la sección a validar.
            nombre_seccion (str): Nombre legible de la sección.
            fila (int): Número de fila en el archivo.
            columna (int): Índice de la sección dentro de la línea.

        Raises:
            ValidacionError: Si la sección está vacía.

        Returns:
            str: La sección validada.
        """
        if seccion.strip() == "":
            raise ValidacionError(
                f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                f"(pos {columna + 1}): '{seccion}' no puede estar vacío."
            )
        return seccion

    @staticmethod
    def validar_valores(archivo, seccion, nombre_seccion, fila, columna, valores):
        """
        Valida que la sección se encuentre en una lista de valores permitidos.

        Args:
            archivo (str): Nombre del archivo que se está procesando.
            seccion (str): Texto de la sección a validar.
            nombre_seccion (str): Nombre legible de la sección.
            fila (int): Número de fila en el archivo.
            columna (int): Índice de la sección dentro de la línea.
            valores (list): Lista de valores válidos.

        Raises:
            ValidacionError: Si la sección no está en los valores válidos.

        Returns:
            str: La sección validada.
        """
        if seccion not in valores:
            raise ValidacionError(
                f"Error en archivo '{archivo}', fila {fila}, sección '{nombre_seccion}' "
                f"(pos {columna + 1}): '{seccion}' no coincide con ninguno de los siguientes "
                f"valores: '{valores}'."
            )
        return seccion

    @staticmethod
    def validar_longitudes(nombre_archivo, lineas, longitud=70):
        """
        Valida que todas las líneas del archivo tengan la longitud especificada.

        Args:
            nombre_archivo (str): Nombre del archivo que se está procesando.
            lineas (list): Lista de líneas de texto.
            longitud (int, optional): Longitud esperada de cada línea. Por defecto es 70.

        Raises:
            LongitudLineaError: Si alguna línea no cumple con la longitud requerida.
        """
        for idx, linea in enumerate(lineas, start=1):
            if len(linea) != longitud:
                raise LongitudLineaError(
                    f"{nombre_archivo}, línea {idx}: longitud {len(linea)} != {longitud}"
                )
