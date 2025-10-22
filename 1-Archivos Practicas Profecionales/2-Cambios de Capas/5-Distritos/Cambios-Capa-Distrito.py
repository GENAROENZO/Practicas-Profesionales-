import xml.etree.ElementTree as ET
import os
import zipfile
from io import BytesIO

def organize_kml_by_department(input_path, output_kml_path):
    """
    Lee un archivo KML o KMZ de distritos, renombra los Placemarks con el nombre del distrito,
    y los reorganiza en carpetas (Folders) jerárquicas basadas en el campo 'departamento'.

    Args:
        input_path (str): Ruta al archivo KML o KMZ de entrada.
        output_kml_path (str): Ruta donde se guardará el archivo KML modificado.
    """
    try:
        print(f"Directorio de trabajo actual: {os.getcwd()}")
        
        # VERIFICACIÓN DE EXISTENCIA
        if not os.path.exists(input_path):
            print(f"Error: El archivo de entrada '{input_path}' no fue encontrado.")
            print("Asegúrate de que el archivo KMZ/KML esté en la ruta especificada.")
            return
        
        # 1. Manejar KMZ (Zip) o KML (XML directo)
        kml_data = None
        if input_path.lower().endswith('.kmz'):
            print(f"Detectado archivo KMZ. Extrayendo doc.kml...")
            try:
                with zipfile.ZipFile(input_path, 'r') as kmz:
                    # El archivo KML principal en un KMZ casi siempre se llama doc.kml
                    with kmz.open('doc.kml') as kml_file:
                        kml_data = kml_file.read()
                # Parsear directamente desde los bytes en memoria
                root = ET.fromstring(kml_data)
            except zipfile.BadZipFile:
                print(f"Error: El archivo '{input_path}' no es un archivo KMZ válido o está corrupto.")
                return
            except KeyError:
                print(f"Error: El archivo KMZ no contiene el KML principal esperado ('doc.kml').")
                print("Si tu archivo KMZ contiene el KML principal con otro nombre, debes cambiar 'doc.kml' en el código.")
                return
        elif input_path.lower().endswith('.kml'):
            print(f"Detectado archivo KML. Parseando...")
            # Parsear el archivo KML directamente
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

        # Namespace KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # --- IDENTIFICACIÓN DEL CONTENEDOR PRINCIPAL ---
        # El contenedor principal para los nuevos Folders (Departamentos) debe ser el <Document>.
        # Si el root es <kml>, el <Document> es su hijo.
        # Si el root es <Document>, es el contenedor.
        document_container = root.find('kml:Document', ns)
        if document_container is None:
            document_container = root
        
        # Buscamos <Document> en cualquier parte si aún no lo encontramos, o si el root es un Documento
        if document_container.tag != '{http://www.opengis.net/kml/2.2}Document':
             document_container = root.find('.//kml:Document', ns)
        
        if document_container is None:
            print("Error: No se encontró la etiqueta <Document> o <kml> principal en el KML.")
            return

        # Encontrar todos los Placemarks para procesamiento, buscando desde la raíz (root)
        placemarks = root.findall('.//kml:Placemark', ns)

        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en el archivo KML dentro de '{input_path}'.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Procesando y reorganizando...")

        # Diccionario para agrupar Placemarks por Departamento
        # Key: Nombre del Departamento, Value: Lista de tuplas (Nombre Distrito, Placemark)
        departments = {}

        for placemark in placemarks:
            # 1. Extraer datos necesarios
            dept_element = placemark.find(".//kml:SimpleData[@name='departamento']", ns)
            distrito_element = placemark.find(".//kml:SimpleData[@name='distrito']", ns)

            department_name = dept_element.text.strip().upper() if dept_element is not None and dept_element.text else "DEPARTAMENTO DESCONOCIDO"
            distrito_name = distrito_element.text.strip() if distrito_element is not None and distrito_element.text else "Distrito Sin Nombre"

            # 2. Establecer el nombre del Placemark al nombre del Distrito
            name_element = placemark.find('kml:name', ns)
            if name_element is None:
                name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
                placemark.insert(0, name_element)
            name_element.text = distrito_name

            # 3. Agrupar el placemark
            if department_name not in departments:
                departments[department_name] = []
            departments[department_name].append((distrito_name, placemark))

        # --- Reorganización de la jerarquía KML ---

        # 4. Eliminar todos los Placemarks y Folders antiguos del contenedor Document/Root
        # Esto asegura que el Placemark original solo exista una vez en el nuevo Folder.
        for elem in list(document_container):
            if elem.tag.endswith('Placemark') or elem.tag.endswith('Folder'):
                document_container.remove(elem)

        print(f"Creando {len(departments)} carpetas de Departamento...")

        # 5. Iterar sobre los departamentos (ordenados alfabéticamente)
        sorted_department_names = sorted(departments.keys())

        for dept_name in sorted_department_names:
            # a. Crear nueva Carpeta (Folder) para el Departamento
            dept_folder = ET.Element('{http://www.opengis.net/kml/2.2}Folder')

            # b. Asignar el nombre del Departamento
            dept_name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
            dept_name_element.text = dept_name.title() # Usar Title case para nombres de carpeta
            dept_folder.append(dept_name_element)

            # c. Ordenar los distritos dentro de la carpeta (alfabéticamente por nombre de distrito)
            # La clave de ordenamiento es el nombre del distrito (primer elemento de la tupla)
            sorted_distritos = sorted(departments[dept_name], key=lambda x: x[0])

            # d. Añadir los Placemarks ordenados a la nueva Carpeta
            for _, placemark in sorted_distritos:
                # Ya eliminamos los placemarks del contenedor principal en el paso 4,
                # por lo que ahora podemos adjuntarlos al nuevo Folder.
                dept_folder.append(placemark)

            # e. Añadir la Carpeta del Departamento al Documento
            document_container.append(dept_folder)
        
        # 6. Guardar el archivo KML modificado
        # Necesitamos el elemento raíz original para escribir todo el documento KML.
        tree = ET.ElementTree(root)
            
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n¡Éxito! Archivo KML reorganizado y nombrado guardado en: {output_kml_path}")
        print("Ahora puedes abrir este archivo en Google Earth o tu software GIS. Verás carpetas por Departamento.")

    except zipfile.BadZipFile:
        print(f"Error: El archivo '{input_path}' no es un archivo KMZ válido o está corrupto.")
    except KeyError:
        print(f"Error: El archivo KMZ no contiene el KML principal esperado (doc.kml).")
    except ET.ParseError as e:
        print(f"Error al parsear el archivo KML: {e}. Asegúrate de que el KML está bien formado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# ¡IMPORTANTE! Ajusta estos nombres de archivo si es necesario.
# Basado en tu ruta: 'C:/Users/Usuario/Desktop/Practicas-Profesionales-/1-Archivos Practicas Profecionales/2-Cambios de Capas/5-Distritos/...'
# La ruta relativa es la más segura en tu caso.
input_kml_file = '1-Archivos Practicas Profecionales/2-Cambios de Capas/5-Distritos/Distritos.kmz'
output_kml_file = '1-Archivos Practicas Profecionales/2-Cambios de Capas/5-Distritos/Distritos-Editado.kml'

# --- Ejecutar la función ---
if __name__ == "__main__":
    organize_kml_by_department(input_kml_file, output_kml_file)
