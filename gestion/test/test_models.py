from django.test import TestCase
from gestion.models import Autor, Libro, Prestamo
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


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
        
        
class PrestamoUsuarioViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('u1', password='test12345')
        self.user2 = User.objects.create_user('u2', password='test12345')
        
    def test_redirige_no_login(self):
        resp = self.client.get(reverse('crear_autor'))
        self.assertEqual(resp.status_code, 302)
        
    def test_carga_login(self):
        resp= self.client.login(username="u1", password='test12345')
        self.assertEqual(resp.status_code, 200)
        resp1=self.client.get(reverse('crear_autores'))
        self.assertEqual(resp1.status_code, 200)