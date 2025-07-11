from django.core.mail import send_mail
from datetime import date, timedelta
from django.db import connection

def enviar_notificaciones():
    mañana = date.today() + timedelta(days=1)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.correo, p.planta_nom, c.tipo_cuidado, c.prox_fecha
            FROM cuidado_programado c
            JOIN planta p ON p.planta_id = c.planta_id
            JOIN usuario u ON u.id_usuario = p.id_usuario
            WHERE c.prox_fecha = %s
        """, [mañana])
        notificaciones = cursor.fetchall()

    for correo, planta, tipo_cuidado, fecha in notificaciones:
        asunto = f"Recordatorio de cuidado: {tipo_cuidado} para {planta}"
        mensaje = (
            f"Hola 🌱\n\n"
            f"Recuerda que mañana ({fecha}) debes realizar el siguiente cuidado para tu planta:\n"
            f"- Planta: {planta}\n"
            f"- Cuidado: {tipo_cuidado}\n\n"
            f"¡MidoriFy te ayuda a mantener tus plantas felices! 💚"
        )
        send_mail(
            asunto,
            mensaje,
            'erikatorrestd@gmail.com',     # Remitente
            [correo],                 # Destinatario
            fail_silently=False,
        )
