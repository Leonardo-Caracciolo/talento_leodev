
# Gestión de Entornos en Anaconda Prompt

## Archivos estaticos

Los archivos estaticos que no se trackean en git estarán en este directorio:
https://resources.deloitte.com/:f:/r/sites/RPATax-GrupoInterno/Shared%20Documents/General/Proyecto%20Talento%26Operaciones/data?csf=1&web=1&e=mIZxdM

## Crear un nuevo entorno

```bash
conda create --name nombre_del_entorno python=3.8
```

Activar un entorno

```bash
conda activate nombre_del_entorno
```

Desactivar un entorno

```bash
conda deactivate
```

Listar todos los entornos

```bash
conda env list
```

Instalar paquetes en un entorno

```bash
conda install nombre_del_paquete
```

Eliminar un entorno

```bash
conda remove --name nombre_del_entorno --all
```

Exportar un entorno

```bash
conda env export > entorno.yml
```

Importar un entorno

```bash
conda env create -f entorno.yml

Actualizar un entorno

```bash
conda env update --file enviroment.yml --prune
```

----------------

# Correr el servidor de Uvicorn

```bash
conda activate talento_sqlmodel
uvicorn app.main:app --reload
```

Este resumen en Markdown contiene los comandos básicos necesarios para gestionar entornos en Anaconda Prompt.

## Descripción del Proyecto

Este proyecto carga, transforma y almacena datos en una base de datos utilizando SQLModel. Los datos se cargan desde archivos Excel, se transforman según diccionarios de mapeo y se almacenan en tablas de la base de datos.

### Estructura del Proyecto

- `models.py`: Define la estructura de las tablas en la base de datos utilizando SQLModel.
- `obtener_dfs.py`: Proporciona funciones para cargar, transformar y almacenar datos.

### Funciones Principales

#### `obtener_dfs.py`

- `get_file_hashes()`: Obtiene los hashes de los archivos de datos.
- `create_hashes_table_if_not_exists(engine)`: Crea la tabla de hashes si no existe.
- `save_dataframe_to_db(df: pd.DataFrame, model)`: Guarda un DataFrame en la base de datos.
- `rename_and_convert_columns(df: pd.DataFrame, mapping: Dict[str, Tuple[str, str]]) -> pd.DataFrame`: Renombra y convierte las columnas de un DataFrame según un diccionario de mapeo.
- `verify_and_update_data()`: Verifica y actualiza los datos en la base de datos si los archivos han cambiado.

### Mapeos

Los diccionarios de mapeo se utilizan para transformar los nombres de las columnas y los tipos de datos de los DataFrames antes de almacenarlos en la base de datos.

- `personal_mapping`: Diccionario de mapeo para el DataFrame de personal.
- `seun_mapping`: Diccionario de mapeo para el DataFrame de SEUN.
- `utilizacion_mapping`: Diccionario de mapeo para el DataFrame de utilización.
- `validacion_mapping`: Diccionario de mapeo para el DataFrame de validación.

### Uso

1. Cargar los datos desde archivos Excel.
2. Renombrar y convertir las columnas utilizando `rename_and_convert_columns`.
3. Guardar los DataFrames en la base de datos utilizando `save_dataframe_to_db`.

Este flujo asegura que los datos se transformen correctamente desde los archivos de entrada hasta las tablas de la base de datos, respetando la estructura y los tipos de datos definidos en los modelos.


### Estructura del archivo 'config.json' (ejemplo de datapaths):
    'file_personal': "C:/Users/amiriarte/OneDrive - Deloitte (O365D)/VSC/RepositorioLio/talento_sqlmodel/data/inputs/testCopia/personal.xlsx",
    "file_utilizacion": "C:/Users/amiriarte/OneDrive - Deloitte (O365D)/VSC/RepositorioLio/talento_sqlmodel/data/inputs/testCopia/utilizacion.xlsx",
    "file_utilizacion_actual": "C:/Users/amiriarte/OneDrive - Deloitte (O365D)/VSC/RepositorioLio/talento_sqlmodel/data/inputs/testCopia/Utilizacion I&SL.xlsx",
    "file_validacion": "C:/Users/amiriarte/OneDrive - Deloitte (O365D)/VSC/RepositorioLio/talento_sqlmodel/data/inputs/testCopia/validacion.xlsx",
    "file_total_socios": "C:/Users/amiriarte/OneDrive - Deloitte (O365D)/VSC/RepositorioLio/talento_sqlmodel/data/inputs/testCopia/Base concentrado.xlsx",
    "file_mapeo_cecos_y_seunes": "C:/Users/amiriarte/OneDrive - Deloitte (O365D)/VSC/RepositorioLio/talento_sqlmodel/data/inputs/testCopia/Mapeo CeCos y SEUNES.xlsx"
