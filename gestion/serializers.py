from rest_framework import serializers
from .models import Libro, Autor

class AutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Autor
        fields = ['id', 'nombre', 'apellido', 'nombre_completo']

    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"

class LibroSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.ReadOnlyField(source='autor.nombre')
    autor_apellido = serializers.ReadOnlyField(source='autor.apellido')

    class Meta:
        model = Libro

        fields = [
            'id', 'titulo','autor','autor_nombre', 'autor_apellido', 
            'isbn', 'anio_publicacion', 'descripcion', 'stock', 'disponible','fuente_datos'
        ]