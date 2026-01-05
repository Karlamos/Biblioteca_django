from django.urls import reverse
from django.test import TestCase
from gestion.models import Libro,Autor
from unittest.mock import patch

class LibroApiTest(TestCase):

    @patch('requests.get')  # "Simula" el método requests.get
    def test_buscar_libro_api_exito(self, mock_get):
        # Configuramos la respuesta falsa que dará el mock
        mock_get.return_value.json.return_value = {
            'docs': [{
                'author_name': ['Isaac Asimov'],
                'first_publish_year': 1951,
                'isbn': ['123456789'],
                'subject': ['Science Fiction', 'Adventure']
            }]
        }

        # Ejecutamos la petición a nuestra vista
        url = reverse('buscar_libro_api') + "?titulo=Fundacion"
        response = self.client.get(url)

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['autor'], 'Isaac Asimov')
        self.assertEqual(data['isbn'], '123456789')

class CrearLibroApiTest(TestCase):

    def test_crear_libro_con_datos_api(self):
        # Datos que simulan lo que enviaría tu formulario desde el frontend
        datos_post = {
            'titulo': 'El fin de la eternidad',
            'autor_api': 'Isaac Asimov', # Nombre que viene de la API
            'isbn_api': '987654321',
            'anio_api': '1955',
            'genero_api': 'Sci-Fi'
        }

        # Ejecutamos el POST
        response = self.client.post(reverse('crear_libro'), datos_post)

        # 1. Verificar redirección a la lista de libros
        self.assertRedirects(response, reverse('lista_libros'))

        # 2. Verificar que el Autor se creó correctamente
        from gestion.models import Autor, Libro
        self.assertTrue(Autor.objects.filter(nombre="Isaac", apellido="Asimov").exists())

        # 3. Verificar que el Libro se guardó con los datos correctos
        libro = Libro.objects.get(titulo='El fin de la eternidad')
        self.assertEqual(libro.isbn, '987654321')
        self.assertEqual(libro.autor.nombre, 'Isaac')

class ListaLibroViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        autor = Autor.objects.create(nombre="autorr", apellido="libro", bibliografia="asasa")
        for i in range(3):
            Libro.objects.create(titulo=f"Chao {i}",autor=autor, disponible=True)  
            
            
    def test_url_existencias(self):
        resp = self.client.get(reverse('lista_libros'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'gestion/templates/libros.html')
        self.assertEqual(len(resp.context['libros']), 3)
        
