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
    pass

def crear_libro(request):
    pass

def lista_autores(request):
    autores =Autor.objects.all()
    return render(request, 'gestion/templates/autores.html',{'autores': autores})

def crear_autores(request):
    pass

def lista_prestamos(request):
    pass

def crear_prestamos(request):
    pass

def detalle_prestamo(request):
    pass

def lista_multa(request):
    pass

def crear_multa(request):
    pass



# Create your views here.
