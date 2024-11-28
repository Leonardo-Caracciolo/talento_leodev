import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
from jinja2 import Environment, FileSystemLoader

def enviar_correo(
    receptor,
    cliente,
    dataframes,
    nombres_adjuntos,
    servidor_smtp="appmail.atrame.deloitte.com",
    puerto_smtp=25,
    cc=None,
):
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
    # Crear el mensaje
    msg = MIMEMultipart()
    msg["From"] = "robot-Tax-AR@deloitte.com"
    msg["To"] = receptor
    msg["Subject"] = "Reporte de Personal - Talento SLATAM"
    if cc:
        msg["Cc"] = ", ".join(cc)

    # Cargar la plantilla de correo
    env = Environment(loader=FileSystemLoader("functions"))
    template = env.get_template("email_template.html")
    html_content = template.render(cliente=cliente)
    msg.attach(MIMEText(html_content, "html"))

    # Adjuntar los DataFrames
    for dataframe, nombre_adjunto in zip(dataframes, nombres_adjuntos):
        part = MIMEBase("application", "octet-stream")
        part.set_payload(dataframe.getvalue())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={nombre_adjunto}",
        )
        msg.attach(part)

    # Enviar el correo
    server = smtplib.SMTP(servidor_smtp, puerto_smtp)
    server.sendmail(msg["From"], [receptor] + (cc if cc else []), msg.as_string())
    server.quit()


# def enviar_correo(
#     receptor,
#     cliente,
#     dataframes,
#     nombres_adjuntos,
#     servidor_smtp="appmail.atrame.deloitte.com",
#     puerto_smtp=25,
#     cc=None,
# ):
#     """
#     Esta función envía un correo electrónico con múltiples DataFrames adjuntos.

#     Parámetros:
#     receptor (str): El correo electrónico del receptor.
#     cliente (str): El nombre del cliente.
#     dataframes (list): Lista de DataFrames que se adjuntarán.
#     nombres_adjuntos (list): Lista de nombres de los archivos adjuntos.
#     servidor_smtp (str): El servidor SMTP.
#     puerto_smtp (int): El puerto SMTP.
#     cc (list): Lista de correos electrónicos para enviar en copia.

#     Retorna:
#     None
#     """
#     # Crear el mensaje
#     msg = MIMEMultipart()
#     msg["From"] = "robot-Tax-AR@deloitte.com"
#     msg["To"] = receptor
#     msg["Subject"] = "Reporte de Personal - Talento SLATAM"
#     if cc:
#         msg["Cc"] = ", ".join(cc)

#     # Cargar la plantilla de correo
#     env = Environment(loader=FileSystemLoader("functions"))
#     template = env.get_template("email_template.html")
#     html_content = template.render(cliente=cliente)
#     msg.attach(MIMEText(html_content, "html"))

#     # Adjuntar los DataFrames
#     for dataframe, nombre_adjunto in zip(dataframes, nombres_adjuntos):
#         part = MIMEBase("application", "octet-stream")
#         part.set_payload(dataframe.getvalue())
#         encoders.encode_base64(part)
#         part.add_header(
#             "Content-Disposition",
#             f"attachment; filename={nombre_adjunto}",
#         )
#         msg.attach(part)

#     # Enviar el correo
#     try:
#         server = smtplib.SMTP(servidor_smtp, puerto_smtp)
#         server.sendmail(msg["From"], [receptor] + (cc if cc else []), msg.as_string())
#         server.quit()
#         print("Correo enviado correctamente")
#     except Exception as e:
#         print(f"Error al enviar el correo: {e}")
