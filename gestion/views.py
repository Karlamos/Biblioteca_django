from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from .models import Autor,Libro,Prestamo,multa
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import ListView, CreateView, UpdateView,DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
import requests
from django.http import JsonResponse
from .models import Autor
from datetime import timedelta
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Libro, Autor,multa


def buscar_libro_api(request):
    titulo = request.GET.get('titulo', '')
    isbn=request.GET.get('isbn_api')
    url = f"https://openlibrary.org/search.json?title={titulo}"
    
    try:
        response = requests.get(url).json()
        if response.get('docs'):
            libro = response['docs'][0]
            
            nombre_completo = libro.get('author_name', ['Autor Desconocido'])[0]
            anio = libro.get('first_publish_year', 'N/A')
            
            lista_isbn = libro.get('isbn', [])
            isbn = lista_isbn[0] if lista_isbn else "No disponible"
            
            return JsonResponse({
                'autor': nombre_completo,
                'anio': anio,
                'isbn': isbn,
                'success': True
            })
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'success': False})

def crear_libro(request):
    autores = Autor.objects.all()
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        nombre_autor_api = request.POST.get('autor_api')    
        isbn_dato = request.POST.get('isbn_api')

        autor_obj = None

        if nombre_autor_api:
            partes = nombre_autor_api.split(' ', 1)
            nom = partes[0]
            ape = partes[1] if len(partes) > 1 else "S/A"

            autor_obj, _ = Autor.objects.get_or_create(nombre=nom, apellido=ape)

        if titulo and autor_obj:
            Libro.objects.create(
                titulo=titulo,
                autor=autor_obj,
                isbn=isbn_dato,
                anio_publicacion=request.POST.get('anio_api'),
                disponible=True
            )
            return redirect('lista_libros') 

    return render(request, 'gestion/templates/crear_libros.html', {'autores': autores})

class LibroListView(LoginRequiredMixin, ListView):
    model = Libro
    template_name = 'gestion/templates/libros_view.html'
    context_object_name= 'libros'
    paginate_by= 10 

class LibroDetalleView(LoginRequiredMixin, DetailView):
    model = Libro
    template_name = 'gestion/templates/detalle_libros.html'
    context_object_name= 'libro'

class LibroCreateView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    model = Libro 
    fields=['titulo','autor','disponible']
    template_name='gestion/templates/crear_libros.html'
    success_url= reverse_lazy('libro_list')
    permission_required='gestion.add_libro'
    
class LibroUpdateView(LoginRequiredMixin,PermissionRequiredMixin,UpdateView):
    model = Libro 
    fields=['titulo','autor']
    template_name='gestion/templates/editar_libros.html'
    success_url= reverse_lazy('libro_list')
    permission_required='gestion.change_libro'
    
class LibroDeleteView(LoginRequiredMixin, PermissionRequiredMixin,DeleteView):
    model = Libro 
    template_name='gestion/templates/delete_libros.html'
    success_url= reverse_lazy('libro_list')
    permission_required='gestion.delete_libro'
    
def index(request):
    title = settings.TITLE
    return render(request,'gestion/templates/home.html', {'titulo':title})

def lista_libros(request):
    libros = Libro.objects.all().order_by('-id') 
    return render(request, 'gestion/templates/libros.html', {'libros': libros})


def editar_autores_old(request, id):
    autor=get_object_or_404(Autor,id=id)
    if request.method == 'POST':
        nombre= request.POST.get('nombre')
        apellido= request.POST.get('apellido')
        bibliografia=request.POST.get('bibliografia')
        
        if nombre and apellido:
            autor.apellido = apellido
            autor.nombre = nombre
            autor.bibliografia = bibliografia
            autor.save()
            return redirect('lista_autores')      
    return render(request, 'gestion/templates/editar_autores.html',{'autor' : autor})  
        
def lista_autores(request):
    autores =Autor.objects.all()
    return render(request, 'gestion/templates/autores.html',{'autores': autores})

