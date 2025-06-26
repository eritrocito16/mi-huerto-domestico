from django.urls import path, include
from rest_framework.routers import DefaultRouter
from huerto_app.api.views import UsuarioViewSet  # ✅ import corregido

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('', include(router.urls)),
]

