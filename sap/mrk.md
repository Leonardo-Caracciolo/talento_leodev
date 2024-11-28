**pywinauto** es una poderosa biblioteca de Python diseñada para automatizar aplicaciones de Windows con interfaces gráficas (GUIs). Permite controlar aplicaciones de escritorio como si un usuario las estuviera operando manualmente, interactuando con ventanas, botones, campos de texto y otros controles de la interfaz.

### **1. Introducción a pywinauto**

- **Automatización de GUI:** pywinauto facilita la automatización de tareas repetitivas en aplicaciones de Windows, como ingreso de datos, navegación por menús, clics de botones, etc.
- **Compatibilidad:** Funciona con la mayoría de las aplicaciones basadas en tecnologías como Win32, Windows UI Automation (UIA), y otras basadas en .NET.
- **Lenguaje de Programación:** Está escrito en Python, lo que facilita su integración en scripts y aplicaciones más grandes.

### **2. Principales Backends de pywinauto**

pywinauto soporta dos backends principales que determinan cómo interactúa con la interfaz de usuario de la aplicación:

1. **Win32 Backend (`"win32"`):**
   - Utiliza la API de Win32 para interactuar con controles.
   - Adecuado para aplicaciones tradicionales de escritorio basadas en Win32.

2. **UI Automation Backend (`"uia"`):**
   - Basado en la tecnología Microsoft UI Automation.
   - Soporta aplicaciones más modernas, incluidas aquellas desarrolladas con tecnologías como WPF, Qt, etc.

**Seleccionar Backend:**
Puedes especificar el backend al iniciar una aplicación o al conectar con una existente.

```python
from pywinauto import Application

# Usando el backend "uia"
app = Application(backend="uia").start("ruta_a_la_aplicación.exe")

# Usando el backend "win32"
app = Application(backend="win32").start("ruta_a_la_aplicación.exe")
```

### **3. Métodos para Identificar Elementos de la Interfaz**

pywinauto ofrece varios métodos para localizar y trabajar con los controles de la interfaz de una aplicación:

#### **a. Localización de Ventanas y Controles**

1. window y child_window:**
   - window

        Se utiliza para acceder a una ventana principal de la aplicación basada en ciertos criterios (título, clase, etc.).
   - child_window
  
        Accede a un control hijo dentro de una ventana.

   ```python
   # Acceder a la ventana principal por título
   main_window = app.window(title="Título de la Ventana")

   # Acceder a un botón hijo por título
   boton = main_window.child_window(title="Guardar", control_type="Button")
   ```

2. **Parámetros Comunes:**
   - title
    
        Texto que aparece en la barra de título del control.
   - auto_id
  
        Identificador automático asignado al control.
   - control_type
    
        Tipo de control (e.g., "Button", "Edit", "ComboBox").
   - **`class_name`**: Nombre de la clase de la ventana/control.

   ```python
   boton = main_window.child_window(auto_id="btnGuardar", control_type="Button")
   ```

#### **b. Métodos de Búsqueda Avanzada**

1. **

descendants

:**
   - Recupera una lista de controles que son descendientes directos o indirectos de una ventana específica.

   ```python
   botones = main_window.descendants(control_type="Button")
   for boton in botones:
       print(boton.window_text())
   ```

2. **`children`:**
   - Obtiene únicamente los controles hijos directos de una ventana.

   ```python
   controles = main_window.children()
   for control in controles:
       print(control.window_text())
   ```

3. **Búsqueda por **`best_match`** y **`found_index`**:**
   - Cuando múltiples controles coinciden con los criterios de búsqueda, puedes especificar el `found_index` para seleccionar el deseado.

   ```python
   boton = main_window.child_window(title="Guardar", control_type="Button", found_index=1)
   ```

#### **c. Inspección de Controles**

Para identificar qué atributos utilizar al localizar controles, puedes utilizar la herramienta **Inspect.exe**:

