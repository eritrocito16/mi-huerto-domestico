from django.db import models

# ----------------------------
# Modelo de Usuario
# ----------------------------
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # aquí guardarás la contraseña hasheada
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# ----------------------------
# Modelo de Planta
# ----------------------------
class Planta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    planta_nom = models.CharField(max_length=100)
    tipo_planta = models.CharField(max_length=50, blank=True)
    cuidados = models.TextField(blank=True)
    foto_url = models.TextField(
        blank=True
    )  # se guarda la URL de la imagen subida a Supabase
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.planta_nom} ({self.usuario.nombre})"


# ----------------------------
# Cuidados programados
# ----------------------------
class CuidadoProgramado(models.Model):
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE)
    tipo_cuidado = models.CharField(
        max_length=20,
        choices=[
            ("riego", "Riego"),
            ("poda", "Poda"),
            ("fertilización", "Fertilización"),
            ("limpieza", "Limpieza"),
            ("luz", "Luz"),
            ("temperatura", "Temperatura"),
        ],
    )
    frecuen_dias = models.IntegerField()  # cada cuántos días se repite
    prox_fecha = models.DateTimeField()  # próxima vez que debe hacerse
    detalles = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo_cuidado} - {self.planta.planta_nom}"


# ----------------------------
# Historial de acciones realizadas
# ----------------------------
class HistorialAccion(models.Model):
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE)
    accion = models.CharField(
        max_length=20,
        choices=[
            ("riego", "Riego"),
            ("poda", "Poda"),
            ("fertilización", "Fertilización"),
            ("limpieza", "Limpieza"),
            ("luz", "Luz"),
            ("temperatura", "Temperatura"),
        ],
    )
    comentario = models.TextField(blank=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} - {self.planta.planta_nom} ({self.fecha_accion.date()})"


# ----------------------------
# Notificaciones programadas
# ----------------------------
class Notificacion(models.Model):
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE)
    tipo_noti = models.CharField(
        max_length=20,
        choices=[
            ("riego", "Riego"),
            ("poda", "Poda"),
            ("fertilización", "Fertilización"),
            ("limpieza", "Limpieza"),
            ("luz", "Luz"),
            ("temperatura", "Temperatura"),
        ],
    )
    fecha_envio = models.DateTimeField()
    enviado = models.BooleanField(default=False)
    mensaje = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo_noti} - {self.planta.planta_nom} - {'✅' if self.enviado else '⏳'}"