from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import connection
from datetime import date

class Command(BaseCommand):
    help = 'Envía notificaciones de cuidados programados pendientes'

    def handle(self, *args, **kwargs):
        hoy = date.today()

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.correo, p.planta_nom, c.tipo_cuidado, c.detalles
                FROM cuidado_programado c
                JOIN planta p ON c.planta_id = p.planta_id
                JOIN usuario u ON p.id_usuario = u.id_usuario
                WHERE c.prox_fecha = %s
            """, [hoy])
            registros = cursor.fetchall()

        for correo, planta, tipo, detalles in registros:
            asunto = f'Recordatorio: {tipo} de tu planta {planta}'
            mensaje = f'Hola 👋\n\nHoy debes realizar el cuidado: {tipo.upper()} para tu planta "{planta}".\n\nDetalles: {detalles}\n\nRecuerda registrar esta acción luego en MidoriFy 🌿.'

            send_mail(
                asunto,
                mensaje,
                'tucorreo@gmail.com',   # Remitente
                [correo],
                fail_silently=False
            )
        
        self.stdout.write(self.style.SUCCESS('Correos enviados exitosamente'))
