
from datetime import datetime, timedelta
import re
import smtplib
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from verifica_fecha_reporte_validacion import obtener_dia_anterior

# Cargar variables de entorno desde .env
load_dotenv()

# PATH_HTML_TEMPLATE = os.getenv("PATH_HTML_TEMPLATE", r"C:\Users\lecaracciolo\Music\email_template.html")
RECEPTOR_DEV = os.getenv("RECEPTOR_DEV")
PATH_HTML_TEMPLATE = os.getenv("PATH_HTML_TEMPLATE")
PATH_HTML_TEMPLATE_SOCIO = os.getenv("PATH_HTML_TEMPLATE_SOCIO")
PATH_HTML_TEMPLATE_SEUN = os.getenv("PATH_HTML_TEMPLATE_SEUN")
PATH_HTML_TEMPLATE_MARKETPLACE = os.getenv("PATH_HTML_TEMPLATE_MARKETPLACE")
RUTA_IMAGENES = os.getenv("RUTA_IMAGENES")
PATH_CSS = os.getenv("PATH_CSS")

def embed_images_in_html(html_content, image_directory):
    # Diccionario para mapear las rutas de las imágenes a sus Content-IDs
    cid_dict = {}
    image_paths = []

    # Recorrer todos los archivos en el directorio de imágenes
    for filename in os.listdir(image_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(image_directory, filename)
            image_paths.append(image_path)
            cid_key = f'image{len(cid_dict) + 1}'
            cid_dict[image_path] = cid_key

    # Reemplazar las rutas de las imágenes en el HTML
    def replace_image_src(match):
        img_tag = match.group(0)
        src = match.group(1)
        # Obtener solo el nombre del archivo de la ruta
        filename = os.path.basename(src)
        for path in image_paths:
            if filename in path:
                new_src = f'src="cid:{cid_dict[path]}"'
                img_tag = img_tag.replace(f'src="{src}"', new_src)
                break
        return img_tag

    html_content = re.sub(r'src="([^"]+)"', replace_image_src, html_content)
    return html_content, cid_dict

def send_email(
    receptor: str,
    mensaje_modificado: str,
    subject: str,
    archivo_adjunto: str = None,
    servidor_smtp: str = "appmail.atrame.deloitte.com",
    puerto_smtp: int =25,
    cc: str = None,
) -> None:
    """
    Esta función envía un correo electrónico con múltiples DataFrames adjuntos.

    Parámetros:
    receptor (str): El correo electrónico del receptor.
    cliente (str): El nombre del cliente.
    dataframes (list): Lista de DataFrames que se adjuntarán.
    nombres_adjuntos (list): Lista de nombres de los archivos adjuntos.
    servidor_smtp (str): El servidor SMTP.
    puerto_smtp (int): El puerto SMTP.
    cc (list): Lista de correos electrónicos para enviar en copia.

    Retorna:
    None
    """
    # RUTA_IMAGENES = r'C:\Users\rtolaba\Desktop\DTI\BackUps-d\img_mail_talento'
    # Embedir imágenes en el contenido HTML
    html_content, cid_dict = embed_images_in_html(mensaje_modificado, RUTA_IMAGENES)

    # Crear el mensaje
    msg = MIMEMultipart('related')
    msg["From"] = "robot-Tax-AR@deloitte.com"
    # msg["To"] = ";".join(receptor)
    msg["To"] = receptor
    if cc:
        msg['Cc'] = cc
    msg["Subject"] = subject

    # Crear la parte HTML
    html_part = MIMEText(html_content, 'html')

    # Adjuntar la parte HTML al mensaje
    msg.attach(html_part)

    # Adjuntar imágenes al correo
    for image_path, cid in cid_dict.items():
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            image = MIMEImage(img_data)
            image.add_header('Content-ID', f'<{cid}>')
            image.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            msg.attach(image)

    # archivo_adjunto = r"C:\Users\rtolaba\Desktop\proyectos\Talento_Web\Modelo_mail\Indicadores de uso detallados.xlsx"
    # Adjuntar el archivo
    if archivo_adjunto:
        with open(archivo_adjunto, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(archivo_adjunto)
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file_name}')
            msg.attach(part)

    # Enviar el correo electrónico
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
        server.send_message(msg)


def armar_tabla_html(contador, socio_param, linea_servicio_param, pais_param, oficina_param, cant_rep_no_entregados, cant_prof_no_entregados):

    color_fondo = ";background:#E2EFD9"

    # Crear nuevas filas dinámicas
    new_rows = f"""
    <tr style='mso-yfti-irow:{contador};height:37.8pt'>
        <td width=109 style='width:81.85pt;border:solid windowtext 1.0pt;
        border-top:none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:
        solid windowtext .5pt{color_fondo if contador == 1 else ""};padding:0cm 5.4pt 0cm 5.4pt;
        height:37.8pt'>
        <p class=xmsonormal align=center style='text-align:center'><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;font-family:"Aptos Narrow",sans-serif;color:black;mso-ansi-language:
        ES-MX'>{socio_param}</span></span><span style='mso-bookmark:_MailOriginal'></span><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;mso-ansi-language:ES-MX'><o:p></o:p></span></span></p>
        </td>
        <span style='mso-bookmark:_MailOriginal'></span>
        <td width=89 style='width:66.4pt;border-top:none;border-left:none;
        border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
        mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
        mso-border-alt:solid windowtext .5pt{color_fondo if contador == 1 else ""};padding:0cm 5.4pt 0cm 5.4pt;
        height:37.8pt'>
        <p class=xmsonormal align=center style='text-align:center'><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;font-family:"Aptos Narrow",sans-serif;color:black;mso-ansi-language:
        ES-MX'>{linea_servicio_param}</span></span><span style='mso-bookmark:_MailOriginal'></span><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;mso-ansi-language:ES-MX'><o:p></o:p></span></span></p>
        </td>
        <span style='mso-bookmark:_MailOriginal'></span>
        <td width=85 style='width:63.4pt;border-top:none;border-left:none;
        border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
        mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
        mso-border-alt:solid windowtext .5pt{color_fondo if contador == 1 else ""};padding:0cm 5.4pt 0cm 5.4pt;
        height:37.8pt'>
        <p class=xmsonormal align=center style='text-align:center'><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;font-family:"Aptos Narrow",sans-serif;color:black;mso-ansi-language:
        ES-MX'>{pais_param}</span></span><span style='mso-bookmark:_MailOriginal'></span><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;mso-ansi-language:ES-MX'><o:p></o:p></span></span></p>
        </td>
        <span style='mso-bookmark:_MailOriginal'></span>
        <td width=77 style='width:57.75pt;border-top:none;border-left:none;
        border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
        mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
        mso-border-alt:solid windowtext .5pt{color_fondo if contador == 1 else ""};padding:0cm 5.4pt 0cm 5.4pt;
        height:37.8pt'>
        <p class=xmsonormal align=center style='text-align:center'><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;font-family:"Aptos Narrow",sans-serif;color:black;mso-ansi-language:
        ES-MX'>{oficina_param}</span></span><span style='mso-bookmark:_MailOriginal'></span><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;mso-ansi-language:ES-MX'><o:p></o:p></span></span></p>
        </td>
        <span style='mso-bookmark:_MailOriginal'></span>
        <td width=85 style='width:63.55pt;border-top:none;border-left:none;
        border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
        mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
        mso-border-alt:solid windowtext .5pt{color_fondo if contador == 1 else ""};padding:0cm 0cm 0cm 0cm;
        height:37.8pt'>
        <p class=xmsonormal align=center style='text-align:center'><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;font-family:"Aptos Narrow",sans-serif;color:black;mso-ansi-language:
        ES-MX'>{cant_rep_no_entregados}</span></span><span style='mso-bookmark:_MailOriginal'><span
        lang=ES-MX style='font-size:8.0pt;color:black;mso-ansi-language:ES-MX'><o:p></o:p></span></span></p>
        </td>
        <span style='mso-bookmark:_MailOriginal'></span>
        <td width=99 style='width:74.25pt;border-top:none;border-left:none;
        border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
        mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
        mso-border-alt:solid windowtext .5pt{color_fondo if contador == 1 else ""};padding:0cm 0cm 0cm 0cm;
        height:37.8pt'>
        <p class=xmsonormal align=center style='text-align:center'><span
        style='mso-bookmark:_MailOriginal'><span lang=ES-MX style='font-size:
        8.0pt;color:black;mso-ansi-language:ES-MX'>{cant_prof_no_entregados}<o:p></o:p></span></span></p>
        <span style='mso-bookmark:_MailOriginal'></span></td>
        <span style='mso-bookmark:_MailOriginal'></span>
       </tr>
    """

    return new_rows

def armar_filas_tablas(df_tabla):
    list_td = []
    contador = 1
    for index, row in df_tabla.iterrows():
        
#armar_tabla_html(contador, mes_param, socio_param, linea_servicio_param, pais_param, oficina_param, cant_rep_no_entregados, cant_prof_no_entregados):
        socio = row['Socio']
        linea_servicio = row['Linea']
        pais = row['Pais']
        oficina = row['Oficina']
        reportes_no_entregados = row['reportes_no_entregados']
        profesionales_no_entregaron = row['profesionales_no_entregaron']

        list_td.append(armar_tabla_html(contador, socio, linea_servicio, pais, oficina, reportes_no_entregados, profesionales_no_entregaron))
        if contador == 1:
            contador = 2
        elif contador == 2:
            contador = 1

    # Una vez obtenemos las filas juntamos todo en un solo string
    contenido_lista_tablas = ''
    for elemento in list_td:
        contenido_lista_tablas += f'{elemento}'

    return contenido_lista_tablas

def read_and_modify_html(
        nombre_apellido: str,
        plantilla: str,
        datatable: pd.DataFrame = None,
        linea_servicio: str = None,
        pais: str = None,
        market_place: str = None
) -> str:
    """
    Lee y modifica el contenido HTML.
    
    Parámetros:
    - nombre_apellido (str): nombre del profesional, socio, seun o lider del market place.
    - plantilla (str): tipo de renderizado html.
      opciones: 'empleado', 'socio', 'seun' o 'marketplace'.
    - datatable (pd.DataFrame): tabla que se mostrará (si es socio, seun o marketplace).
    - linea_servicio (str): linea de servicio del seun (solo para plantilla 'seun')
    - pais (str): pais del seun (solo para plantilla 'seun')
    - market_place (str): market place (solo para plantilla 'marketplace')

    Retorna:
    html_content (str): Contenido html con las variables renderizadas.
    """

    # Obtener la fecha actual
    fecha_actual = datetime.now()
    fecha_ayer = obtener_dia_anterior()

    # Extraer el mes y el año
    lista_meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    mes_actual = lista_meses[fecha_actual.month - 1]
    año_actual = fecha_actual.year

    # Selecciono la plantilla html para el mail, cambiando las variables correspondientes
    if plantilla == "empleado":
        with open(PATH_HTML_TEMPLATE, "r", encoding="utf-8") as file:
            html_content = file.read()
        html_content = html_content.replace("{dia_anterior}", str(fecha_ayer.strftime('%d-%m-%Y')))
        html_content = html_content.replace("{dia_hoy}", str(fecha_actual.strftime('%d-%m-%Y')))
    else:
        if plantilla == "socio":
            with open(PATH_HTML_TEMPLATE_SOCIO, "r", encoding="utf-8") as file:
                html_content = file.read()

        elif plantilla == "seun":
            with open(PATH_HTML_TEMPLATE_SEUN, "r", encoding="utf-8") as file:
                html_content = file.read()
            html_content = html_content.replace("{linea_servicio}", linea_servicio)
            html_content = html_content.replace("{pais}", pais)

        elif plantilla == "marketplace":
            with open(PATH_HTML_TEMPLATE_MARKETPLACE, "r", encoding="utf-8") as file:
                html_content = file.read()
            html_content = html_content.replace("{market_place}", market_place)
        
        else: print(f"Error: la plantilla '{plantilla}' no existe.")

        datatable_html = datatable.to_html(index=False, classes='data', header=True)

        html_content = html_content.replace("{dia_hora_envio}", str(fecha_actual.strftime('%d-%m-%Y %H:%M:%S')))
        html_content = html_content.replace("{detalle_datatable}", datatable_html)
        html_content = html_content.replace("{mes}", str(mes_actual))
    
    html_content = html_content.replace("{nombre_apellido}", str(nombre_apellido))
    html_content = html_content.replace("{mes_actual}", str(mes_actual))
    html_content = html_content.replace("{año_actual}", str(año_actual))
    
    #? Agrego los estilos css
    with open(PATH_CSS, "r", encoding="utf-8") as file:
        css_content = file.read()
    html_content = html_content.replace("{styles}", f'<style>{css_content}</style>')

    return html_content

def obtener_data_excel_ejemplo(ruta):

    # Ruta al archivo Excel
    file_path = ruta

    # Nombre de la hoja
    sheet_name = 'ejemplo'

    # Leer los datos de la hoja específica en un DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    return df


if __name__=="__main__":

    # ruta_excel_ejemplo = r"C:\Users\rtolaba\Desktop\proyectos\Talento_Web\Modelo_mail\datos_de_prueba_mail_Gaston.xlsx"
    # ruta_excel_ejemplo = r""
    # df_datos_ejemplos = obtener_data_excel_ejemplo(ruta_excel_ejemplo)

    #nombre_apellido, fecha_desde, fecha_hasta: str, rol_socio: str, df_tabla

    # rol_socio = 'SEUN, Cono Sur BPS'
    # df_tabla = df_datos_ejemplos

    # receptor=email,
    # receptor="lmarinaro@deloitte.com",
    # nombre_apellido = "Quignon, Gaston"
    remitente = "robot-Tax-AR@deloitte.com"
    receptor="amiriarte@deloitte.com"
    subject="Indicadores de uso | Talento"
    # cpy = "lmarinaro@deloitte.com"

    # #? Profesional
    # nombre_apellido = "AGUIRRE MARIA SOL"
    # subject="IMPORTANTE Reportes de tiempo PENDIENTE dia 21-11-2024"
    # html_final = read_and_modify_html(nombre_apellido,"empleado")
    # send_email(receptor, html_final, subject)

    # #? SOCIO
    # nombre_apellido = "LORDI NOELIA VANESA"
    # subject="IMPORTANTE - PROFESIONALES ASIGNADOS - BLUE TAX & CARGABILIDAD - noviembre"
    # df = pd.DataFrame({
    #     "Mes de Noviembre": ["1-11-2024 al 3-11-2024", "4-11-2024 al 10-11-2024", "11-11-2024 al 17-11-2024", "18-11-2024 al 24-11-2024", "25-11-2024 al 30-11-2024"],
    #     "Profesionales sin reporte": [0,2,1,1,0],
    #     "Reportes no entregados": [0,6,4,1,0],
    # })
    # html_final = read_and_modify_html(nombre_apellido,"socio", datatable=df)
    # send_email(receptor, html_final, subject)

    # ? SEUN
    nombre_apellido = "LORDI NOELIA VANESA"
    subject="IMPORTANTE – PROFESIONALES ASIGNADOS BPS - Tax - Argentina – BLUE TAX & CARGABILIDAD - noviembre"
    df = pd.DataFrame({
        "Mes de Noviembre": ["1-11-2024 al 3-11-2024", "4-11-2024 al 10-11-2024", "11-11-2024 al 17-11-2024", "18-11-2024 al 24-11-2024", "25-11-2024 al 30-11-2024"],
        "Profesionales sin reporte": [0,2,1,1,0],
        "Reportes no entregados": [0,6,4,1,0],
    })
    html_final = read_and_modify_html(nombre_apellido,"seun", datatable=df, linea_servicio="BPS - Tax", pais="Argentina")
    send_email(receptor, html_final, subject)

    # # ? MarketPLace
    # nombre_apellido = "CATALDO ATILIO"
    # subject="IMPORTANTE – PROFESIONALES ASIGNADOS CONOSUR – BLUE TAX & CARGABILIDAD - noviembre"
    # df = pd.DataFrame({
    #     "Mes de Noviembre": ["1-11-2024 al 3-11-2024", "4-11-2024 al 10-11-2024", "11-11-2024 al 17-11-2024", "18-11-2024 al 24-11-2024", "25-11-2024 al 30-11-2024"],
    #     "Profesionales sin reporte": [0,2,1,1,0],
    #     "Reportes no entregados": [0,6,4,1,0],
    # })
    # html_final = read_and_modify_html(nombre_apellido,"marketplace", datatable=df, market_place="CONOSUR")
    # send_email(receptor, html_final, subject)