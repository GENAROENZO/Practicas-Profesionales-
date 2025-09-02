import xml.etree.ElementTree as ET
import os
import re # Importamos el módulo 're' para expresiones regulares

def modify_kml_placemarks(input_kml_path, output_kml_path):
    """
    Modifica un archivo KML para establecer el nombre de cada Placemark (polígono)
    basándose en el valor completo de 'ccpp1' y los ordena numéricamente
    por el primer número de ccpp1 y luego por el segundo.
    Preserva todas las SimpleData existentes para su uso como atributos GIS.

    Args:
        input_kml_path (str): Ruta al archivo KML de entrada.
        output_kml_path (str): Ruta donde se guardará el archivo KML modificado.
    """
    try:
        # --- LÍNEAS DE DEPURACIÓN (Mantener para verificar ruta y archivos) ---
        current_working_directory = os.getcwd()
        print(f"Directorio de trabajo actual: {current_working_directory}")

        files_in_directory = os.listdir(current_working_directory)
        print(f"Archivos encontrados en el directorio: {files_in_directory}")

        if input_kml_path in files_in_directory:
            print(f"¡Confirmado! '{input_kml_path}' se encuentra en el directorio.")
        else:
            print(f"Advertencia: '{input_kml_path}' NO se encontró en la lista de archivos del directorio.")
            print("Por favor, verifica el nombre exacto del archivo y la ubicación.")
        # --- FIN DE LÍNEAS DE DEPURACIÓN ---

        # Registrar los namespaces KML
        ET.register_namespace('', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('gx', "http://www.google.com/kml/ext/2.2")
        ET.register_namespace('kml', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('atom', "http://www.w3.org/2005/Atom")

        # Parsear el archivo KML
        tree = ET.parse(input_kml_path)
        root = tree.getroot()

        # Namespace KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Encontrar la carpeta que contiene los Placemarks
        folder = root.find('.//kml:Folder', ns)
        if folder is None:
            print("Error: No se encontró la etiqueta <Folder> que contiene los Placemarks.")
            print("Asegúrate de que tus Placemarks estén dentro de una carpeta en el KML.")
            return

        placemarks_to_sort = []
        placemarks = folder.findall('kml:Placemark', ns)

        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en '{input_kml_path}'.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Procesando y ordenando...")

        # Expresión regular para encontrar los dos números en "XXXX YYYY"
        # Captura el primer número en grupo 1 y el segundo en grupo 2
        ccpp1_numbers_regex = re.compile(r'(\d+)\s+(\d+)')

        for placemark in placemarks:
            sort_key_value = None
            extracted_name = None

            # Buscar el elemento <SimpleData name="ccpp1">
            ccpp1_element = placemark.find(".//kml:SimpleData[@name='ccpp1']", ns)

            if ccpp1_element is not None and ccpp1_element.text:
                ccpp1_text = ccpp1_element.text.strip()
                match = ccpp1_numbers_regex.search(ccpp1_text)

                if match:
                    first_num_str = match.group(1)
                    second_num_str = match.group(2)
                    extracted_name = f"{first_num_str} {second_num_str}" # El nombre será el valor completo de ccpp1
                    try:
                        # La clave de ordenamiento es una tupla (primer_numero_int, segundo_numero_int)
                        sort_key_value = (int(first_num_str), int(second_num_str))
                    except ValueError:
                        # Si la conversión falla, se usará el texto completo para ordenar
                        sort_key_value = ccpp1_text
                        print(f"Advertencia: El código '{ccpp1_text}' de ccpp1 no es completamente numérico. Se ordenará como texto.")
                else:
                    # Si el texto de ccpp1 no coincide con el patrón "XXXX YYYY"
                    extracted_name = ccpp1_text
                    sort_key_value = ccpp1_text
                    print(f"Advertencia: El texto '{ccpp1_text}' de ccpp1 no coincide con el patrón esperado (XXXX YYYY). Se usará el texto completo para ordenar/nombrar.")
            else:
                # Si no se encuentra ccpp1, usar el id del Placemark
                extracted_name = placemark.attrib.get('id', 'Sin Nombre')
                sort_key_value = extracted_name
                print(f"Advertencia: No se encontró <SimpleData name='ccpp1'> para Placemark con ID: {extracted_name}. Se usará el ID para ordenar/nombrar.")

            # Actualizar/Crear la etiqueta <name> con el valor extraído
            name_element = placemark.find('kml:name', ns)
            if name_element is not None:
                name_element.text = extracted_name
            else:
                new_name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
                new_name_element.text = extracted_name
                placemark.insert(0, new_name_element) # Insertar al principio del Placemark

            placemarks_to_sort.append((sort_key_value, placemark))

        # Función de clave de ordenamiento personalizada para manejar tipos mixtos (tuplas y strings)
        def sort_key_func(item):
            key_value = item[0]
            if isinstance(key_value, tuple):
                # Si es una tupla de números (ordenamiento principal y secundario)
                return (0, key_value[0], key_value[1]) # Prioridad 0, luego primer num, luego segundo num
            else:
                # Si es un string (fallback), se ordena alfabéticamente después de los números
                return (1, str(key_value)) # Prioridad 1, luego la cadena

        placemarks_to_sort.sort(key=sort_key_func)

        # Eliminar y re-añadir los Placemarks en el orden correcto
        for placemark in placemarks:
            folder.remove(placemark)
        for _, sorted_placemark in placemarks_to_sort:
            folder.append(sorted_placemark)

        # Guardar el archivo KML modificado
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n¡Éxito! Archivo KML ordenado y nombrado guardado en: {output_kml_path}")

    except FileNotFoundError:
        print(f"Error: El archivo '{input_kml_path}' no fue encontrado.")
        print("Asegúrate de que el archivo KML esté en el mismo directorio que el script.")
    except ET.ParseError as e:
        print(f"Error al parsear el archivo KML: {e}. Asegúrate de que es un XML válido.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# ¡IMPORTANTE! Cambia 'doc.kml' por el nombre exacto de tu archivo KML de entrada
# si no se llama 'doc.kml'.
# y 'padriones_ordenados_con_atributos.kml' por el nombre que quieres para el archivo de salida.
input_kml_file = 'doc.kml' # Nombre por defecto para KML descomprimido
output_kml_file = 'padriones_ordenados_con_atributos.kml'

# --- Ejecutar la función ---
if __name__ == "__main__":
    if os.path.exists(input_kml_file):
        modify_kml_placemarks(input_kml_file, output_kml_file)
    else:
        print(f"Error: El archivo de entrada '{input_kml_file}' no existe en la misma carpeta que el script.")
        print("Asegúrate de que el archivo KML esté en el mismo directorio.")
