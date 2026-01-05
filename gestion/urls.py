from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", index, name="index"),
    
    #gestion Usuarios
    path('login/',auth_views.LoginView.as_view(), name='login'),
    path('logout',auth_views.LogoutView.as_view(next_page='login'), name="logout"),
    
    #cambio de contraseña
    path('password/change', auth_views.PasswordChangeView.as_view(),name="password_change"),
    path('password/change/done', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    
    #registro
    path('registro/', registro, name="registro"),
    
    #libros
    path('libros/', lista_libros, name="lista_libros"),
    path('libros/nuevo/', crear_libro, name="crear_libro"),
    path('buscar-api/',buscar_libro_api, name='buscar_libro_api'),
    
    #autores
    path('autores/', lista_autores, name="lista_autores"),
    path('autores/nuevo/', crear_autores, name="crear_autores"),
    path('autores/<int:id>/editar/', crear_autores, name='editar_autores'),
    
    #prestamo
    path('prestamos/', lista_prestamos, name="lista_prestamos"),
    path('prestamos/nuevo/', crear_prestamos, name="crear_prestamos"),
    path('prestamos/<int:id>/devolver/',devolver_prestamo,name='devolver_prestamo'),
    
    #multas
    path('multas/', lista_multa, name="lista_multa"),
    path('multas/nuevo/', crear_multa, name="crear_multa"),
    path('multas/nuevo/<int:prestamo_id>', crear_multa, name="crear_multa"),
    path('prestamo/<int:id>/multar/', crear_multa, name='crear_multa'),
        path('multas/<int:multa_id>/pagar/', liquidar_multa, name='liquidar_multa'),

    
    #path con classview
    path('libros_view/', LibroListView.as_view(), name="libros_view"),

]