@login_required
def crear_autores(request, id=None):
    if id==None:
        autor=None
        modo='Crear'
    else:
        autor=get_object_or_404(Autor,id=id)
        modo='editar'
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        if autor== None:
            Autor.objects.create(nombre=nombre, apellido=apellido, bibliografia=bibliografia)
        else:
            autor.apellido = apellido
            autor.nombre = nombre
            autor.bibliografia = bibliografia
            autor.save()
        return redirect(lista_autores)
    context ={'autor':autor,
              'titulo': 'Editar Autor' if modo == 'editar' else 'Crear Autor',
              'texto_boton':'Guardar cambios' if modo == 'editar' else 'Crear'}
    return render(request,'gestion/templates/crear_autores.html', context)

def lista_prestamos(request):
    prestamos = Prestamo.objects.all().order_by('-id')
    hoy = timezone.now().date()

    for p in prestamos:
        p.estado = "Devuelto" if p.fecha_devol else ("Vencido" if hoy > p.fecha_max else "Vigente")
        p.fecha_prestamo_display = p.fecha_prestamos
        p.fecha_vencimiento_display = p.fecha_max
        p.multa_pendiente = p.multas.filter(pagada=False).exists()
        p.multa_obj = p.multas.filter(pagada=False).first()


    return render(request, 'gestion/templates/prestamos.html', {'prestamos': prestamos})

def crear_prestamos(request):

    if not request.user.has_perm('gestion.gestionar_prestamos'):
        return HttpResponseForbidden()
    
    libros = Libro.objects.filter(disponible=True)
    usuarios = User.objects.all()

    if request.method == 'POST':
        libro_id = request.POST.get('libro') 
        usuario_id = request.POST.get('usuario')
        
        if libro_id and usuario_id:
            libro = get_object_or_404(Libro, id=libro_id)
            usuario = get_object_or_404(User, id=usuario_id)
            
            hoy = timezone.now().date()
            vencimiento = hoy + timedelta(days=8)

            Prestamo.objects.create(
                libro=libro,
                usuario=usuario,
                fecha_prestamos=hoy,
                fecha_max=vencimiento
            )
            libro.disponible = False
            libro.save()


            return redirect('lista_prestamos')
        else:
            print(f"ERROR: Datos incompletos. Libro: {libro_id}, Usuario: {usuario_id}")
    
    return render(request, 'gestion/templates/crear_prestamos.html', {
        'libros': libros, 
        'usuarios': usuarios, 
        'fecha': timezone.now().date()
    })


def lista_multa(request):
    multas =multa.objects.all()
    return render(request, 'gestion/templates/multa.html',{'multas': multas})


@login_required
def devolver_prestamo(request, id):
    prestamo = get_object_or_404(Prestamo, id=id)
    prestamo.fecha_devol = timezone.now().date()
    prestamo.save()

    if prestamo.dias_retraso > 0:
        multa.objects.create(
            prestamo=prestamo,
            tipo='r'
        )

    prestamo.libro.disponible = True
    prestamo.libro.save()

    return redirect('lista_prestamos')


@login_required
def crear_multa(request,id):
   
    prestamo = get_object_or_404(Prestamo, id=id)

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        multa.objects.create(
            prestamo=prestamo,
            tipo=tipo
        )

        return redirect('lista_multa')

    return render(request, 'gestion/templates/multar_prestamo.html', {
        'prestamo': prestamo
    })


def liquidar_multa(request, multa_id):
    multa_obj = get_object_or_404(multa, id=multa_id)
    
    multa_obj.pagada = True
    multa_obj.save()

    prestamo = multa_obj.prestamo
    if not prestamo.multas.filter(pagada=False).exists():
        prestamo.estado = "Devuelto"
        prestamo.save()

    return redirect('lista_prestamos')  
    
    
    
    
    
    
    
def registro(request):
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario=form.save()
            login(request, usuario)
            return redirect('index')
    else:
        form= UserCreationForm()
    return render(request, 'gestion/templates/registration/registro.html', {'form':form})