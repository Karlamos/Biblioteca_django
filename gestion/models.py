from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.

class Autor(models.Model):
    nombre=models.CharField(max_length=50)
    apellido=models.CharField(max_length=50)
    bibliografia = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Libro(models.Model):
    titulo = models.CharField(max_length=200) 
    autor = models.ForeignKey(Autor, related_name="libros", on_delete=models.PROTECT)
    disponible = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True) 
    anio_publicacion = models.CharField(max_length=10, blank=True, null=True) 
    stock = models.PositiveIntegerField(default=0)
    isbn = models.CharField(max_length=20, blank=True, null=True, unique=True) 
    fuente_datos = models.CharField(max_length=50, default='Django')
    def __str__(self):
        return f"{self.titulo} (ISBN: {self.isbn})"
  
    def save(self, *args, **kwargs):
        self.stock = int(self.stock) if self.stock else 0
        self.disponible = self.stock > 0
        super(Libro, self).save(*args, **kwargs)

class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, related_name="prestamos", on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="PRESTAMOS", on_delete=models.PROTECT)
    fecha_prestamos= models.DateField(default=timezone.now)
    fecha_max= models.DateField()
    fecha_devol=models.DateField(blank=True, null=True)
    
    class Meta:
        permissions = [
            ("gestionar_prestamo", "Puede aprobar o denegar préstamos"),
            ("Ver_prestamo", "Puede ver la lista detallada de préstamos"),
        ]
    
    def __str__(self):
        return f"prestamo de {self.libro.titulo} a {self.usuario.username}"
    
    @property
    def dias_retraso(self):
        hoy = timezone.now().date()
        fecha_ref = self.fecha_devol or hoy
        if fecha_ref > self.fecha_max:
            return (fecha_ref - self.fecha_max).days
        else: 
            return 0
        
    @property
    def multa_retraso(self):
        return self.dias_retraso * 0.50
    
class multa(models.Model):
    prestamo = models.ForeignKey(Prestamo, related_name="multas", on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=(('r','retraso'),('p','perdida'),('d','deterioro')))
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagada = models.BooleanField(default=False)
    fecha = models.DateField(default=timezone.now)
    
    class Meta:
        permissions = [
            ("pagar_multa", "Puede registrar el pago de una multa"),
        ]
    def save(self, *args, **kwargs):
        if self.monto == 0:
            if self.tipo == 'r':
                self.monto = self.prestamo.multa_retraso
            elif self.tipo == 'd':
                self.monto = 5.00 
            elif self.tipo == 'p':
                self.monto = 20.00 
        
        super().save(*args, **kwargs)
        
    @property
    def motivo_texto(self):
        return dict(self._meta.get_field('tipo').choices).get(self.tipo)
        
    @property
    def estado(self):
        return "Pagado" if self.pagada else "Pendiente"




from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

@receiver(post_save, sender=User)
def assign_group_permissions(instance, created, **kwargs):
    if created:
        # 1. Caso Súper Usuario
        if instance.is_superuser:
            grupo, _ = Group.objects.get_or_create(name='Admin')
            instance.groups.add(grupo)
        
        # 2. Asignación por el campo 'role' (asumiendo que tu CustomUserCreationForm lo guarda)
        # Si no tienes el campo en el modelo, usamos tu lógica de nombres como respaldo
        role = getattr(instance, 'role', '').lower()
        username = instance.username.lower()

        if role == 'bibliotecario' or 'bibliotecario' in username:
            grupo, _ = Group.objects.get_or_create(name='Bibliotecario')
            instance.groups.add(grupo)
            # Asignar permiso específico
            perm = Permission.objects.filter(codename='gestionar_prestamos').first()
            if perm: instance.user_permissions.add(perm)

        elif role == 'bodeguero' or 'bodeguero' in username:
            grupo, _ = Group.objects.get_or_create(name='Bodeguero')
            instance.groups.add(grupo)

        else:
            # Caso por defecto: Usuario Normal
            grupo, _ = Group.objects.get_or_create(name='Usuario')
            instance.groups.add(grupo)
            perm = Permission.objects.filter(codename='view_prestamo').first()
            if perm: instance.user_permissions.add(perm)

        print(f"Grupos y permisos asignados a {instance.username} OK")