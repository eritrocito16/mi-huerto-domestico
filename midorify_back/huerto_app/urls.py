from django.urls import path
from .views import login_view, mis_plantas_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('mis-plantas/', mis_plantas_view, name='mis_plantas'),
]
