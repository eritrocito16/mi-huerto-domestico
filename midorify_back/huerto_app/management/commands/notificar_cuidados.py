from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import connection
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Envía notificaciones por correo de cuidados programados para mañana'

    def handle(self, *args, **kwargs):
        manana = date.today() + timedelta(days=1)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.correo, p.planta_nom, c.tipo_cuidado, c.prox_fecha
                FROM cuidado_programado c
                JOIN planta p ON p.planta_id = c.planta_id
                JOIN usuario u ON u.id_usuario = p.id_usuario
                WHERE c.prox_fecha = %s
            """, [manana])
            notificaciones = cursor.fetchall()

        if not notificaciones:
            self.stdout.write(self.style.WARNING('No hay cuidados programados para mañana.'))
            return

        for correo, planta, tipo_cuidado, fecha in notificaciones:
            asunto = f"🌿 Recordatorio: {tipo_cuidado} para tu planta {planta}"
            mensaje = (
                f"Hola 🌱,\n\n"
                f"Este es un recordatorio de MidoriFy:\n"
                f"Mañana ({fecha}) debes realizar el siguiente cuidado:\n"
                f"- Planta: {planta}\n"
                f"- Cuidado: {tipo_cuidado}\n\n"
                f"¡No olvides cuidar tus plantas! 💚"
            )

            # Buscar el ID del cuidado para el botón
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id
                    FROM cuidado_programado c
                    JOIN planta p ON p.planta_id = c.planta_id
                    JOIN usuario u ON u.id_usuario = p.id_usuario
                    WHERE u.correo = %s AND p.planta_nom = %s AND c.tipo_cuidado = %s AND c.prox_fecha = %s
                """, [correo, planta, tipo_cuidado, fecha])
                row = cursor.fetchone()

            if not row:
                continue

            cuidado_id = row[0]

            mensaje_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #2f6e4e;">
                <p>Hola 🌱,</p>

                <p>Este es un recordatorio de <strong>MidoriFy</strong>:<br>
                Mañana (<strong>{fecha}</strong>) debes realizar el siguiente cuidado:</p>

                <ul>
                    <li><strong>Planta:</strong> {planta}</li>
                    <li><strong>Cuidado:</strong> {tipo_cuidado}</li>
                </ul>

                <p>
                    <a href="http://localhost:8000/confirmar_cuidado/?id={cuidado_id}"
                       style="padding: 10px 15px; background-color: #2f6e4e; color: white; 
                              text-decoration: none; border-radius: 6px; font-weight: bold;">
                        ✅ Ya lo hice
                    </a>
                </p>

                <p>¡No olvides cuidar tus plantas! 💚</p>
            </body>
            </html>
            """

            send_mail(
                asunto,
                mensaje,
                'midorify.plantas@gmail.com',
                [correo],
                fail_silently=False,
                html_message=mensaje_html
            )

        self.stdout.write(self.style.SUCCESS('✅ Correos de notificación enviados correctamente.'))
