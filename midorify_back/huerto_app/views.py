from django.shortcuts import render, redirect
from django.db import connection

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
                # Copiar la planta base a ese usuario
                cursor.execute("""
                    INSERT INTO planta (planta_nom, tipo_planta, cuidados, id_usuario)
                    SELECT planta_nom, tipo_planta, cuidados, %s
                    FROM planta
                    WHERE planta_id = %s AND id_usuario = 1
                """, [usuario_id, planta_id])

    with connection.cursor() as cursor:
        # Mostrar solo plantas del usuario
        cursor.execute("""
            SELECT planta_nom, tipo_planta, cuidados FROM planta
            WHERE id_usuario = %s
        """, [usuario_id])
        plantas_registradas = cursor.fetchall()

        # Mostrar opciones del catálogo
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
