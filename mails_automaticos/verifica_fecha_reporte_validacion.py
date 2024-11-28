import pandas as pd 
from datetime import datetime, timedelta


def obtener_dia_anterior():
    """Verifica si las fechas de la columna 'Fecha' del DF_Validacion son del día anterior
    y si el dia actual es lunes, verifica la fecha de hace 3 días atras

    Args:
        df (_type_): _DF_validacion_
        columna_fecha (_type_): _Nombre de la columna que contiene las fechas_
        
    Return: Retorna una columna Bool con True o false segun corresponda
    """
    
    hoy = datetime.now()
    
    #0 = Lunes , 6 = Domingo
    dia_actual = hoy.weekday()
    
    if dia_actual == 0:
        fecha_comparacion = hoy - timedelta(days= 3)
    else:
        fecha_comparacion = hoy - timedelta( days= 1)

    # df[columna_fecha] = pd.to_datetime(df[columna_fecha])

    return fecha_comparacion.date()
    
if __name__=="__main__":
    dia_anterior = obtener_dia_anterior()
    print(dia_anterior.day)