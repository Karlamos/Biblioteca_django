from django.test import TestCase
from gestion.models import Autor, Libro, Prestamo, multa
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta


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
        fecha_vencida = timezone.now().date() - timedelta(days=8)
        
        cls.prestamo = Prestamo.objects.create(
            libro=libro, 
            usuario=usuario, 
            fecha_max=fecha_vencida
        )
        
        
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

        resp = self.client.get(reverse('crear_autores'))
        self.assertEqual(resp.status_code, 302)
        
    def test_carga_login(self):

        esta_logueado = self.client.login(username="u1", password='test12345')
        self.assertTrue(esta_logueado) 
        respuesta_pag = self.client.get(reverse('crear_autores'))
        self.assertEqual(respuesta_pag.status_code, 200)

class MultaModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.autor = Autor.objects.create(nombre="Test", apellido="Autor")
        cls.libro = Libro.objects.create(titulo="Libro Test", autor=cls.autor)
        cls.usuario = User.objects.create_user(username='tester', password='password123')
        
        hoy = timezone.now().date()
        fecha_vencimiento = hoy - timedelta(days=10)
        cls.prestamo = Prestamo.objects.create(
            libro=cls.libro, 
            usuario=cls.usuario, 
            fecha_max=fecha_vencimiento
        )

    def test_calculo_automatico_monto_retraso(self):
        nueva_multa = multa.objects.create(prestamo=self.prestamo, tipo='r')
        self.assertEqual(self.prestamo.dias_retraso, 10)
        self.assertEqual(float(nueva_multa.monto), 5.00)

    def test_monto_fijo_perdida(self):
        multa_perdida = multa.objects.create(prestamo=self.prestamo, tipo='p')
        self.assertEqual(float(multa_perdida.monto), 20.00)

class DevolucionMultaViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bibliotecario', password='password123')
        self.autor = Autor.objects.create(nombre="Autor", apellido="Pruebas")
        self.libro = Libro.objects.create(titulo="Libro a devolver", autor=self.autor, disponible=False)
    
        vencimiento = timezone.now().date() - timedelta(days=5)
        self.prestamo = Prestamo.objects.create(
            libro=self.libro, 
            usuario=self.user, 
            fecha_max=vencimiento
        )

    def test_creacion_multa_al_devolver(self):
        self.client.login(username='bibliotecario', password='password123')

        response = self.client.get(reverse('devolver_prestamo', args=[self.prestamo.id]))
        
        self.assertRedirects(response, reverse('lista_prestamos'))
        
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)
        
        existe_multa = multa.objects.filter(prestamo=self.prestamo, tipo='r').exists()
        self.assertTrue(existe_multa)
        
        m_obj = multa.objects.get(prestamo=self.prestamo)
        self.assertEqual(float(m_obj.monto), 2.50) 