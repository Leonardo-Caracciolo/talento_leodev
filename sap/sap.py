from pyrfc import Connection

# Definir los parámetros de conexión a SAP
sap_conn_params = {
    'user': 'LMARINARO',
    'passwd': 'Marisol40458645_$',
    'ashost': 'mxmex.deloitte.com',
    'sysnr': '02',
    'client': 'PRO',
    'lang': 'ES'
}


# Establecer la conexión
conn = Connection(**sap_conn_params)

# Ejecutar transacción (reemplaza 'STFC_CONNECTION' con tu transacción)
result = conn.call('STFC_CONNECTION')

# Manejar la respuesta
print(result)

# Cerrar la conexión
conn.close()