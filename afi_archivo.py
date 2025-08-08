"""Módulo para gestionar archivos AFI"""  # TODO Convertir correctamente las funciones a validar campos

from validaciones import AfiError, Validaciones
import diccionarios


class AfiArchivo(Validaciones):
    """
    Representa un archivo .afi y proporciona métodos para validar y parsear su contenido.

    Hereda de:
        Validaciones: Clase con métodos estáticos para validar contenido de archivos.

    Atributos:
        nombre (str): Nombre del archivo.
        lineas (list[str]): Lista de líneas del archivo.
        resultados (list): Resultados parseados correctamente.
        errores_parseo (list[str]): Lista de errores ocurridos durante el parseo.
        parsers (dict[str, callable]): Diccionario que mapea cabeceras a funciones de parseo.
    """

    def __init__(self, nombre_archivo, lineas):
        """
        Inicializa una instancia de AfiArchivo.

        Args:
            nombre_archivo (str): Nombre del archivo.
            lineas (list[str]): Contenido del archivo como lista de líneas.
        """
        self.nombre = nombre_archivo
        self.lineas = lineas
        self.resultados = []
        self.errores_parseo = []
        self.parsers = {
            "ETI": self.parse_linea_eti,
            "EMP": self.parse_linea_emp,
            "RZS": self.parse_linea_rzs,
            "PES": self.parse_linea_pes,
            "TRA": self.parse_linea_tra,
            "AYN": self.parse_linea_ayn,
            "DOM": self.parse_linea_dom,
            "LDD": self.parse_linea_ldd,
            "FAB": self.parse_linea_fab,
            "DAM": self.parse_linea_dam,
            "ODL": self.parse_linea_odl,
        }

    def validar_longitud(self, longitud=70):
        """
        Valida que todas las líneas del archivo tengan la longitud especificada.

        Args:
            longitud (int, optional): Longitud esperada de cada línea. Por defecto 70.

        Raises:
            LongitudLineaError: Si alguna línea no tiene la longitud esperada.
        """
        self.validar_longitudes(self.nombre, self.lineas, longitud)

    def parsear(self):
        """
        Intenta parsear todas las líneas del archivo utilizando la función correspondiente.
        Guarda los resultados exitosos en `self.resultados` y los errores en `self.errores_parseo`.
        """
        for fila, linea in enumerate(self.lineas, start=1):
            try:
                self.resultados.append(self.parse_linea(fila, linea))
            except (AfiError, ValueError) as e:
                self.errores_parseo.append(f"Fila {fila}: {e}")
                continue

    def parse_linea(self, fila, linea):
        """
        Parsea una línea del archivo usando la función correspondiente según su cabecera.

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Resultado del parseo de la línea.

        Raises:
            ValueError: Si la cabecera de la línea no está reconocida.
        """
        cabecera = linea[0:3]
        parser_func = self.parsers.get(cabecera)
        if parser_func is None:
            raise ValueError(
                f"{self.nombre}, fila {fila}: cabecera desconocida '{cabecera}'"
            )
        return parser_func(fila, linea)

    def parse_linea_eti(self, fila, linea):
        """
        Parsea la linea de ETIquetas de inicio

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre ETI
        sintaxis = self.validar_valores(
            self.nombre, linea[3:7], "sintaxis", fila, 3, ["AFI9"]
        )
        version_mensaje = self.validar_numeros(
            self.nombre, linea[7:8], "version_mensaje", fila, 7
        )
        id_programa = self.validar_obligatorio(
            self.nombre, linea[8:12], "id_programa", fila, 8
        )
        version_proceso = self.validar_obligatorio(
            self.nombre, linea[12:13], "version_proceso", fila, 12
        )
        clave_autorizacion = self.validar_numeros(
            self.nombre, linea[13:21], "version_mensaje", fila, 13
        )
        reservado_1 = linea[21:29]
        fecha = self.validar_numeros(
            self.nombre, linea[29:37], "version_mensaje", fila, 29
        )
        hora = self.validar_numeros(
            self.nombre, linea[37:41], "version_mensaje", fila, 37
        )
        nombre_archivo = self.validar_obligatorio(
            self.nombre, linea[41:49], "nombre_archivo", fila, 41
        )
        extension_archivo = self.validar_valores(
            self.nombre, linea[49:52], "extension_archivo", fila, 49, ["AFI"]
        )
        prioridad = self.validar_valores(
            self.nombre, linea[52:53], "prioridad", fila, 49, ["N"]
        )
        indicador_prueba = linea[53:54]
        # Debe estar vacío, P es prueba, N es no sustitutivo;
        # "Solo afecta a las liquidaciones complementarias del tipo
        # L02, L03, L09 (del mes en curso no), L13, TP2 y A76.
        # Cuando venga consignada esta marca, no se procederá
        # a la sustitución automática de estas liquidaciones por otras
        # presentadas en el mismo período y con idéntico CCC, período
        # de liquidación y tipo de liquidación."
        id_registro_ano = self.validar_numeros(
            self.nombre, linea[54:56], "id_registro_ano", fila, 54
        )
        id_registro_mes = self.validar_numeros(
            self.nombre, linea[56:58], "id_registro_mes", fila, 56
        )
        id_registro_serie = self.validar_numeros(
            self.nombre, linea[58:59], "id_registro_serie", fila, 58
        )
        id_registro_envio = self.validar_numeros(
            self.nombre, linea[59:64], "id_registro_envio", fila, 59
        )
        id_registro_ordinal = self.validar_numeros(
            self.nombre, linea[64:68], "id_registro_ordinal", fila, 64
        )  # Refiere a dentro del lote (num envio), el orden del archivo (i.e. envio 3 archivo 2)
        reservado_2 = linea[68:69]
        reservado_3 = linea[69:70]

        return {
            "cabecera": cabecera,
            "sintaxis": sintaxis,
            "version_mensaje": version_mensaje,
            "id_programa": id_programa,
            "version_proceso": version_proceso,
            "clave_autorizacion": clave_autorizacion,
            "reservado_1": reservado_1,
            "fecha": fecha,
            "hora": hora,
            "nombre_archivo": nombre_archivo,
            "extension_archivo": extension_archivo,
            "prioridad": prioridad,
            "indicador_prueba": indicador_prueba,
            "id_registro_ano": id_registro_ano,
            "id_registro_mes": id_registro_mes,
            "id_registro_serie": id_registro_serie,
            "id_registro_envio": id_registro_envio,
            "id_registro_ordinal": id_registro_ordinal,
            "reservado_2": reservado_2,
            "reservado_3": reservado_3,
        }

    def parse_linea_emp(self, fila, linea):
        """
        Parsea la linea de EMPresa

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre EMP
        seguridad_social_regimen = self.validar_diccionario(
            self.nombre,
            linea[3:7],
            "seguridad_social_regimen",
            fila,
            3,
            diccionarios.REGIMEN_SECTOR,
        )
        seguridad_social_provincia = self.validar_diccionario(
            self.nombre,
            linea[7:9],
            "seguridad_social_provincia",
            fila,
            7,
            diccionarios.PROVINCIAS,
        )
        seguridad_social_numero = self.validar_obligatorio(
            self.nombre, linea[9:18], "id_programa", fila, 8
        )
        empresario_tipo_identificacion = self.validar_diccionario(
            self.nombre,
            linea[18:19],
            "empresario_tipo_identificacion",
            fila,
            18,
            diccionarios.TIPO_IDENTIFICACION,
        )
        empresario_codigo_pais = self.validar_diccionario(
            self.nombre,
            linea[19:22],
            "empresario_codigo_pais",
            fila,
            19,
            diccionarios.PAISES,
        )
        empresario_numero_identificacion = self.validar_tipo_documento(
            self.nombre,
            linea[22:36],
            "empresario_numero_identificacion",
            fila,
            22,
            empresario_tipo_identificacion,
        )  # Padding a la izquierda de ceros
        empresario_calificador = linea[36:38]  # Opcional, subcif
        ccc_regimen = self.validar_diccionario(
            self.nombre,
            linea[38:42],
            "ccc_regimen",
            fila,
            38,
            diccionarios.REGIMEN_SECTOR,
        )
        ccc_provincia = self.validar_diccionario(
            self.nombre,
            linea[42:44],
            "ccc_provincia",
            fila,
            42,
            diccionarios.PROVINCIAS,
        )
        ccc_numero = linea[44:53]  # Codigo Cuenta Cotización (CCC)
        reservado_recaudacion = linea[53:66]
        accion = self.validar_diccionario(
            self.nombre,
            linea[66:69],
            "accion",
            fila,
            66,
            diccionarios.ACCIONES_EMP,
            True,
        )
        reservado = linea[69:70]

        return {
            "cabecera": cabecera,
            "seguridad_social_regimen": seguridad_social_regimen,
            "seguridad_social_provincia": seguridad_social_provincia,
            "seguridad_social_numero": seguridad_social_numero,
            "empresario_tipo_identificacion": empresario_tipo_identificacion,
            "empresario_codigo_pais": empresario_codigo_pais,
            "empresario_numero_identificacion": empresario_numero_identificacion,
            "empresario_calificador": empresario_calificador,
            "ccc_regimen": ccc_regimen,
            "ccc_provincia": ccc_provincia,
            "ccc_numero": ccc_numero,
            "reservado_recaudacion": reservado_recaudacion,
            "accion": accion,
            "reservado": reservado,
        }

    def parse_linea_rzs(self, fila, linea):
        """
        Parsea la línea de RaZón Social

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre RZS
        indicador_rzs = self.validar_valores(
            self.nombre, linea[3:4], "indicador_rzs", fila, 3, ["0", "1", "2", "3", "4"]
        )  # Reservado
        tipo_alfabetico = self.validar_diccionario(
            self.nombre,
            linea[4:5],
            "tipo_alfabetico",
            fila,
            4,
            diccionarios.TIPO_AFABETICO_EMPRESARIO,
        )
        razon_social = linea[5:60]
        clave_autorizacion = linea[60:68]  # Para acción CTA, número de autorización
        reservado = linea[68:70]

        return {
            "cabecera": cabecera,
            "indicador_rzs": indicador_rzs,
            "tipo_alfabetico": tipo_alfabetico,
            "razon_social": razon_social,
            "clave_autorizacion": clave_autorizacion,
            "reservado": reservado,
        }

    def parse_linea_pes(self, fila, linea):
        """
        Parsea la línea de PEculiaridades Solicitadas, Obligatorio para IDC/PL-CCC Acotado

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre PES
        resultado = {"cabecera": cabecera}

        # Generar peculiaridad_1 a peculiaridad_33
        for i in range(33):
            start = 3 + (i * 2)
            end = start + 2
            key = f"peculiaridad_{i+1}"
            resultado[key] = self.validar_diccionario(
                self.nombre,
                linea[start:end],
                key,
                fila,
                start,
                diccionarios.TIPO_PECULIARIDAD_COTIZACION,
            )

        return resultado

    def parse_linea_tra(self, fila, linea):
        """
        Parsea la línea de TRAbajador

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre TRA
        ss_provincia = self.validar_diccionario(
            self.nombre,
            linea[3:5],
            "ss_provincia",
            fila,
            3,
            diccionarios.PROVINCIAS,
        )
        ss_numero = self.validar_numeros(self.nombre, linea[5:15], "ss_numero", fila, 5)
        ipf_tipo = self.validar_diccionario(
            self.nombre,
            linea[15:16],
            "ipf_tipo",
            fila,
            15,
            diccionarios.IPF,
        )
        ipf_pais = self.validar_diccionario(
            self.nombre,
            linea[16:19],
            "ipf_pais",
            fila,
            16,
            diccionarios.PAISES,
        )
        ipf_alfaclave = self.validar_tipo_documento(
            self.nombre,
            linea[19:33],
            "ipf_alfaclave",
            fila,
            19,
            ipf_tipo,
        )  # Padding a la izquierda de ceros
        reservado_respuesta_afi = linea[33:36]
        reservado_recaudacion = linea[36:61]
        if ipf_tipo[0] == "1":
            nacionalidad = linea[61:64]  # Opcional para DNI
        else:
            nacionalidad = self.validar_diccionario(
                self.nombre,
                linea[61:64],
                "nacionalidad",
                fila,
                61,
                diccionarios.PAISES,
            )
        indicador_trabajador = linea[64:65]  # Reservado para futuro uso versión 9.6
        reservado = linea[65:70]

        return {
            "cabecera": cabecera,
            "ss_provincia": ss_provincia,
            "ss_numero": ss_numero,
            "ipf_tipo": ipf_tipo,
            "ipf_pais": ipf_pais,
            "ipf_alfaclave": ipf_alfaclave,
            "reservado_respuesta_afi": reservado_respuesta_afi,
            "reservado_recaudacion": reservado_recaudacion,
            "nacionalidad": nacionalidad,
            "indicador_trabajador": indicador_trabajador,
            "reservado": reservado,
        }

    def parse_linea_ayn(self, fila, linea):
        """Parsea la línea Apellidos Y Nombre

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre AYN
        primer_apellido = self.validar_letras(
            self.nombre, linea[3:23], "primer_apellido", fila, 3
        )
        segundo_apellido = linea[23:43]
        nombre = linea[43:58]
        reservado = linea[58:70]
        return {
            "cabecera": cabecera,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido,
            "nombre": nombre,
            "reservado": reservado,
        }

    def parse_linea_dom(self, fila, linea):
        """
        Parsea la línea de DOMicilio, todos los paramentros menos la cabecera son opcionales

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre DOM
        indicador_domicilio = linea[3:4]  # Reservado para uso futuro
        dom_tipo_via = self.validar_diccionario(
            self.nombre, linea[4:6], "dom_tipo_via", fila, 4, diccionarios.TIPO_VIA
        )
        dom_nombre_via = linea[6:42]
        dom_numero = linea[42:47]  # Solo números
        dom_bis = linea[47:49]
        dom_bloque = linea[49:51]
        dom_escalera = linea[51:53]
        dom_piso = linea[53:55]
        dom_puerta = linea[55:58]
        telefono = linea[58:68]  # 10 dígitos, padding de ceros a la izquierda
        reservado = linea[68:70]

        return {
            "cabecera": cabecera,
            "indicador_domicilio": indicador_domicilio,
            "dom_tipo_via": dom_tipo_via,
            "dom_nombre_via": dom_nombre_via,
            "dom_numero": dom_numero,
            "dom_bis": dom_bis,
            "dom_bloque": dom_bloque,
            "dom_escalera": dom_escalera,
            "dom_piso": dom_piso,
            "dom_puerta": dom_puerta,
            "telefono": telefono,
            "reservado": reservado,
        }

    def parse_linea_ldd(self, fila, linea):
        """
        Parsea la linea de Localidad Domicilio Decodificado

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre LDD
        codigo_postal = linea[3:8]
        localidad = linea[8:48]
        provincia = linea[
            48:50
        ]  # Lista de provincias https://www.seg-social.es/wps/wcm/connect/wss/99d52a02-2968-4f38-b594-290ce13c29fb/T62-Provincia.pdf?MOD=AJPERES
        telefono_sms = linea[50:62]  # Solo para acciones MA o MB, left padding ceros
        prefijo_pais = linea[62:65]  # Solo para acciones MA o MB
        reservado = linea[
            65:70
        ]  # https://es.wikipedia.org/wiki/Anexo:Prefijos_telefónicos_mundiales

        return {
            "cabecera": cabecera,
            "codigo_postal": codigo_postal,
            "localidad": localidad,
            "provincia": provincia,
            "telefono_sms": telefono_sms,
            "prefijo_pais": prefijo_pais,
            "reservado": reservado,
        }

    def parse_linea_fab(self, fila, linea):
        """
        Parsea la linea de Fecha Alta Baja

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        return {
            "cabecera": linea[0:3],  # Siempre FAB
            "accion": linea[
                3:6
            ],  # Lista de acciones https://www.seg-social.es/wps/wcm/connect/wss/dad0574d-411d-4d69-b78f-9d7947ceabab/T07-Acci%C3%B3n+2024-02.pdf?MOD=AJPERES
            "situacion": linea[
                6:8
            ],  # Lista de situaciones https://www.seg-social.es/wps/wcm/connect/wss/ac6c2087-f6d7-4f62-8f85-64c574a6698c/T21-Situaci%C3%B3n+2023-11.pdf?MOD=AJPERES
            "fecha_real": linea[8:16],
            "grupo_cotizacion": linea[
                16:18
            ],  # Lista de grupos de cotizacion https://www.seg-social.es/wps/wcm/connect/wss/d9ea5c7f-8bf6-41a7-91b6-daabaf67d371/T18-Grupo+de+cotizaci%C3%B3n.pdf?MOD=AJPERES
            "grupo_cotizacion_diario": linea[18:19],  # Booleano S/N
            "grado_discapacidad": linea[19:21],
            "tipo_contrato": linea[
                21:24
            ],  # Lista de contratos https://www.seg-social.es/wps/wcm/connect/wss/53104a0c-a484-4728-948f-7355385cf99d/T19-Clave+de+Contrato+de+trabajo+2023-01.pdf?MOD=AJPERES
            "condicion_desempleado": linea[
                24:25
            ],  # Lista de condiciones de desempleo https://www.seg-social.es/wps/wcm/connect/wss/ea63cb12-6a21-4d27-9e14-87fa971c938d/T37-Condici%C3%B3n+de+desempleado+2023-08.pdf?MOD=AJPERES
            "mujer_subrepresentada": linea[25:26],  # Booleano S/N
            "coeficiente_tiempo_parcial": linea[26:29],
            "colectivo_trabajador": linea[
                29:32
            ],  # Listado de colectivos de trabajadores https://www.seg-social.es/wps/wcm/connect/wss/81619dd8-3725-4f83-92aa-325b8202fadc/T61-Colectivo+de+trabajador+2022-06.pdf?MOD=AJPERES
            "indicador_impresion": linea[
                32:33
            ],  # Espacio = No Impresión; S = Impresión resolución; C = Impresión resolución + IDC; I=IDC.
            "categoria_profesional": linea[
                33:40
            ],  # Obligatorio para Régimen 0911. Opcional para Régimen Especial de Trabajadores del Mar. No admisible para resto de regímenes.
            "fecha_nacimiento": linea[40:48],
            "sexo": linea[48:49],  # 1 hombre 2 mujer
            "reservado": linea[49:50],
            "cese_actividad": linea[
                50:51
            ],  # 5 = Extranjero obligación retorno país origen; 6 = Cese de actividad.
            "coeficiente_huelga_ere": linea[51:54],
            "mujer_reincorporada": linea[
                54:55
            ],  # S= Mujer reincorporada después de maternidad; 2=Superposición por 2ªreincorporación; 3=5 años de inactividad; 4=Mujer reincorporada después de excedencia.
            "incapacitado_readmitido": linea[
                55:56
            ],  # Lista codigos https://www.seg-social.es/wps/wcm/connect/wss/59269e17-bb97-4c60-8ced-3bb5fa6a1ba6/T101+-+Incapacitado+readmitido+2023-08.pdf?MOD=AJPERES
            "trabajador_autonomo": linea[
                56:57
            ],  # S= Sí; 1= Familiar 2º grado. Bonificación Ley 6/2017.
            "5jr_semana": linea[
                57:58
            ],  # Booleano S/N. El campo “5JR/semana según convenio” deberá cumplimentarse en aquellos casos en los que el convenio colectivo que resulte de aplicación al trabajador, le permita realizar para un mismo empresario, un mínimo de 5 jornadas reales semanales.
            "n_trabajadores_empresa": linea[
                58:59
            ],  # 1= Empresa <50 Trabajadores (Contrato emprendedores); 3=Menos de 10 trabajadores.
            "relacion_laboral_especial": linea[
                59:63
            ],  # Lista relaciones laborales especiales https://www.seg-social.es/wps/wcm/connect/wss/378ec2c8-09d4-43d2-a027-5a31d29b5b2c/T38-Relaci%C3%B3n+Laboral+de+Car%C3%A1cter+Especial+2025-05.pdf?MOD=AJPERES
            "tipo_inactividad": linea[
                63:65
            ],  # Lista tipos de inactividad https://www.seg-social.es/wps/wcm/connect/wss/08f5f0c8-8745-4872-82ff-d123ddef5cc3/T41-Tipos+de+inactividad+2025-05.pdf?MOD=AJPERES
            "responsable_formacion": linea[65:66],  # Booleano S/N
            "exenciones_trabajador": linea[66:67],  # Booleano S/N
            "exclusion_social_victimas": linea[
                67:68
            ],  # Lista codigos https://www.seg-social.es/wps/wcm/connect/wss/f17bc7b7-7d13-40e8-9d89-b17d8f1776b9/T83-Exclusi%C3%B3n+social-V%C3%ADctimas+2024-11.pdf?MOD=AJPERES
            "renta_activa_insercion": linea[68:69],  # Booleano S/N
            "trabajadoras_24m_alumbramiento": linea[69:70],  # Booleano S/N
        }

    def parse_linea_dam(self, fila, linea):
        """
        Parsea la linea de Datos Asociados al Movimiento

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        return {
            "cabecera": linea[0:3],  # Siempre DAM
            "fecha_inicio_contrato": linea[3:11],
            "fic_especifico": linea[
                11:12
            ],  # Obigatorio si fecha_inicio_contrato contiene algo, booleano S/N
            "nuss_trabajador_sustituido": linea[12:24],
            "causa_sustitucion": linea[
                24:26
            ],  # Obigatorio si nuss_trabajador_sustituido contiene algo (solo para sistema especial 32), lista causas https://www.seg-social.es/wps/wcm/connect/wss/333d95d6-b3a4-4b6c-89ac-cd888ac68c79/T39-Causa+de+sustituci%C3%B3n+2025-05.pdf?MOD=AJPERES
            "permanencia_parte_entera": linea[26:27],  # De existir debe ser 1
            "permamencia_parte_decimal": linea[27:29],  # De existir debe ser 33 o 61
            "coeficiente_reductor_jubilacion": linea[
                29:31
            ],  # Solo para altas en regimenes 0111, 0811 y 0911
            "relevo": linea[31:32],
            "dias_trabajados": linea[32:34],
            "sistema_especial": linea[
                34:36
            ],  # Desuso, tabla https://www.seg-social.es/wps/wcm/connect/wss/ffbab7de-37e1-4863-9c22-41ef50fc0bfb/T91-Sistema+Especial.pdf?MOD=AJPERES
            "exclusion_cotizacion": linea[
                36:39
            ],  # Lista codigos https://www.seg-social.es/wps/wcm/connect/wss/23627250-475b-4516-811f-2781422efcdb/T52-Tipo+de+Relaci%C3%B3n+Laboral+2022-09.pdf?MOD=AJPERES
            "cambio_puesto_trabajo": linea[
                39:41
            ],  # Lista codigos https://www.seg-social.es/wps/wcm/connect/wss/0be0df0d-3b4b-41e2-b14b-d0e1a1929ff8/T73-Cambio+de+puesto+de+trabajo.pdf?MOD=AJPERES
            "indicativo_perdida_beneficios": linea[
                41:43
            ],  # Para acción MC se admitirán todos los valores. Para acción MA solo los valores: 01=falta de concurrencia de requisitos; 08=extinción contrato bonificado últimos 12 meses y 99=no aplicación peculiaridades vigentes.
            "vinculo_familiar": linea[
                43:44
            ],  # Uso futuro, lista https://www.seg-social.es/wps/wcm/connect/wss/8225d8d4-e6fa-42bf-97a7-1d1efecd0380/T97-V%C3%ADnculo+familiar+2023-08.pdf?MOD=AJPERES
            "nss_persona_fisica_vinculada": linea[44:56],
            "programa_formento_empleo_agrario": linea[
                56:57
            ],  # Valores: 0=No; 1=Sí; 2=Sí, con exclusión de cotización adicional contratos inferiores a 30 días
            "modalidad_cotizacion": linea[
                57:58
            ],  # Obligatorio para altas de Régimen 0613. No admisible para otros regímenes. Valores: 0=sin modalidad de cotización; 1=cotización mensual; 2=cotización por jornadas reales.
            "beneficios": linea[
                58:60
            ],  # Valor: 01=Beneficiario Sistema Nacional de Garantía Juvenil – solicitado. 11 = Beneficiario Sistema Nacional de Garantía Juvenil – acreditado.16 - Benef. SNGJ-Baja cualificación; 17 - Ceuta y Melilla; 18 - Formación práctica Coop.-Soc. Laboral. 19=Ct formación Art.23 RDL 1/2023; 20=Transf. Ct fijo disc. SEA Art. 29 RDL 1/2023; 21= Incorporación socios coop/soc lab. Art 28 RDL 1/2023
            "ocupacion": linea[
                60:62
            ],  # Lista https://www.seg-social.es/wps/wcm/connect/wss/7738be41-3c14-4a2e-8a0a-b55ddbc8ded6/T58-Ocupaci%C3%B3n.pdf?MOD=AJPERES
            "excedente_sector_industrial": linea[
                62:64
            ],  # 1=Textil. Confección; 2=Calzado. Curtidos. Marroquinería.
            "reduccion_jornada": linea[64:67],
            "coeficiente_tiempo_parcial_inicial": linea[67:70],
        }

    def parse_linea_odl(self, fila, linea):
        """
        Parsea la linea de Otros Datos Laborales

        Args:
            fila (int): Número de línea actual.
            linea (str): Contenido de la línea.

        Returns:
            Diccionario con el contenido de la línea separado por secciones.
        """
        cabecera = linea[0:3]  # Siempre ODL
        convenio_colectivo = self.validar_numeros(
            self.nombre, linea[3:17], "convenio_colectivo", fila, 3
        )  # txt de los codigos de convenios colectivos a 2016/03 https://www.seg-social.es/descarga/es/214684
        reservado_1 = linea[17:23]
        ocupacion_cno = self.validar_numeros(
            self.nombre, linea[23:27], "ocupacion_cno", fila, 23
        )  # Lista codigos https://www.seg-social.es/wps/wcm/connect/wss/43c07033-9bc6-43e0-acca-fea462663adf/T90-TABLA+DE+OCUPACI%C3%93N+C.N.O.+2022-12.pdf?MOD=AJPERES
        reservado_2 = self.validar_numeros(
            self.nombre, linea[27:33], "reservado_2", fila, 27
        )
        importe_contribucion_entero = self.validar_numeros(
            self.nombre, linea[33:37], "importe_contribucion_entero", fila, 33
        )
        importe_contribucion_decimal = self.validar_numeros(
            self.nombre, linea[37:39], "importe_contribucion_decimal", fila, 37
        )
        entidad_plan_pensiones = linea[
            39:44
        ]  # Obligatorio para SAA 439 para acción ASA; opcional para acción MSA; no admisible para ESA. Ver tabla https://www.seg-social.es/wps/wcm/connect/wss/d2256385-d5fe-40b1-ad5a-58b1bedb51af/T100+-+Entidad+gestora+del+Plan+de+pensiones+2025-06.pdf?MOD=AJPERES
        pais = self.validar_numeros(
            self.nombre, linea[44:47], "importe_contribucion_decimal", fila, 44
        )  # Obligatorio para SAA 150, 151, 152, 153 y 154 para acciones ASA y MSA; no admisible para ESA. Ver tabla https://www.seg-social.es/wps/wcm/connect/wss/b2a14538-73e9-4e9b-ae81-82e50ec0090b/T12-Nacionalidad+Pais+2021-09.pdf?MOD=AJPERES
        region_especial_pais = linea[47:50]  # En desuso
        fin_previsto_contrato = self.validar_numeros(
            self.nombre, linea[50:58], "importe_contribucion_decimal", fila, 50
        )  # En desuso
        reservado_3 = linea[58:70]  # En desuso

        return {
            "cabecera": cabecera,
            "convenio_colectivo": convenio_colectivo,
            "reservado_1": reservado_1,
            "ocupacion_cno": ocupacion_cno,
            "reservado_2": reservado_2,
            "importe_contribucion_entero": importe_contribucion_entero,
            "importe_contribucion_decimal": importe_contribucion_decimal,
            "entidad_plan_pensiones": entidad_plan_pensiones,
            "pais": pais,
            "region_especial_pais": region_especial_pais,
            "fin_previsto_contrato": fin_previsto_contrato,
            "reservado_3": reservado_3,
        }
