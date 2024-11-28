import logging
import os
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pywinauto import Application, Desktop

# Cargar variables desde .env
load_dotenv()

# Incrementar el tiempo de espera para la evaluación de expresiones en PyDev en segundos
os.environ['PYDEVD_WARN_EVALUATION_TIMEOUT'] = '60'


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Variables de configuración
SAP_GUI_PATH = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\sapshcut.exe"
SAP_SYSTEM = "PRO"
SAP_CLIENT = "100"
SAP_USER = os.getenv("SAP_USER")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
TRANSACTION = "/nZSM181"
VARIANT = "ARG_ARBA_HOY"
EXPORT_PATH = r"C:\ruta\a\archivo.csv"
TABLE_NAME = "MARA"  # Asegúrate de definir esta variable

def iniciar_sap():
    try:
        app = Application(backend="uia").start(
            f'"{SAP_GUI_PATH}" -system={SAP_SYSTEM} -client={SAP_CLIENT} -user={SAP_USER} -pw={SAP_PASSWORD}'
        )
        logging.info("SAP GUI iniciado exitosamente.")
        return app
    except Exception as e:
        logging.error(f"Error al iniciar SAP GUI: {e}")
        raise

def listar_botones(sap_window):
    try:
        botones = sap_window.descendants(control_type="Button")
        logging.info(f"Se encontraron {len(botones)} botones en la ventana.")
        for boton in botones:
            logging.info(f"Botón encontrado: Título='{boton.window_text()}', auto_id='{boton.element_info.id}'")
        return botones
    except Exception as e:
        logging.error(f"Error al listar los botones: {e}")
        raise

def esperar_ventana(titulo_ventana, backend="uia", timeout=180):
    try:
        sap_window = Desktop(backend=backend).window(title=titulo_ventana)
        sap_window.wait("visible", timeout=timeout)
        sap_window.wait("ready", timeout=timeout)
        sap_window.set_focus()
        logging.info(f"Ventana '{titulo_ventana}' encontrada y enfocada.")
        return sap_window
    except Exception as e:
        logging.error(f"No se pudo encontrar la ventana '{titulo_ventana}': {e}")
        raise

def esperar_ventana_ui(titulo_ventana, timeout=60):
    try:
        sap_window = Desktop(backend="uia").window(title=titulo_ventana)
        sap_window.wait("visible", timeout=timeout)
        sap_window.set_focus()
        logging.info(f"Ventana '{titulo_ventana}' encontrada y enfocada.")
        return sap_window
    except Exception as e:
        logging.error(f"No se pudo encontrar la ventana '{titulo_ventana}': {e}")
        raise

def esperar_ventana_win32(titulo_ventana, timeout=60):
    try:
        sap_window = Desktop(backend="win32").window(title=titulo_ventana)
        sap_window.wait("visible", timeout=timeout)
        sap_window.set_focus()
        logging.info(f"Ventana '{titulo_ventana}' encontrada y enfocada.")
        return sap_window
    except Exception as e:
        logging.error(f"No se pudo encontrar la ventana '{titulo_ventana}': {e}")
        raise

def ejecutar_transaccion(sap_window):
    try:
        # Enfocar la ventana de SAP Easy Access
        sap_window.set_focus()
        # Enviar el código de transacción directamente
        transaction_field = sap_window.child_window(auto_id=200, control_type="ComboBox")
        transaction_field.type_keys(f"{TRANSACTION}", pause=0.5)
        sap_window.type_keys(f"{TRANSACTION}{{ENTER}}", pause=0.5)
        logging.info(f"Transacción {TRANSACTION} ejecutada.")
    except Exception as e:
        logging.error(f"Error al ejecutar la transacción: {e}")
        raise

def obtener_todos_inputs(sap_window):
    """
    Obtiene todos los controles de entrada en la ventana proporcionada.

    :param sap_window: Objeto de la ventana donde buscar los inputs.
    :return: Diccionario con listas de controles agrupadas por tipo.
    """
    try:
        # Definir los tipos de controles que representan inputs
        tipos_controls = ["Edit", "ComboBox", "CheckBox", "RadioButton", "Slider", "DateTimePicker"]

        inputs = {}

        for control_type in tipos_controls:
            controles = sap_window.descendants(control_type=control_type)
            inputs[control_type] = controles
            logging.info(f"Se encontraron {len(controles)} controles de tipo '{control_type}'.")

        return inputs
    except Exception as e:
        logging.error(f"Error al obtener los inputs: {e}")
        raise

def inspeccionar_controles(sap_window):
    try:
        sap_window.print_control_identifiers()
    except Exception as e:
        logging.error(f"Error al inspeccionar los controles: {e}")
        raise

