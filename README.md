# Este proyecto está en porgreso (WIP), aún queda añadir cosas para que tenga una funcionalidad completa

# Librería AFI - Validación y Segmentación para Seguridad Social Española

Este repositorio contiene una librería en Python diseñada para validar y segmentar archivos AFI de la Seguridad Social española.

## ¿Qué es un AFI?

Un AFI es un fichero estándar utilizado por la Seguridad Social española que contiene información sobre la afiliación de trabajadores y empresas para la gestión y control de la afiliación en el mismo.

## Funcionalidades

- Segmentación y parseo de líneas de fichero AFI según los distintos tipos de registros (razón social, trabajador, domicilio, peculiaridades, etc.).
- Gestión de errores y validaciones específicas para asegurar la integridad de los datos.
- Validación de diferentes tipos de documentos oficiales (DNI, NIE, CIF, pasaportes).

## Uso y pruebas

Para crear un entorno virtual y preparar la librería, ejecuta los siguientes comandos:

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# o
venv\Scripts\activate     # En Windows PowerShell

pip install -r requirements.txt
```

## Recursos

Se usa la librería python-stdnum para validar ciertos números
- https://github.com/arthurdejong/python-stdnum