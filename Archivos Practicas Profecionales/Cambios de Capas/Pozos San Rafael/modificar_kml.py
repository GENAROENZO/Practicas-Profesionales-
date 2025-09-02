import xml.etree.ElementTree as ET
import os

def modify_kml_placemarks(input_kml_path, output_kml_path):
    """
    Modifica un archivo KML para establecer el nombre de cada Placemark
    basándose en el valor de 'dp_pozo' en sus SimpleData.

    Args:
        input_kml_path (str): Ruta al archivo KML de entrada.
        output_kml_path (str): Ruta donde se guardará el archivo KML modificado.
    """
    try:
        # Registrar el namespace KML para que ElementTree lo reconozca
        # Esto es crucial para buscar elementos correctamente
        ET.register_namespace('', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('gx', "http://www.google.com/kml/ext/2.2")
        ET.register_namespace('kml', "http://www.opengis.net/kml/2.2")
        ET.register_namespace('atom', "http://www.w3.org/2005/Atom")

        # Parsear el archivo KML
        tree = ET.parse(input_kml_path)
        root = tree.getroot()

        # Namespace KML (necesario para buscar elementos con prefijos)
        # Esto es para que Python sepa a qué namespace pertenecen las etiquetas
        # Si no se usa, ElementTree no encontrará las etiquetas correctamente
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Buscar todos los elementos <Placemark> en el documento
        # Usamos findall con el namespace para asegurar que se encuentren todos los Placemarks
        placemarks = root.findall('.//kml:Placemark', ns)

        if not placemarks:
            print(f"No se encontraron elementos <Placemark> en '{input_kml_path}'.")
            return

        print(f"Se encontraron {len(placemarks)} Placemarks. Procesando...")

        # Iterar sobre cada Placemark
        for placemark in placemarks:
            # Buscar el elemento <ExtendedData> dentro del Placemark
            extended_data = placemark.find('kml:ExtendedData', ns)

            if extended_data is not None:
                # Buscar el elemento <SchemaData> dentro de ExtendedData
                schema_data = extended_data.find('kml:SchemaData', ns)

                if schema_data is not None:
                    # Buscar el <SimpleData name="dp_pozo"> dentro de SchemaData
                    # Usamos un XPath más específico para asegurarnos de encontrar el correcto
                    dp_pozo_element = schema_data.find("kml:SimpleData[@name='dp_pozo']", ns)

                    if dp_pozo_element is not None and dp_pozo_element.text:
                        pozo_number = dp_pozo_element.text.strip() # Obtener el texto y quitar espacios extra

                        # Buscar si ya existe una etiqueta <name>
                        name_element = placemark.find('kml:name', ns)

                        if name_element is not None:
                            # Si la etiqueta <name> ya existe, actualiza su texto
                            name_element.text = pozo_number
                            # print(f"Actualizado nombre de Placemark a: {pozo_number}")
                        else:
                            # Si la etiqueta <name> no existe, crearla e insertarla
                            # La insertamos justo después de la etiqueta id del Placemark
                            # Esto asegura que el nombre aparezca visible en Google Earth
                            new_name_element = ET.Element('{http://www.opengis.net/kml/2.2}name')
                            new_name_element.text = pozo_number
                            # Encontrar la posición correcta para insertar el nombre
                            # Generalmente, va después de styleUrl o al principio
                            # Si hay styleUrl, lo insertamos después. Si no, al principio.
                            # Para tu KML, parece que va después de la etiqueta de apertura del Placemark
                            # y antes de styleUrl o ExtendedData.

                            # Obtener la posición del primer hijo del placemark
                            # Esto lo insertará al principio, que es lo más seguro
                            placemark.insert(0, new_name_element)
                            # print(f"Insertado nuevo nombre de Placemark: {pozo_number}")
                    # else:
                        # print("No se encontró 'dp_pozo' o está vacío para un Placemark.")
            # else:
                # print("No se encontró <ExtendedData> para un Placemark.")

        # Guardar el archivo KML modificado
        # pretty_print=True para que el XML de salida sea legible
        tree.write(output_kml_path, encoding='utf-8', xml_declaration=True) # Se eliminó pretty_print=True
        print(f"\n¡Éxito! Archivo KML modificado guardado en: {output_kml_path}")

    except FileNotFoundError:
        print(f"Error: El archivo '{input_kml_path}' no fue encontrado.")
    except ET.ParseError as e:
        print(f"Error al parsear el archivo KML: {e}. Asegúrate de que es un XML válido.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- Configuración ---
# ¡IMPORTANTE! Cambia 'doc.kml' por el nombre exacto de tu archivo KML de entrada
# y 'pozos_san_rafael_con_nombres.kml' por el nombre que quieres para el archivo de salida.
# Asegúrate de que estos archivos estén en la misma carpeta que el script de Python.
input_kml_file = 'doc.kml'
output_kml_file = 'pozos_san_rafael_con_nombres.kml'

# --- Ejecutar la función ---
if __name__ == "__main__":
    # Verifica si el archivo de entrada existe antes de intentar procesarlo
    if os.path.exists(input_kml_file):
        modify_kml_placemarks(input_kml_file, output_kml_file)
    else:
        print(f"Error: El archivo de entrada '{input_kml_file}' no existe en la misma carpeta que el script.")
        print("Asegúrate de que 'doc.kml' (o el nombre correcto de tu KML) esté en el mismo directorio.")

