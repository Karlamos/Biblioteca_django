from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from .models import Autor,Libro,Prestamo,multa
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import ListView, CreateView, UpdateView,DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin,AccessMixin
from django.urls import reverse_lazy
import requests
from django.http import JsonResponse
from datetime import timedelta
from .forms import CustomUserCreationForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
#pip install reportlab

from django.core.exceptions import PermissionDenied

#reporte#
def generar_pdf_prestamo(prestamo):
    # Crear el objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprobante_{prestamo.id}.pdf"'

    # Crear el objeto PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Dibujar la información
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "RECIBO DE PRÉSTAMO DE LIBRO")
    
    p.setFont("Helvetica", 12)
    p.line(100, height - 110, 500, height - 110)
    
    y = height - 140
    datos = [
        f"ID Préstamo: {prestamo.id}",
        f"Usuario: {prestamo.usuario.get_full_name() or prestamo.usuario.username}",
        f"Libro: {prestamo.libro.titulo}",
        f"ISBN: {prestamo.libro.isbn}",
        f"Fecha de Préstamo: {prestamo.fecha_prestamos}",
        f"Fecha Máxima de Devolución: {prestamo.fecha_max}",
    ]

    for dato in datos:
        p.drawString(100, y, dato)
        y -= 25

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, y - 40, "Gracias por utilizar nuestra biblioteca. Por favor, cuide el material.")

    # Cerrar el PDF
    p.showPage()
    p.save()
    return response

@login_required
def descargar_recibo_pdf(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    # Opcional: Validar que solo el dueño o un bibliotecario pueda descargarlo
    return generar_pdf_prestamo(prestamo)






#grupos#
class GrupoRequiredMixin(AccessMixin):
    """Requerir grupo específico"""
    group_name = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name=self.group_name).exists():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class SoloMisObjetosMixin:
    """Filtra solo objetos del usuario logueado"""
    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)
    
    
    
    
    

#api openlibrary#
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









#libros
def lista_libros(request):
    libros = Libro.objects.all().order_by('-id') 
    return render(request, 'gestion/templates/libros.html', {'libros': libros})
def crear_libro(request):
    autores = Autor.objects.all()
    es_bodeguero = request.user.groups.filter(name='Bodeguero').exists()
    es_admin = request.user.groups.filter(name='Admin').exists()
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        nombre_autor_api = request.POST.get('autor_api')    
        isbn_dato = request.POST.get('isbn_api')
        stock_valor = 0
        if es_bodeguero or es_admin:
            stock_valor = request.POST.get('stock', 0)
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
                stock=stock_valor,
                disponible=True
            )
            return redirect('lista_libros') 

    return render(request, 'gestion/templates/crear_libros.html', {'autores': autores, 'es_bodeguero': (es_bodeguero or es_admin)})

def editar_libro(request, libro_id):

    libro = get_object_or_404(Libro, id=libro_id)
    autores = Autor.objects.all()
    

    es_autorizado = request.user.groups.filter(name='Bodeguero').exists() or request.user.is_superuser

    if request.method == 'POST':

        if not es_autorizado:
            return redirect('lista_libros')


        libro.titulo = request.POST.get('titulo')
        libro.isbn = request.POST.get('isbn_api')
        libro.anio_publicacion = request.POST.get('anio_api')
        libro.descripcion = request.POST.get('descripcion')
        

        nuevo_stock = request.POST.get('stock')
        if nuevo_stock is not None:
            libro.stock = nuevo_stock
        

        libro.save()
        return redirect('lista_libros')

    return render(request, 'gestion/templates/editar_libro.html', {
        'libro': libro,
        'autores': autores,
        'es_autorizado': es_autorizado
    })






#idk#
class LibroListView(LoginRequiredMixin, ListView):  
    model = Libro
    template_name = 'gestion/templates/libros_view.html'
    context_object_name= 'libros'
    paginate_by= 10 

class LibroCreateView(LoginRequiredMixin, GrupoRequiredMixin, PermissionRequiredMixin, CreateView):
    group_name = 'Bodeguero'  
    permission_required = 'gestion.add_libro'

