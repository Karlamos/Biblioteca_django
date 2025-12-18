from django.test import TestCase
from gestion.models import Autor, Libro, Prestamo
from django.contrib.auth.models import User
from django.utils import timezone

class LibroModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        autor = Autor.objects.create(nombre="Issac", apellido="Asimov", bibliografia="hola amigos de youttubeeeee...")
        Libro.objects.create(titulo="hola",autor=autor, disponible=True)
        
    def test_str_devuelve_titulo(self):
        libro = Libro.objects.get(id=1)
        self.assertEqual(str(libro), 'hola')
        

class PrestamoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        autor = Autor.objects.create(nombre="Issac", apellido="Asimov", bibliografia="hola amigos de youttubeeeee...")
        usuario = User.objects.create(username='Juan', password='#123Uyqwe')
        libro = Libro.objects.create(titulo="Chao",autor=autor, disponible=False)  
        cls.prestamo = Prestamo.objects.create(libro=libro, usuario=usuario, fecha_max ='2025-12-18')
        
        
    def test_libro_no_disponible(self):
        self.prestamo.refresh_from_db()
        self.assertFalse(self.prestamo.libro.disponible)
        self.assertEqual(self.prestamo.dias_retraso, 8)
        if self.prestamo.dias_retraso > 0:
            self.assertGreater(self.prestamo.multa_retraso, 0)
        