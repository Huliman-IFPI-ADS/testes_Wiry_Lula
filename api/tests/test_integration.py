from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserRegistrationTest(APITestCase):

    def setUp(self):
        self.register_url = reverse('cadastro')

    def test_register_user_success(self):
        register_data = {
            'name': 'Wirysson Gomes',
            'email': 'wiryssongomes@gmail.com',
            'password': 'wiry123',
            'crew': 'halley',
        }

        # Envia uma solicitação POST para o endpoint de registro
        response = self.client.post(self.register_url, register_data)

        # Verifica se a resposta foi bem-sucedida (201 CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se o usuário foi criado no banco de dados
        user = get_user_model().objects.get(email='wiryssongomes@gmail.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'wiryssongomes')  
        self.assertEqual(user.crew, 'halley')
    def test_user_name_is_lowercase(self):
        register_data = {
            'name': 'Wirysson Gomes',
            'email': 'wiryssongomes2@gmail.com',
            'password': 'wiry123',
            'crew': 'halley',
        }

        # Envia uma solicitação POST para o endpoint de registro
        self.client.post(self.register_url, register_data)

        # Verifica se o usuário foi criado no banco de dados
        user = get_user_model().objects.get(email='wiryssongomes2@gmail.com')
        self.assertEqual(user.name, 'wiryssongomes')  

    def test_register_user_missing_field(self):
        # Tentando criar um usuário sem o campo "email"
        invalid_data = {
            'name': 'Wirysson Gomes',
            'password': 'wiry123',
            'crew': 'halley',
        }

        response = self.client.post(self.register_url, invalid_data)

        # Verifica se a resposta indica erro de campo obrigatório (400 BAD REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLoginTestNoToken(APITestCase):

    def test_login_success(self):
        register_data = {
            'name': 'Wirysson Gomes',
            'email': 'wiryssongomes@gmail.com',
            'password': 'wiry123',
            'crew': 'halley', 
        }
        self.client.post(reverse('cadastro'), register_data)

        # Agora, tentamos fazer login
        url = reverse('token_obtain_pair')  
        
        login_data = {
            'username_or_email': 'wiryssongomes@gmail.com',
            'password': 'wiry123'
        }
        
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_failure(self):
        register_data = {
            'name': 'Wirysson Gomes',
            'email': 'wiryssongomes@gmail.com',
            'password': 'wiry123',
            'crew': 'halley',  
        }
        self.client.post(reverse('cadastro'), register_data)

        # Tentando fazer login com senha errada
        url = reverse('token_obtain_pair')
        
        invalid_data = {
            'username_or_email': 'wiryssongomes@gmail.com',
            'password': 'wiryzada'
        }
        
        response = self.client.post(url, invalid_data)
        
        # Verificamos que credenciais inválidas retornam 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
