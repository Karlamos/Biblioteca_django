from django.contrib import admin
from .models import Autor, Libro
# Register your models here.
admin.site.register(Autor)

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'isbn', 'anio_publicacion', 'stock', 'disponible')
    search_fields = ('titulo', 'isbn', 'autor__nombre')