- **Inspect.exe:** Viene incluida en el [Windows SDK](https://developer.microsoft.com/es-es/windows/downloads/windows-10-sdk/). Permite inspeccionar los atributos de los controles de una aplicación, facilitando la identificación de 

title

, `automation_id`, 

control_type

, etc.

### **4. Interactuando con Controles**

Una vez que has identificado un control, pywinauto proporciona métodos para interactuar con él:

- **Clic en Botones:**

  ```python
  boton.click()
  ```

- **Escribir en Campos de Texto:**

  ```python
  campo_texto = main_window.child_window(auto_id="txtUsername", control_type="Edit")
  campo_texto.type_keys("usuario123", with_spaces=True)
  ```

- **Seleccionar Opciones en ComboBoxes:**

  ```python
  combo = main_window.child_window(title="Opciones", control_type="ComboBox")
  combo.select("Opción 1")
  ```

- **Obtener o Establecer Valores:**

  ```python
  valor_actual = campo_texto.get_value()
  campo_texto.set_text("nuevo_valor")
  ```

### **5. Ejemplos Prácticos**

#### **a. Clic en un Botón Específico**

```python
from pywinauto import Application

# Iniciar la aplicación
app = Application(backend="uia").start("ruta_a_la_aplicación.exe")

# Acceder a la ventana principal
main_window = app.window(title="Título de la Ventana")

# Localizar el botón "Guardar" y hacer clic
boton_guardar = main_window.child_window(title="Guardar", control_type="Button")
boton_guardar.wait("visible", timeout=30)
boton_guardar.click()
```

#### **b. Escribir en un Campo de Texto y Seleccionar una Opción**

```python
# Localizar el campo de texto "Usuario" y escribir el nombre de usuario
campo_usuario = main_window.child_window(auto_id="txtUsuario", control_type="Edit")
campo_usuario.type_keys("usuario123", with_spaces=True)

# Localizar el campo de texto "Contraseña" y escribir la contraseña
campo_password = main_window.child_window(auto_id="txtPassword", control_type="Edit")
campo_password.type_keys("contraseña!", with_spaces=True)

# Localizar y hacer clic en el botón "Iniciar Sesión"
boton_login = main_window.child_window(title="Iniciar Sesión", control_type="Button")
boton_login.click()
```

#### **c. Seleccionar una Opción en un Menú**

```python
# Navegar por un menú y seleccionar una opción
main_window.menu_select("Archivo->Nuevo")
```

### **6. Métodos Útiles de pywinauto para Identificar Elementos**

- **`print_control_identifiers()`:**
  - Imprime una estructura jerárquica de todos los controles en una ventana, lo que facilita la identificación de atributos para interactuar con ellos.

  ```python
  main_window.print_control_identifiers()
  ```

- **`exists()`:**
  - Verifica si un control existe.

  ```python
  if boton_guardar.exists():
      boton_guardar.click()
  ```

- **

wait()

 y `wait_not()` Métodos:**
  - Espera a que un control esté en un estado específico (e.g., visible, enabled).

  ```python
  boton_guardar.wait("visible", timeout=30)
  boton_guardar.wait("enabled", timeout=30)
  ```

- **`toggle()` y `check()` Métodos:**
  - Para controles como casillas de verificación o botones de alternancia.

  ```python
  checkbox = main_window.child_window(title="Aceptar términos", control_type="CheckBox")
  checkbox.check()  # Selecciona la casilla
  ```

### **7. Buenas Prácticas al Usar pywinauto**

- **Usar 

wait

 en Lugar de 

time.sleep()

:**
  - Prefiere métodos de espera dinámica (

wait()

) en lugar de pausas fijas para mejorar la eficiencia y fiabilidad.

  ```python
  # Mejor
  boton_guardar.wait("visible", timeout=30)
  
  # Evitar
  time.sleep(5)
  ```

- **Inspeccionar Controles Antes de Automatizar:**
  - Utiliza `Inspect.exe` o `print_control_identifiers()` para comprender la estructura de la interfaz y seleccionar los atributos correctos.

- **Manejar Excepciones:**
  - Implementa manejo de errores para capturar y responder a situaciones inesperadas.

  ```python
  try:
      boton_guardar.click()
  except Exception as e:
      logging.error(f"Error al hacer clic en 'Guardar': {e}")
  ```

- **Mantener el Código Limpio y Modular:**
  - Organiza las interacciones en funciones específicas para facilitar el mantenimiento y la reutilización.

### **8. Recursos Adicionales**

- **Documentación Oficial de pywinauto:**
  - [https://pywinauto.readthedocs.io/](https://pywinauto.readthedocs.io/)

- **Tutoriales y Ejemplos:**
  - [Automate GUI Applications in Python](https://realpython.com/pywin32-python/) *(Aunque enfocado en pywin32, muchos conceptos son aplicables)*
  - [GitHub - pywinauto Examples](https://github.com/pywinauto/pywinauto/tree/master/examples)

- **Herramienta Inspect.exe:**
  - [Descargar Inspect.exe](https://docs.microsoft.com/es-es/windows/win32/winauto/inspect-objects)

### **Conclusión**

pywinauto es una herramienta versátil para automatizar y controlar aplicaciones de Windows mediante Python. Al entender sus backends, métodos de localización de controles y prácticas recomendadas, puedes crear scripts robustos que interactúen de manera efectiva con aplicaciones complejas como SAP GUI. Utiliza herramientas de inspección y asegúrate de manejar adecuadamente los estados de los controles para maximizar la fiabilidad de tus automatizaciones.



Para obtener todos los elementos de entrada (**inputs**) presentes en una ventana utilizando **pywinauto**, debes identificar y listar los controles que permiten la entrada de datos por parte del usuario. Estos pueden incluir campos de texto (**Edit**), casillas de verificación (**CheckBox**), botones de radio (**RadioButton**), cuadros combinados (**ComboBox**), entre otros.

A continuación, se detalla cómo lograr esto de manera efectiva:

### **1. Identificar Tipos de Controles de Entrada**

Antes de listar los controles, es importante saber qué tipos de controles representan entradas de datos en la aplicación que estás automatizando. Algunos de los más comunes son:

- **Edit**: Campos de texto donde el usuario puede escribir.
- **ComboBox**: Cuadros combinados que permiten seleccionar de una lista desplegable o ingresar un valor personalizado.
- **CheckBox**: Casillas de verificación que pueden estar marcadas o desmarcadas.
- **RadioButton**: Botones de opción que permiten seleccionar una opción entre varias.
- **Slider**: Controles deslizantes para seleccionar un valor dentro de un rango.
- **DateTimePicker**: Selectores de fecha y hora.

### **2. Utilizar 

descendants

 para Buscar Controles de Entrada**

La función 

descendants

 de **pywinauto** permite buscar todos los controles descendientes de una ventana que coinciden con ciertos criterios. Puedes utilizarla para buscar controles específicos que representan entradas de datos.

#### **Ejemplo de Función para Obtener Todos los Inputs**

```python
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
```

#### **Uso en el Script Principal**

```python
def main():
    try:
        app = iniciar_sap()
        titulo_ventana = "SAP Easy Access"
        sap_window = esperar_ventana_ui(titulo_ventana)
        ejecutar_transaccion(sap_window)
        seleccionar_variante(sap_window)
        exportar_datos(sap_window)
        
        # Obtener todos los inputs en la ventana actual
        inputs = obtener_todos_inputs(sap_window)
        
        # Iterar y mostrar información de cada tipo de input
        for tipo, controles in inputs.items():
            print(f"\nControl Tipo: {tipo}")
            for control in controles:
                try:
                    titulo = control.window_text()
                    auto_id = control.element_info.id
                    print(f" - {tipo}: Título='{titulo}', auto_id='{auto_id}'")
                except Exception as e:
                    logging.error(f"Error al obtener información del control: {e}")
    
    except Exception as e:
        logging.error(f"Se produjo un error durante la ejecución: {e}")
    finally:
        try:
            cerrar_sap(sap_window)
        except:
            pass
```

### **3. Inspeccionar Controles con `print_control_identifiers()`**

Para identificar con precisión los atributos de cada control de entrada, puedes utilizar el método `print_control_identifiers()`. Este método imprime una estructura jerárquica de todos los controles disponibles en la ventana, incluyendo sus 

title

, `automation_id`, y 

control_type

.

#### **Ejemplo de Uso**

```python
def inspeccionar_controles(sap_window):
    """
    Imprime los identificadores de todos los controles en la ventana proporcionada.

    :param sap_window: Objeto de la ventana a inspeccionar.
    """
    try:
        sap_window.print_control_identifiers()
    except Exception as e:
        logging.error(f"Error al inspeccionar los controles: {e}")
        raise
```

#### **Incorporar en el Flujo de Trabajo**

Puedes llamar a esta función después de haber accedido a la ventana principal para visualizar todos los controles disponibles:

```python
def main():
    try:
        app = iniciar_sap()
        titulo_ventana = "SAP Easy Access"
        sap_window = esperar_ventana_ui(titulo_ventana)
        ejecutar_transaccion(sap_window)
        seleccionar_variante(sap_window)
        exportar_datos(sap_window)
        
        # Inspeccionar y listar controles
        inspeccionar_controles(sap_window)
        
        # Obtener todos los inputs en la ventana actual
        inputs = obtener_todos_inputs(sap_window)
        
        # Procesar los inputs según sea necesario
        for tipo, controles in inputs.items():
            print(f"\nControl Tipo: {tipo}")
            for control in controles:
                try:
                    titulo = control.window_text()
                    auto_id = control.element_info.id
                    print(f" - {tipo}: Título='{titulo}', auto_id='{auto_id}'")
                except Exception as e:
                    logging.error(f"Error al obtener información del control: {e}")
    
    except Exception as e:
        logging.error(f"Se produjo un error durante la ejecución: {e}")
    finally:
        try:
            cerrar_sap(sap_window)
        except:
            pass
```

### **4. Trabajar con los Controles de Entrada**

Una vez que hayas identificado los controles de entrada, puedes interactuar con ellos según tus necesidades. A continuación, se presentan ejemplos de cómo trabajar con diferentes tipos de inputs:

#### **a. Escribir en un Campo de Texto (`Edit`)**

```python
def escribir_en_campo_texto(sap_window, auto_id, texto):
    try:
        campo_texto = sap_window.child_window(auto_id=auto_id, control_type="Edit")
        campo_texto.set_text(texto)
        logging.info(f"Texto '{texto}' ingresado en el campo con auto_id='{auto_id}'.")
    except Exception as e:
        logging.error(f"Error al escribir en el campo de texto: {e}")
        raise
```

#### **b. Seleccionar una Opción en un Cuadro Combinado (`ComboBox`)**

```python
def seleccionar_combo_box(sap_window, auto_id, opcion):
    try:
        combo = sap_window.child_window(auto_id=auto_id, control_type="ComboBox")
        combo.select(opcion)
        logging.info(f"Opción '{opcion}' seleccionada en ComboBox con auto_id='{auto_id}'.")
    except Exception as e:
        logging.error(f"Error al seleccionar en ComboBox: {e}")
        raise
```

#### **c. Marcar una Casilla de Verificación (`CheckBox`)**

```python
def marcar_checkbox(sap_window, auto_id):
    try:
        checkbox = sap_window.child_window(auto_id=auto_id, control_type="CheckBox")
        checkbox.check()
        logging.info(f"Casilla de verificación con auto_id='{auto_id}' marcada.")
    except Exception as e:
        logging.error(f"Error al marcar CheckBox: {e}")
        raise
```

#### **d. Seleccionar un Botón de Radio (`RadioButton`)**

```python
def seleccionar_radio_button(sap_window, auto_id):
    try:
        radio = sap_window.child_window(auto_id=auto_id, control_type="RadioButton")
        radio.select()
        logging.info(f"RadioButton con auto_id='{auto_id}' seleccionado.")
    except Exception as e:
        logging.error(f"Error al seleccionar RadioButton: {e}")
        raise
```

### **5. Herramientas para Inspeccionar Controles**

Para facilitar la identificación de los atributos necesarios para interactuar con los controles, utiliza herramientas de inspección que te proporcionen detalles sobre la jerarquía y propiedades de los widgets de la interfaz.

#### **a. Inspect.exe**

**Inspect.exe** es una herramienta incluida en el [Windows SDK](https://developer.microsoft.com/es-es/windows/downloads/windows-10-sdk/) que permite inspeccionar los elementos de la interfaz de usuario y ver sus propiedades.

**Pasos para Usar Inspect.exe:**

1. **Instalación**: Descarga e instala el [Windows 10 SDK](https://developer.microsoft.com/es-es/windows/downloads/windows-10-sdk/) si aún no lo tienes.
2. **Abrir Inspect.exe**: Una vez instalado, busca **Inspect.exe** en el menú de inicio o en el directorio de instalación del SDK.
3. **Inspeccionar Controles**: Ejecuta la aplicación SAP GUI y usa **Inspect.exe** para señalar y seleccionar los controles de los cuales deseas obtener información.
4. **Obtener Propiedades**: Al seleccionar un control, **Inspect.exe** mostrará propiedades como `Name` (equivalente a 

title

), `AutomationId`, `ControlType`, entre otros, que puedes usar en tu script de **pywinauto**.

#### **b. Herramienta `print_control_identifiers`**

Como se mencionó anteriormente, el método `print_control_identifiers()` de **pywinauto** también es útil para listar todos los controles disponibles en una ventana.

```python
def inspeccionar_controles(sap_window):
    try:
        sap_window.print_control_identifiers()
    except Exception as e:
        logging.error(f"Error al inspeccionar los controles: {e}")
        raise
```

### **6. Consideraciones Adicionales**

- **Backends de pywinauto**: Asegúrate de utilizar el backend adecuado (`"uia"` o `"win32"`) según la tecnología de la interfaz de usuario de la aplicación SAP que estás automatizando.
  
  ```python
  app = Application(backend="uia").start("ruta_a_la_aplicación.exe")
  ```

- **Manejo de Excepciones**: Implementa manejo de errores para capturar situaciones donde un control no se encuentre o no esté accesible.

- **Espera Dinámica vs. 

time.sleep()

**: Prefiere métodos de espera dinámica como 

wait("visible")

 o 

wait("enabled")

 en lugar de usar 

time.sleep()

 para mejorar la eficiencia y fiabilidad de tu script.

- **Segmentación por Jerarquía**: Los controles pueden estar anidados dentro de otros controles. Asegúrate de navegar correctamente por la jerarquía para acceder a los controles deseados.

- **Automatización Responsable**: Siempre verifica que la automatización no interfiera con otras operaciones de la aplicación y respeta las políticas de uso de tu organización.

### **7. Ejemplo Completo Integrando la Obtención de Inputs**

A continuación, se muestra cómo podrías integrar la función para obtener todos los inputs en tu script existente:

```python
import logging
import os
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pywinauto import Application, Desktop

# Cargar variables desde .env
load_dotenv()

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
```

### **8. Explicación Paso a Paso**

1. **Importaciones y Configuración Inicial:**
   - Importa las librerías necesarias, carga las variables de entorno y configura el logging para rastrear las acciones y errores.

2. **Funciones de Automatización:**
   - **

iniciar_sap()

**: Inicia la aplicación SAP GUI con las credenciales proporcionadas.
   - **

esperar_ventana()

, 

esperar_ventana_ui()

, 

esperar_ventana_win32()

**: Funciones para esperar y enfocarse en ventanas específicas, utilizando diferentes backends según sea necesario.
   - **

ejecutar_transaccion()

**: Envía el código de la transacción SAP para navegar dentro de la aplicación.
   - **

seleccionar_variante()

**: Realiza una serie de interacciones para seleccionar una variante específica dentro de la aplicación, incluyendo esperar y clicar en botones, escribir fechas, y más.
   - **`obtener_todos_inputs()`**: Obtiene todos los controles de entrada en una ventana específica, agrupados por tipo.
   - **

listar_botones()

**: Lista y registra todos los botones presentes en una ventana.
   - **`inspeccionar_controles()`**: Imprime todos los controles disponibles en una ventana para su inspección.

3. **Interacción con Inputs:**
   - Después de realizar las acciones necesarias para navegar dentro de SAP, se llama a `obtener_todos_inputs()` para listar todos los inputs disponibles en la ventana actual.
   - Se itera sobre los diferentes tipos de controles de entrada y se registra su información (

title

 y 

auto_id

) para facilitar posteriores interacciones.

4. **Funciones Adicionales:**
   - **

ingresar_tabla()

** y **

exportar_datos()

**: Funciones para ingresar nombres de tablas y exportar datos desde SAP.
   - **

cerrar_sap()

**: Cierra la conexión con SAP GUI.

5. **Ejecución del Script:**
   - En la función 

main()

, se orquesta la ejecución de todas las funciones anteriores para automatizar el flujo de trabajo deseado en SAP GUI, incluyendo la obtención y listaje de todos los inputs disponibles.

### **9. Buenas Prácticas**

- **Usar Backends Adecuados:** Dependiendo de la tecnología de la interfaz de SAP, selecciona el backend apropiado (`"uia"` es generalmente más adecuado para interfaces modernas).

- **Inspeccionar Controles Antes de Automatizar:** Utiliza herramientas como **Inspect.exe** o `print_control_identifiers()` para entender la estructura de la interfaz y asegurarte de que estás interactuando con los controles correctos.

- **Implementar Manejo de Errores Adecuado:** Captura y maneja excepciones para evitar que el script falle silenciosamente y para proporcionar información útil de depuración.

- **Evitar 

time.sleep()

 Siempre que Sea Posible:** Prefiere métodos de espera dinámica (

wait("visible")

, 

wait("enabled")

) para mejorar la eficiencia y fiabilidad del script.

- **Registrar Acciones y Errores:** Utiliza el logging para mantener un registro detallado de las acciones realizadas y de cualquier error que ocurra. Esto facilita la depuración y el monitoreo del script.

- **Mantener el Código Modular y Reutilizable:** Organiza el código en funciones bien definidas que puedan ser reutilizadas y mantenidas fácilmente.

### **10. Recursos Adicionales**

- **Documentación Oficial de pywinauto:**
  - [pywinauto Documentation](https://pywinauto.readthedocs.io/)

- **Tutoriales y Ejemplos:**
  - [GitHub - pywinauto Examples](https://github.com/pywinauto/pywinauto/tree/master/examples)
  - [Automate GUI Applications in Python](https://realpython.com/pywin32-python/) *(Aunque enfocado en pywin32, muchos conceptos son aplicables)*

- **Herramienta Inspect.exe:**
  - [Descargar Inspect.exe](https://docs.microsoft.com/es-es/windows/win32/winauto/inspect-objects)

### **Conclusión**

Utilizando **pywinauto**, puedes automatizar la interacción con aplicaciones de Windows como SAP GUI de manera eficiente y precisa. Identificar y listar todos los controles de entrada te permite comprender mejor la interfaz de usuario y automatizar tareas complejas de manera robusta. Asegúrate de inspeccionar cuidadosamente los controles, manejar adecuadamente los estados de espera y errores, y mantener un código modular y bien documentado para facilitar el mantenimiento y la escalabilidad de tus scripts de automatización.