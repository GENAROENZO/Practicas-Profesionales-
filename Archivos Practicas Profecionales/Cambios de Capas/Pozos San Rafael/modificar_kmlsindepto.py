import xml.etree.ElementTree as ET
import os

def modify_kml_placemarks(input_kml_path, output_kml_path):
    """
    Modifica un archivo KML para establecer el nombre de cada Placemark
    basándose en el valor de 'dp_pozo' en sus SimpleData y los ordena numéricamente.

    Args:
        input_kml_path (str): Ruta al archivo KML de entrada.
        output_kml_path (str): Ruta donde se guardará el archivo KML modificado.
    """
    try:
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

        # Lista para almacenar los Placemarks y sus números de pozo para ordenar
        placemarks_to_sort = []

        # Buscar todos los elementos <Placemark> en el documento
        # Usamos findall en la carpeta para obtener solo los Placemarks dentro de ella
        placemarks = folder.findall('kml:Placemark', ns)

        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en '{input_kml_path}'.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Procesando y ordenando...")

        # Iterar sobre cada Placemark para extraer el número de pozo y prepararlo para ordenar
        for placemark in placemarks:
            extended_data = placemark.find('kml:ExtendedData', ns)
            pozo_number_for_sort = None # Variable para almacenar el número para ordenar

            if extended_data is not None:
                schema_data = extended_data.find('kml:SchemaData', ns)
                if schema_data is not None:
                    dp_pozo_element = schema_data.find("kml:SimpleData[@name='dp_pozo']", ns)

                    if dp_pozo_element is not None and dp_pozo_element.text:
                        pozo_number_raw = dp_pozo_element.text.strip()

                        # --- MODIFICACIÓN: Eliminar "17 " si el número de pozo comienza con él ---
                        if pozo_number_raw.startswith('17 '):
                            pozo_number_clean = pozo_number_raw[3:] # Elimina los primeros 3 caracteres ("17 ")
                        else:
                            pozo_number_clean = pozo_number_raw
                        # -------------------------------------------------------------------------

                        # Intentar convertir a entero para un ordenamiento numérico
                        try:
                            pozo_number_for_sort = int(pozo_number_clean)
                        except ValueError:
                            # Si no se puede convertir a entero, usar la cadena original para ordenar
                            # Esto es una medida de seguridad si hay números de pozo no numéricos
                            pozo_number_for_sort = pozo_number_clean
                            print(f"Advertencia: El número de pozo '{pozo_number_clean}' no es completamente numérico. Se ordenará como texto.")

                        # Actualizar el nombre del Placemark
                        name_element = placemark.find('kml:name', ns)
                        if name_element is not None:
                            name_element.text = pozo_number_clean
                        else:
                            new_name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
                            new_name_element.text = pozo_number_clean
                            placemark.insert(0, new_name_element)
                    else:
                        # Si no hay dp_pozo, usar un valor por defecto para ordenar o el id
                        pozo_number_for_sort = placemark.attrib.get('id', '0') # Usa el id si no hay dp_pozo
                        # print(f"Advertencia: No se encontró 'dp_pozo' para Placemark con ID: {pozo_number_for_sort}. Se usará el ID para ordenar.")
            
            # Añadir el Placemark y su clave de ordenamiento a la lista
            # Si pozo_number_for_sort es None (no se encontró dp_pozo), se ordenará al final
            placemarks_to_sort.append((pozo_number_for_sort, placemark))

        # Ordenar los Placemarks por el número de pozo
        # Si hay valores None o no numéricos, se ordenarán de forma consistente (Python los maneja)
        placemarks_to_sort.sort(key=lambda x: x[0])

        # Eliminar todos los Placemarks existentes de la carpeta
        for placemark in placemarks:
            folder.remove(placemark)

        # Añadir los Placemarks ordenados de nuevo a la carpeta
        for _, sorted_placemark in placemarks_to_sort:
            folder.append(sorted_placemark)

        # Guardar el archivo KML modificado
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n¡Éxito! Archivo KML modificado y ordenado guardado en: {output_kml_path}")

    except FileNotFoundError:
        print(f"Error: El archivo '{input_kml_path}' no fue encontrado.")
    except ET.ParseError as e:
        print(f"Error al parsear el archivo KML: {e}. Asegúrate de que es un XML válido.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# ¡IMPORTANTE! Cambia 'doc.kml' por el nombre exacto de tu archivo KML de entrada
# y 'pozos_san_rafael_ordenados.kml' por el nombre que quieres para el archivo de salida.
# Asegúrate de que estos archivos estén en la misma carpeta que el script de Python.
input_kml_file = 'doc.kml'
output_kml_file = 'pozos_san_rafael_ordenados.kml'

# --- Ejecutar la función ---
if __name__ == "__main__":
    if os.path.exists(input_kml_file):
        modify_kml_placemarks(input_kml_file, output_kml_file)
    else:
        print(f"Error: El archivo de entrada '{input_kml_file}' no existe en la misma carpeta que el script.")
        print("Asegúrate de que 'doc.kml' (o el nombre correcto de tu KML) esté en el mismo directorio.")

