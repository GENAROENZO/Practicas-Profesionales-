import xml.etree.ElementTree as ET
import os
import zipfile
from io import BytesIO
import re

def modify_kml_placemarks(input_path, output_kml_path, target_simple_data_name='nombre'):
    """
    Lee un archivo KML o KMZ, establece el nombre de cada Placemark
    basándose en el valor de un SimpleData específico (por defecto 'nombre'),
    y ordena los Placemarks alfabéticamente.

    Args:
        input_path (str): Ruta al archivo KML o KMZ de entrada.
        output_kml_path (str): Ruta donde se guardará el KML modificado.
        target_simple_data_name (str): Nombre del campo SimpleData que contiene
                                       el nombre que se usará para el Placemark.
    """
    try:
        print(f"Directorio de trabajo actual: {os.getcwd()}")
        
        # VERIFICACIÓN DE EXISTENCIA
        if not os.path.exists(input_path):
            print(f"Error: El archivo de entrada '{input_path}' no fue encontrado.")
            print("Asegúrate de que el archivo KMZ/KML esté en la ruta especificada.")
            return

        # 1. Manejar KMZ (Zip) o KML (XML directo)
        root = None
        if input_path.lower().endswith('.kmz'):
            print(f"Detectado archivo KMZ. Extrayendo doc.kml...")
            try:
                with zipfile.ZipFile(input_path, 'r') as kmz:
                    # Lee el KML principal (doc.kml) en memoria
                    with kmz.open('doc.kml') as kml_file:
                        kml_data = kml_file.read()
                root = ET.fromstring(kml_data)
            except (zipfile.BadZipFile, KeyError, FileNotFoundError) as e:
                print(f"Error al procesar KMZ: {e}")
                return
        elif input_path.lower().endswith('.kml'):
            print(f"Detectado archivo KML. Parseando...")
            tree = ET.parse(input_path)
            root = tree.getroot()
        else:
            print(f"Error: El archivo de entrada '{input_path}' no es ni .kmz ni .kml.")
            return

        # Registrar los namespaces KML
        ET.register_namespace('', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('gx', "http://www.google.com/kml/ext/2.2")
        ET.register_namespace('kml', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('atom', "http://www.w3.org/2005/Atom")

        # Namespace KML para búsquedas
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # --- Extracción de Placemarks ---
        # Encontrar todos los Placemarks en el documento
        placemarks = root.findall('.//kml:Placemark', ns)

        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en el archivo KML dentro de '{input_path}'.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Procesando y renombrando...")

        # Lista para almacenar tuplas (nombre_para_ordenar, Placemark)
        sorted_placemarks = []

        for placemark in placemarks:
            # 2. Buscar el valor del SimpleData por su nombre ('nombre' por defecto)
            target_element = placemark.find(f".//kml:SimpleData[@name='{target_simple_data_name}']", ns)
            
            new_name = "Sin Nombre"
            if target_element is not None and target_element.text:
                new_name = target_element.text.strip()
            
            # 3. Establecer el nuevo nombre del Placemark
            name_element = placemark.find('kml:name', ns)
            if name_element is None:
                name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
                placemark.insert(0, name_element)
            name_element.text = new_name

            # 4. Almacenar para el ordenamiento alfabético
            sorted_placemarks.append((new_name.lower(), placemark))

        # 5. Ordenar los Placemarks alfabéticamente por el nombre extraído
        sorted_placemarks.sort(key=lambda x: x[0])

        # --- Reorganización de la jerarquía KML ---
        
        # Encontrar el contenedor principal (Document o Folder que contenga todos los placemarks originales)
        document_container = root.find('kml:Document', ns)
        if document_container is None:
            document_container = root
        
        # Si el root no es el Documento, lo buscamos
        if document_container.tag != '{http://www.opengis.net/kml/2.2}Document':
             document_container = root.find('.//kml:Document', ns)

        if document_container is None:
            print("Advertencia: No se encontró un contenedor Document. Usando Root.")
            document_container = root

        # Eliminar todos los Placemarks antiguos del contenedor original
        for elem in list(document_container):
            if elem.tag.endswith('Placemark') or elem.tag.endswith('Folder'):
                document_container.remove(elem)
        
        # Reinsertar los Placemarks ordenados en el contenedor
        for _, placemark in sorted_placemarks:
            document_container.append(placemark)
        
        # 6. Guardar el archivo KML modificado
        tree = ET.ElementTree(root)
            
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n¡Éxito! Archivo KML renombrado y ordenado guardado en: {output_kml_path}")
        print(f"Se utilizó el campo '{target_simple_data_name}' para el nombre visible.")

    except zipfile.BadZipFile:
        print(f"Error: El archivo '{input_path}' no es un archivo KMZ válido o está corrupto.")
    except KeyError:
        print(f"Error: El archivo KMZ no contiene el KML principal esperado ('doc.kml').")
    except ET.ParseError as e:
        print(f"Error al parsear el archivo KML: {e}. Asegúrate de que el KML está bien formado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# ¡IMPORTANTE! 
# 1. Reemplaza 'CuerposDeAgua.kmz' por el nombre EXACTO de tu archivo KMZ.
# 2. Si el campo que contiene el nombre del cuerpo de agua no se llama 'nombre',
#    reemplaza 'nombre' en target_simple_data_name por el nombre correcto del campo.
input_kml_file = '1-Archivos Practicas Profecionales/2-Cambios de Capas/6-Cuerpos de Agua/Cuerpos-Agua.kmz'
output_kml_file = '1-Archivos Practicas Profecionales/2-Cambios de Capas/6-Cuerpos de Agua/CuerposdeAgua-Editado.kml'
target_simple_data_name = 'nombre' # <--- CAMPO A USAR COMO NOMBRE

# --- Ejecutar la función ---
if __name__ == "__main__":
    modify_kml_placemarks(input_kml_file, output_kml_file, target_simple_data_name)