def seleccionar_variante(sap_window):
    windows_uia = Desktop(backend="uia").windows()
    windows_win32 = Desktop(backend="win32").windows()
    try:
        # Obtener las fechas de hoy y ayer
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        
        # Formatear las fechas como 'dd.mm.yyyy'
        today_str = today.strftime('%d.%m.%Y')
        yesterday_str = yesterday.strftime('%d.%m.%Y')
        
        sap_window = esperar_ventana("Validación de tiempos SLATAM")
        sap_window.set_focus()
        
        sap_window.type_keys(yesterday_str)
        sap_window.type_keys('{TAB}')
        sap_window.type_keys(today_str)
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('AR')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('VE')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('ACA')
        sap_window.type_keys('{TAB}')
        sap_window.type_keys('VEVA')
        sap_window.type_keys('{TAB}')
        
        botones_previos = listar_botones(sap_window)
        windows_win32_previo = Desktop(backend="win32").windows()
        
        sap_window.type_keys('{F8}', pause=0.5)
        logging.info("Tecla F8 enviada.")
        
        # Esperar al botón "Seleccionar layout..."
        boton_layout = sap_window.child_window(title="Seleccionar layout...", control_type="Button")
        boton_layout.wait("visible", timeout=120)
        boton_layout.click()
        logging.info("Botón 'Seleccionar layout...' clickeado exitosamente.")
        
        sap_window = esperar_ventana_win32("Seleccionar cálculo costes tabla", timeout=180)
        sap_window = esperar_ventana_win32("Seleccionar cálculo costes tabla", timeout=60)
        
        sap_window.type_keys('{ENTER}', pause=0.5)
        sap_window.type_keys('{ENTER}')
        sap_window = esperar_ventana_win32("Save As", timeout=60)
        
        sap_window.type_keys('{ENTER}')
        sap_window.type_keys('{ENTER}')
        
        logging.info("Tecla ENTER enviada después de seleccionar la variante.")
        
        # Esperar un breve momento para que la ventana de variante aparezca
        time.sleep(1)  # Ajusta el tiempo según sea necesario
        
        # Enviar el código de la variante y presionar F8 dos veces para ejecutar
        sap_window.type_keys(f"{VARIANT}{{F8}}{{F8}}", pause=0.5)
        logging.info(f"Variante '{VARIANT}' seleccionada y ejecutada con F8.")
        
        # Obtener y listar todos los inputs después de seleccionar la variante
        inputs = obtener_todos_inputs(sap_window)
        for tipo, controles in inputs.items():
            logging.info(f"\nControl Tipo: {tipo}")
            for control in controles:
                try:
                    titulo = control.window_text()
                    auto_id = control.element_info.id
                    logging.info(f" - {tipo}: Título='{titulo}', auto_id='{auto_id}'")
                except Exception as e:
                    logging.error(f"Error al obtener información del control: {e}")
    
    except Exception as e:
        logging.error(f"Error al seleccionar la variante: {e}")
        raise

def ingresar_tabla(sap_window):
    try:
        time.sleep(2)  # Espera a que la transacción cargue
        table_field = sap_window.child_window(
            auto_id="usr/ctxtGD-TAB", control_type="Edit"
        )
        table_field.type_keys(f"{TABLE_NAME}{{ENTER}}", pause=0.5)
        logging.info(f"Tabla {TABLE_NAME} ingresada.")
    except Exception as e:
        logging.error(f"Error al ingresar la tabla: {e}")
        raise

def exportar_datos(sap_window):
    try:
        # Navegar por el menú para exportar
        sap_window.menu_select("Archivo->Lista->Exportar->Formato Local")
        time.sleep(1)  # Espera a que aparezca la ventana de guardar
        save_as = sap_window.child_window(
            auto_id="usr/ctxtDY_PATH", control_type="Edit"
        )
        save_as.set_text(EXPORT_PATH)
        sap_window.child_window(
            title="Guardar", auto_id="btnG", control_type="Button"
        ).click()
        logging.info(f"Datos exportados a {EXPORT_PATH}.")
    except Exception as e:
        logging.error(f"Error al exportar los datos: {e}")
        raise

def cerrar_sap(sap_window):
    try:
        sap_window.close()
        logging.info("Conexión de SAP cerrada.")
    except Exception as e:
        logging.error(f"Error al cerrar SAP: {e}")

def main():
    try:
        app = iniciar_sap()
        titulo_ventana = "SAP Easy Access"
        sap_window = esperar_ventana_ui(titulo_ventana)
        ejecutar_transaccion(sap_window)
        seleccionar_variante(sap_window)
        exportar_datos(sap_window)
        
        # Obtener y listar todos los inputs en la ventana principal
        inputs = obtener_todos_inputs(sap_window)
        for tipo, controles in inputs.items():
            logging.info(f"\nControl Tipo: {tipo}")
            for control in controles:
                try:
                    titulo = control.window_text()
                    auto_id = control.element_info.id
                    logging.info(f" - {tipo}: Título='{titulo}', auto_id='{auto_id}'")
                except Exception as e:
                    logging.error(f"Error al obtener información del control: {e}")
    
    except Exception as e:
        logging.error(f"Se produjo un error durante la ejecución: {e}")
    finally:
        try:
            cerrar_sap(sap_window)
        except:
            pass

if __name__ == "__main__":
    main()