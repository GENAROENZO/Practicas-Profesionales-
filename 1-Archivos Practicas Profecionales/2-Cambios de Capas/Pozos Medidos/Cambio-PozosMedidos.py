import xml.etree.ElementTree as ET
import os
import re # Importamos el módulo 're' para expresiones regulares

def modify_kml_placemarks(input_kml_path, output_kml_path):
    """
    Ordena los Placemarks en un archivo KML numéricamente
    basándose en el número presente en sus nombres (ej. 'P - 1', 'P - 10').
    No modifica el contenido de la etiqueta <name>.

    Args:
        input_kml_path (str): Ruta al archivo KML de entrada.
        output_kml_path (str): Ruta donde se guardará el archivo KML modificado.
    """
    try:
        # --- INICIO DE LÍNEAS DE DEPURACIÓN ---
        current_working_directory = os.getcwd()
        print(f"Directorio de trabajo actual: {current_working_directory}")

        files_in_directory = os.listdir(current_working_directory)
        print(f"Archivos encontrados en el directorio: {files_in_directory}")

        if input_kml_path in files_in_directory:
            print(f"¡Confirmado! '{input_kml_path}' se encuentra en el directorio.")
        else:
            print(f"Advertencia: '{input_kml_path}' NO se encontró en la lista de archivos del directorio.")
            print("Por favor, verifica el nombre exacto del archivo y la ubicación.")
            # Aquí podríamos salir si el archivo no se encuentra para evitar el FileNotFoundError
            # Pero lo dejaremos para que el error original se muestre si es otra causa.
        # --- FIN DE LÍNEAS DE DEPURACIÓN ---

        # Registrar los namespaces KML para que ElementTree los reconozca
        ET.register_namespace('', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('gx', "http://www.google.com/kml/ext/2.2")
        ET.register_namespace('kml', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('atom', "http://www.w3.org/2005/Atom")

        # Parsear el archivo KML
        tree = ET.parse(input_kml_path)
        root = tree.getroot()

        # Namespace KML (necesario para buscar elementos con prefijos)
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Encontrar la carpeta que contiene los Placemarks
        # Asumimos que los Placemarks están dentro de un <Folder>
        folder = root.find('.//kml:Folder', ns)
        if folder is None:
            print("Error: No se encontró la etiqueta <Folder> que contiene los Placemarks.")
            print("Asegúrate de que tus Placemarks estén dentro de una carpeta en el KML.")
            return

        # Lista para almacenar los Placemarks y sus claves de ordenamiento
        placemarks_to_sort = []

        # Buscar todos los elementos <Placemark> en la carpeta
        placemarks = folder.findall('kml:Placemark', ns)

        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en '{input_kml_path}'.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Procesando y ordenando...")

        # Expresión regular para encontrar el número en el nombre del punto (ej. "P - 1" -> 1)
        name_number_regex = re.compile(r'P - (\d+)')

        # Iterar sobre cada Placemark para extraer el número del nombre
        for placemark in placemarks:
            name_element = placemark.find('kml:name', ns)
            sort_key_value = None # Valor a usar para el ordenamiento

            if name_element is not None and name_element.text:
                name_text = name_element.text.strip()
                match = name_number_regex.search(name_text)

                if match:
                    try:
                        # Extraemos y convertimos el número capturado a entero
                        sort_key_value = int(match.group(1))
                    except ValueError:
                        # Si la conversión falla (ej. "P - ABC"), usamos el texto completo para ordenar
                        sort_key_value = name_text
                        print(f"Advertencia: El nombre '{name_text}' no contiene un número válido para ordenar. Se ordenará como texto.")
                else:
                    # Si el nombre no coincide con el patrón "P - X", usamos el texto completo para ordenar
                    sort_key_value = name_text
                    print(f"Advertencia: El nombre '{name_text}' no coincide con el patrón 'P - X'. Se ordenará como texto.")
            else:
                # Si el Placemark no tiene etiqueta <name> o está vacía, usamos su ID para ordenar
                sort_key_value = placemark.attrib.get('id', 'Sin Nombre')
                print(f"Advertencia: Placemark sin etiqueta <name> o vacía. Se usará el ID '{sort_key_value}' para ordenar.")

            # Añadir la clave de ordenamiento y el Placemark a la lista
            placemarks_to_sort.append((sort_key_value, placemark))

        # Función de clave de ordenamiento personalizada para manejar tipos mixtos (int y string)
        # Los valores numéricos se ordenarán numéricamente, los strings alfabéticamente
        def sort_key_func(item):
            key_value = item[0]
            if isinstance(key_value, int):
                return (0, key_value) # Tupla: (prioridad 0 para números, el número en sí)
            else:
                return (1, str(key_value)) # Tupla: (prioridad 1 para strings, la cadena en sí)

        # Ordenar los Placemarks utilizando la clave personalizada
        placemarks_to_sort.sort(key=sort_key_func)

        # Eliminar todos los Placemarks existentes de la carpeta
        for placemark in placemarks:
            folder.remove(placemark)

        # Añadir los Placemarks ordenados de nuevo a la carpeta
        for _, sorted_placemark in placemarks_to_sort:
            folder.append(sorted_placemark)

        # Guardar el archivo KML modificado
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n¡Éxito! Archivo KML ordenado guardado en: {output_kml_path}")

    except FileNotFoundError:
        print(f"Error: El archivo '{input_kml_path}' no fue encontrado.")
    except ET.ParseError as e:
        print(f"Error al parsear el archivo KML: {e}. Asegúrate de que es un XML válido.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# ¡IMPORTANTE! Cambia 'doc.kml' por el nombre exacto de tu archivo KML de entrada
# si no se llama 'doc.kml'.
# y 'monitoreo_aguas_subterranea_ordenado_solo_por_nombre.kml' por el nombre que quieres para el archivo de salida.
# Asegúrate de que estos archivos estén en la misma carpeta que el script de Python.
input_kml_file = 'doc.kml' # Cambiado a 'doc.kml'
output_kml_file = 'monitoreo_aguas_subterranea_ordenado_solo_por_nombre.kml'

# --- Ejecutar la función ---
if __name__ == "__main__":
    if os.path.exists(input_kml_file):
        modify_kml_placemarks(input_kml_file, output_kml_file)
    else:
        print(f"Error: El archivo de entrada '{input_kml_file}' no existe en la misma carpeta que el script.")
        print("Asegúrate de que el archivo KML esté en el mismo directorio.")
