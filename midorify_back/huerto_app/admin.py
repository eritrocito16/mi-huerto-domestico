from django.contrib import admin
from .models import Usuario, Planta, CuidadoProgramado, Historial, Notificacion  # importa tu modelo

admin.site.register(Usuario)  # lo registras en el panel admin

admin.site.register(Planta)
admin.site.register(CuidadoProgramado) 
admin.site.register(Historial) 
admin.site.register(Notificacion)

# Register your models here.
