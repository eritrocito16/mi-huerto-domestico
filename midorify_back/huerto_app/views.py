from django.shortcuts import render, redirect
from django.db import connection
from datetime import date, timedelta

# Vista para iniciar sesión
def login_view(request):
    if request.method == "POST":
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SELECT id_usuario, nombre FROM usuario WHERE correo=%s AND password=%s", [correo, password])
            user = cursor.fetchone()

        if user:
            request.session['usuario_id'] = user[0]
            request.session['usuario_nombre'] = user[1]
            return redirect('/dashboard/')  # ✅ Agrega la barra final
        else:
            return render(request, 'login.html', {'error': 'Correo o contraseña incorrectos'})

    return render(request, 'login.html')


# Vista del dashboard
def dashboard_view(request):
    if 'usuario_id' in request.session:
        nombre = request.session.get('usuario_nombre')
        return render(request, 'dashboard.html', {'nombre': nombre})
    else:
        return redirect('/login/')


# Vista de mis plantas
def mis_plantas_view(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')

    usuario_id = request.session['usuario_id']

    if request.method == "POST":
        planta_id = request.POST.get("planta_id")

        with connection.cursor() as cursor:
            # Verificar si ya tiene esa planta
            cursor.execute("""
                SELECT COUNT(*) FROM planta
                WHERE id_usuario = %s AND planta_nom = (
                    SELECT planta_nom FROM planta WHERE planta_id = %s AND id_usuario = 1
                )
            """, [usuario_id, planta_id])
            ya_tiene = cursor.fetchone()[0]

            if not ya_tiene:
                # 1. Copiar la planta desde el catálogo (usuario 1)
                cursor.execute("""
                    INSERT INTO planta (planta_nom, tipo_planta, cuidados, id_usuario)
                    SELECT planta_nom, tipo_planta, cuidados, %s
                    FROM planta
                    WHERE planta_id = %s AND id_usuario = 1
                """, [usuario_id, planta_id])

                # 2. Obtener el nuevo ID de la planta copiada
                cursor.execute("SELECT LAST_INSERT_ID()")
                nueva_planta_id = cursor.fetchone()[0]

                # 3. Copiar cuidados programados desde el catálogo
                cursor.execute("""
                    SELECT tipo_cuidado, frecuen_dias, detalles
                    FROM cuidado_programado
                    WHERE planta_id = %s
                """, [planta_id])
                cuidados = cursor.fetchall()

                hoy = date.today()
                for tipo_cuidado, frecuen_dias, detalles in cuidados:
                    prox_fecha = hoy + timedelta(days=frecuen_dias) # ¡Que la primera fecha sea hoy!
                    print("Copiando:", tipo_cuidado, "Frecuencia:", frecuen_dias, "Próxima fecha:", prox_fecha)
                    cursor.execute("""
                        INSERT INTO cuidado_programado (planta_id, tipo_cuidado, frecuen_dias, prox_fecha, detalles)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [nueva_planta_id, tipo_cuidado, frecuen_dias, prox_fecha, detalles])

    with connection.cursor() as cursor:
        # Plantas que ya tiene el usuario
        cursor.execute("""
            SELECT planta_nom, tipo_planta, cuidados FROM planta
            WHERE id_usuario = %s
        """, [usuario_id])
        plantas_registradas = cursor.fetchall()

        # Plantas del catálogo base (usuario 1)
        cursor.execute("""
            SELECT planta_id, planta_nom FROM planta
            WHERE id_usuario = 1
        """)
        plantas_disponibles = cursor.fetchall()

    return render(request, 'mis_plantas.html', {
        'plantas_registradas': plantas_registradas,
        'plantas_disponibles': plantas_disponibles,
    })


def cuidados_view(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')
    
    usuario_id = request.session['usuario_id']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.planta_nom, c.tipo_cuidado, c.frecuen_dias, c.prox_fecha, c.detalles
            FROM planta p
            JOIN cuidado_programado c ON p.planta_id = c.planta_id
            WHERE p.id_usuario = %s
            ORDER BY c.prox_fecha ASC
        """, [usuario_id])

        cuidados = cursor.fetchall()

    return render(request, 'cuidados.html', {'cuidados': cuidados})




def historial_view(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')

    usuario_id = request.session['usuario_id']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.planta_nom, h.accion, h.comentario, h.fecha_accion
            FROM historial h
            JOIN planta p ON h.planta_id = p.planta_id
            WHERE p.id_usuario = %s
            ORDER BY h.fecha_accion DESC
        """, [usuario_id])
        historial = cursor.fetchall()

    return render(request, 'historial.html', {'historial': historial})

def registro_view(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuario (nombre, correo, password)
                VALUES (%s, %s, %s)
            """, [nombre, correo, password])

        return redirect('/login/')

    return render(request, 'registro.html')

from django.http import HttpResponse
from datetime import datetime

def registrar_cuidado_view(request):
    planta_id = request.GET.get("planta")
    usuario_id = request.GET.get("usuario")
    accion = request.GET.get("accion")
    comentario = request.GET.get("comentario", "")

    if not planta_id or not usuario_id or not accion:
        return HttpResponse("Faltan datos necesarios", status=400)

    with connection.cursor() as cursor:
        # Verificar que la planta realmente pertenezca al usuario
        cursor.execute("""
            SELECT COUNT(*) FROM planta
            WHERE planta_id = %s AND id_usuario = %s
        """, [planta_id, usuario_id])
        valido = cursor.fetchone()[0]

        if valido:
            cursor.execute("""
                INSERT INTO historial (planta_id, accion, comentario, fecha_accion)
                VALUES (%s, %s, %s, %s)
            """, [planta_id, accion, comentario, datetime.now()])
            return HttpResponse("Acción registrada correctamente en el historial ✅")
        else:
            return HttpResponse("No autorizado", status=403)


def confirmar_cuidado_view(request):
    cuidado_id = request.GET.get("id")

    if not cuidado_id:
        return HttpResponse("⚠️ Falta el ID del cuidado")

    with connection.cursor() as cursor:
        # Obtener datos del cuidado y planta
        cursor.execute("""
            SELECT c.planta_id, c.tipo_cuidado, p.planta_nom, p.id_usuario
            FROM cuidado_programado c
            JOIN planta p ON c.planta_id = p.planta_id
            WHERE c.id = %s
        """, [cuidado_id])
        row = cursor.fetchone()

        if not row:
            return HttpResponse("❌ El cuidado no existe")

        planta_id, tipo_cuidado, planta_nom, usuario_id = row

        # 1. Registrar en historial
        cursor.execute("""
            INSERT INTO historial (planta_id, accion, comentario, fecha_accion)
            VALUES (%s, %s, %s, NOW())
        """, [planta_id, tipo_cuidado, f"Confirmado vía correo por usuario {usuario_id}"])

        # 2. Registrar en notificación
        cursor.execute("""
            INSERT INTO notificacion (planta_id, tipo_noti, fecha_envio, enviado, mensaje)
            VALUES (%s, %s, NOW(), TRUE, %s)
        """, [planta_id, tipo_cuidado, f"Se confirmó el cuidado '{tipo_cuidado}' para la planta '{planta_nom}'"])

    return HttpResponse("✅ ¡Gracias! Se registró tu cuidado correctamente.")

def notificaciones_view(request):
    if 'usuario_id' not in request.session:
        return redirect('/login/')

    usuario_id = request.session['usuario_id']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.planta_nom, n.tipo_noti, n.fecha_envio, n.enviado
            FROM notificacion n
            JOIN planta p ON n.planta_id = p.planta_id
            WHERE p.id_usuario = %s
            ORDER BY n.fecha_envio DESC
        """, [usuario_id])
        notificaciones = cursor.fetchall()

    return render(request, 'notificaciones.html', {'notificaciones': notificaciones})

