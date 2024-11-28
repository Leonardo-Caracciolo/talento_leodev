import sys
from datetime import datetime
from df_seun import main as seun_main
from df_empleado import main as empleado_main
from df_socio import main as socio_main
from registrar_ejecuciones import create_table_registro_ejecuciones, registrar_ejecucion_db

def main():
    create_table_registro_ejecuciones()
    try:
        # iniciado = datetime.now()
        # estado = seun_main()
        # registrar_ejecucion_db("envio_correo_seun", estado, iniciado)

        # iniciado = datetime.now()
        # estado = empleado_main() #? Funciona correcto
        # registrar_ejecucion_db("envio_correo_empleado", estado, iniciado)
        
        iniciado = datetime.now()
        estado = socio_main()
        registrar_ejecucion_db("envio_correo_socio", estado, iniciado)
        
        print("Ejecución completada exitosamente.")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        sys.exit()


if __name__ == "__main__":
    main()
