from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Autor,Libro,Prestamo,multa
from django.conf import settings

def index(request):
    title = settings.TITLE
    return render(request,'gestion/templates/home.html', {'titulo':title})

def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'gestion/templates/libros.html', {'libros':libros})

def crear_libro(request):
    autores = Autor.objects.all()
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        autor_id = request.POST.get('autor')
        if titulo and autor_id:
            autor = get_object_or_404(Autor,id=autor_id)
            Libro.objects.create(titulo=titulo, autor=autor)
            return redirect('lista_libros')
    return render(request, 'gestion/templates/crear_libros.html',{'autores':autores})

def lista_autores(request):
    autores =Autor.objects.all()
    return render(request, 'gestion/templates/autores.html',{'autores': autores})

def crear_autores(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        Autor.objects.create(nombre=nombre, apellido=apellido, bibliografia=bibliografia)
        return redirect(lista_autores)
    return render(request,'gestion/templates/crear_autores.html',)

def lista_prestamos(request):
    prestamos =Prestamo.objects.all()
    return render(request, 'gestion/templates/prestamos.html',{'prestamos': prestamos}) 

def crear_prestamos(request):
    libro = Libro.objects.all()
    if request.method == 'POST':
        libro_id= request.POST.get('titulo')
        usuario_id = request.POST.get('usuario')
        fecha_prestamos = request.POST.get('fecha_prestamos')
        fecha_max = request.POST.get('fecha_max')
        fecha_devol = request.POST.get('fecha_devol')
        if libro_id and usuario_id:
            libro = get_object_or_404(Libro, id=libro_id)
            usuario=get_object_or_404(User, id=usuario_id)
            Prestamo.objects.create(libro=libro,usuario=usuario,fecha_prestamos=fecha_prestamos,fecha_max=fecha_max,fecha_devol=fecha_devol)
            return redirect('lista_prestamos')
        
    return render(request,'gestion/templates/crear_prestamos.html',)

def detalle_prestamo(request):
    pass

def lista_multa(request):
    multas =multa.objects.all()
    return render(request, 'gestion/templates/multa.html',{'multas': multas})

def crear_multa(request):
    pass



# Create your views here.
