
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.inicio, name='index'),
    path('programas/admin', views.programa_admin, name='programas/admin'),
    path('programas/alumno', views.programa_alumno, name='programa/alumno'),
    path('programas/', views.gestionar_programas, name='gestionar_programas'),
    path('login/', views.login, name='login'),
    path('programas/alumno/<int:id>/', views.detalle_programa, name='detalle_programa'),
    path('postulaciones/', views.listar_postulaciones, name='listar_postulaciones'),
    path('postulaciones/<int:id>/<str:accion>/', views.gestionar_postulacion, name='gestionar_postulacion'),
    path('perfil/', views.perfil_alumno, name='perfil_alumno'),
    path('registro/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)