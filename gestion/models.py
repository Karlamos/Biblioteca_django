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
    titulo = models.CharField(max_length=200) # Más espacio
    autor = models.ForeignKey(Autor, related_name="libros", on_delete=models.PROTECT)
    disponible = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True) # Nuevo
    genero = models.CharField(max_length=100, blank=True, null=True) # Nuevo
    anio_publicacion = models.CharField(max_length=4, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
      return f"{self.titulo}"

class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, related_name="prestamos", on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="PRESTAMOS", on_delete=models.PROTECT)
    fecha_prestamos= models.DateField(default=timezone.now)
    fecha_max= models.DateField()
    fecha_devol=models.DateField(blank=True, null=True)
    
    class Meta:
        permissions =(
            ("Ver_prestamo","Puede ver el prestamo"),
            ("gestionar_prestamos","Puede gestionar prestamos"),
            
        )
    
    def __str__(self):
        return f"prestamo de {self,Libro} a {self.usuario}"
    
    @property
    def dias_retraso(self):
        hoy = timezone.now().date()
        fecha_ref = self.fecha_devol or hoy
        if fecha_ref > self.fecha_max:
            return (fecha_ref - self.fecha_devol).days
        else: 
            return 0
        
    @property
    def multa_retraso(self):
        tarifa = 0.50
        return self.dias_retraso * tarifa
    
class multa(models.Model):
    prestamo = models.ForeignKey(Prestamo, related_name="multas", on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=(('r','retraso'),('p','perdida'),('d','deterioro')))
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagada = models.BooleanField(default=False)
    fecha = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Multa{self.tipo} - {self.monto} - {self.prestamo}"
    def save(self, *args, **kwargs):
        if self.tipo == 'r' and self.monto == 0:
            self.monto = self.prestamo.multa_retaso
        super().save(*args **kwargs)
# Create your models here.
