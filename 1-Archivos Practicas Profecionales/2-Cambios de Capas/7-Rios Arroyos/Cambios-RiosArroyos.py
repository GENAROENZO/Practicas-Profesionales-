import xml.etree.ElementTree as ET
import os
import zipfile
from io import BytesIO
import re
from collections import defaultdict

def organize_kml_by_attribute(input_path, output_kml_path, name_attribute='nombre', group_attribute='tipo'):
    """
    Lee un archivo KML o KMZ, renombra los Placemarks usando el valor del
    campo 'name_attribute' y los organiza en carpetas jerárquicas usando
    el valor del campo 'group_attribute'.
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
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # --- Extracción y Agrupación de Placemarks ---
        placemarks = root.findall('.//kml:Placemark', ns)
        
        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en el archivo KML.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Agrupando por '{group_attribute}'...")

        # Diccionario para agrupar placemarks: {Tipo: [(nombre_ordenado, placemark), ...]}
        grouped_data = defaultdict(list)

        for placemark in placemarks:
            # 2. Obtener el valor para la AGRUPACIÓN (e.g., 'ARROYO', 'RIO')
            group_element = placemark.find(f".//kml:SimpleData[@name='{group_attribute}']", ns)
            group_value = group_element.text.strip() if group_element is not None and group_element.text else "SIN TIPO"

            # 3. Obtener el valor para el NOMBRE (e.g., 'COEHUE CO')
            name_element_data = placemark.find(f".//kml:SimpleData[@name='{name_attribute}']", ns)
            new_name = name_element_data.text.strip() if name_element_data is not None and name_element_data.text else "Sin Nombre"

            # 4. Establecer el nuevo nombre del Placemark
            name_element = placemark.find('kml:name', ns)
            if name_element is None:
                name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
                # Insertar el nombre al principio del Placemark
                placemark.insert(0, name_element) 
            name_element.text = new_name

            # 5. Almacenar para el ordenamiento
            grouped_data[group_value].append((new_name.lower(), placemark))

        # --- Reorganización de la jerarquía KML ---
        
        # Encontrar el contenedor principal (Document)
        document_container = root.find('kml:Document', ns)
        
        if document_container is None:
            # Si el KML no usa <Document>, usamos el Root (menos común pero posible)
            print("Advertencia: No se encontró un contenedor Document. Usando Root.")
            document_container = root.find(f'.//kml:Folder', ns) or root

        # Eliminar todos los Placemarks y Folders antiguos del contenedor original
        for elem in list(document_container):
            if elem.tag.endswith('Placemark') or elem.tag.endswith('Folder'):
                document_container.remove(elem)
        
        # 6. Crear y reinsertar las nuevas carpetas ordenadas
        
        # Ordenar las carpetas por nombre (A-Z: ARROYO antes que RIO)
        sorted_group_keys = sorted(grouped_data.keys())

        for group_name in sorted_group_keys:
            # Crear la Carpeta (Folder) para el Tipo (e.g., ARROYO)
            folder = ET.Element('{http://www.opengis.net/kml/2.2}Folder')
            name = ET.Element('{http://www.opengis.net/kml/2.2}name')
            name.text = group_name
            folder.append(name)

            # Ordenar los placemarks dentro de la carpeta por nombre
            sorted_items = sorted(grouped_data[group_name], key=lambda x: x[0])
            
            # Agregar los Placemarks ordenados a la nueva Carpeta
            for _, placemark in sorted_items:
                folder.append(placemark)

            # Agregar la nueva Carpeta al Documento
            document_container.append(folder)
        
        # 7. Guardar el archivo KML modificado
        tree = ET.ElementTree(root)
            
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n¡Éxito! Archivo KML organizado y renombrado guardado en: {output_kml_path}")
        print(f"Organizado en carpetas por campo: '{group_attribute}'. Renombrado por campo: '{name_attribute}'.")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# 1. Reemplaza 'Rios-Arroyos.kmz' por el nombre EXACTO de tu archivo KMZ.
input_kml_file = '1-Archivos Practicas Profecionales/2-Cambios de Capas/7-Rios Arroyos/Rios-Arroyos.kmz'

# 2. El nombre de salida
output_kml_file = '1-Archivos Practicas Profecionales/2-Cambios de Capas/7-Rios Arroyos/Rios-Arroyos-Editado.kml'

# 3. Campo que se usa para nombrar cada elemento (según tu KML, es 'nombre')
name_attribute_key = 'nombre' 

# 4. Campo que se usa para crear las carpetas (según tu KML, es 'tipo')
group_attribute_key = 'tipo'

# --- Ejecutar la función ---
if __name__ == "__main__":
    organize_kml_by_attribute(input_kml_file, output_kml_file, name_attribute_key, group_attribute_key)