class LibroUpdateView(LoginRequiredMixin, GrupoRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Libro
    fields=['titulo','autor','anio_publicacion','stock', 'disponible','descripcion']
    template_name = 'gestion/templates/editar_libro.html'
    success_url= reverse_lazy('lista_libros')
    group_name = 'Bodeguero'   
    permission_required = 'gestion.change_libro'

class LibroDeleteView(LoginRequiredMixin, GrupoRequiredMixin, PermissionRequiredMixin, DeleteView):
    group_name = 'Bodeguero'  
    permission_required = 'gestion.delete_libro'


class AutorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Autor
    fields = ['nombre', 'apellido', 'bibliografia']
    template_name = 'gestion/templates/crear_autor.html'
    permission_required = 'gestion.add_autor' 

class PrestamoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Prestamo
    fields = ['libro', 'usuario', 'fecha_devolucion_esperada']
    template_name = 'gestion/templates/crear_prestamo.html'
    permission_required = 'gestion.add_prestamo'
    
def index(request):
    title = settings.TITLE
    return render(request,'gestion/templates/home.html', {'titulo':title})









#autores#
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
    if not request.user.groups.filter(name__in=['Bodeguero', 'Admin']).exists():
        return HttpResponseForbidden()  # ← AGREGADO
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








#prestamo#
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


@login_required
def crear_prestamos(request):

    if not (request.user.has_perm('gestion.gestionar_prestamos') or 
            request.user.groups.filter(name='Bibliotecario').exists() or 
            request.user.is_superuser):  # ← MEJORADO
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

@login_required
def devolver_prestamo(request, id):
    if not request.user.groups.filter(name='Bibliotecario').exists():
        return HttpResponseForbidden()  # ← AGREGADO
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
@permission_required('gestion.change_prestamo', raise_exception=True)
def aprobar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    prestamo.estado = 'Aprobado'
    prestamo.save()
    return redirect('lista_prestamos')





#multas#
def lista_multa(request):
    multas =multa.objects.all()
    return render(request, 'gestion/templates/multa.html',{'multas': multas})


@login_required
def crear_multa(request,id):
    if not request.user.groups.filter(name='Bibliotecario').exists():
        return HttpResponseForbidden()  # ← AGREGADO
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

@login_required
def liquidar_multa(request, multa_id):
    multa_obj = get_object_or_404(multa, id=multa_id)
    

    es_bibliotecario = request.user.groups.filter(name='Bibliotecario').exists()
    es_bodeguero = request.user.groups.filter(name='Bodeguero').exists()
    
    if not (es_bibliotecario or es_bodeguero or request.user.is_superuser):
        if multa_obj.prestamo.usuario != request.user:
            raise PermissionDenied("No puedes pagar una multa que no te pertenece.")

    multa_obj.pagada = True
    multa_obj.save()

    prestamo = multa_obj.prestamo
    if not prestamo.multas.filter(pagada=False).exists():
        prestamo.estado = "Devuelto"
        prestamo.save()

    return redirect('lista_prestamos')  
    
    
    
    
    
    
    
    
    
#registro#   
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
        


from django.contrib.auth.models import Group

def registro_superusuario(request):
    if request.method == 'POST':
        # 1. Creamos la instancia del formulario con los datos del POST
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            # 2. Guardamos el usuario (sin enviarlo a la BD aún para editar campos extra si hace falta)
            user = form.save()
            
            # 3. Obtenemos el rol desde el formulario (limpio y validado)
            rol_nombre = form.cleaned_data.get('role')
            
            if rol_nombre:
                try:
                    # Buscamos el grupo en la BD (asegúrate de que el nombre coincida)
                    # Nota: los nombres de grupos suelen capitalizarse: 'Admin', 'Bibliotecario'
                    grupo = Group.objects.get(name=rol_nombre.capitalize())
                    user.groups.add(grupo)
                    
                    # 4. Si es admin, le damos acceso al panel de administración
                    if rol_nombre.lower() == 'admin':
                        user.is_staff = True
                        user.save()
                        
                except Group.DoesNotExist:
                    print(f"Error: El grupo '{rol_nombre}' no existe en la base de datos.")
            
            return redirect('index')
    else:
        # Usamos el formulario personalizado para la carga inicial
        form = CustomUserCreationForm()
        
    return render(request, 'gestion/templates/registration/registro_superusuario.html', {'form': form})
    
    