from django.db import models

# ----------------------------
# Modelo de Usuario
# ----------------------------
from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)  # 🟢 Clave primaria real
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField()  # 🟡 Se quita auto_now_add, ya lo maneja MySQL

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False  # 🔒 No dejar que Django intente crear/modificar la tabla
        db_table = 'usuario'





# ----------------------------
# Modelo de Planta
# ----------------------------
class Planta(models.Model):
    planta_id = models.AutoField(primary_key=True)  # 👈 Define la PK correcta
    id_usuario = models.ForeignKey('Usuario', db_column='id_usuario', on_delete=models.CASCADE)
    planta_nom = models.CharField(max_length=100)
    tipo_planta = models.CharField(max_length=50, null=True, blank=True)
    cuidados = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.planta_nom

    class Meta:
        managed = False
        db_table = 'planta'



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
    prox_fecha = models.DateField()  # próxima vez que debe hacerse
    detalles = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo_cuidado} - {self.planta.planta_nom}"
    
    class Meta:
        managed = False  # 👈 Esto debe estar bien indentado
        db_table = 'cuidado_programado'


# ----------------------------
# Historial de acciones realizadas
# ----------------------------
class Historial(models.Model):
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
    
    class Meta:
        managed = False  # 👈 Esto debe estar bien indentado
        db_table = 'historial'


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
    
    class Meta:
        managed = False  # 👈 Esto debe estar bien indentado
        db_table = 'notificacion'