from django.test import TestCase
from unittest.mock import patch, PropertyMock, MagicMock
from api.galaxies.models import Galaxy
from unittest.mock import Mock
from api.users.models import User, PointsDistribution, Attribute
from api.planets.models import Creature, Planet, Phase, Hint, Question, Alternative
from api.game.models import Game
from django.core.exceptions import ValidationError


class GalaxyModelMockTest(TestCase):

    @patch('api.galaxies.models.Galaxy.image', new_callable=PropertyMock)  
    def test_galaxy_image_mock(self, mock_image):
        # Simula um comportamento para o campo de imagem
        mock_image.return_value = 'galaxies/mock_image.jpg'
        
        # Criação de uma instância de Galaxy
        galaxy = Galaxy(name='Via Lactea')
        
     
        self.assertEqual(galaxy.name, 'Via Lactea')
        self.assertEqual(galaxy.image, 'galaxies/mock_image.jpg')  
        self.assertIsNone(galaxy.uploaded_at)  # Como não foi salvo, deve ser None

    @patch('api.galaxies.models.Galaxy.image', new_callable=PropertyMock)  # Usando PropertyMock
    def test_galaxy_str_mock(self, mock_image):
        # Simula um comportamento para o campo de imagem
        mock_image.return_value = 'galaxies/mock_image.jpg'

        # Criação de uma instância de Galaxy
        galaxy = Galaxy(name='Andromeda')

       
        self.assertEqual(str(galaxy), 'Andromeda')
        
class GameModelTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            name="Wiry Gomes",
            email="wiryssongomes@gmail.com",
            password="wiry123"
        )
        self.phase = Phase.objects.create(name="Test Phase")

       
        self.game = Game.objects.create(
            user=self.user,
            phase=self.phase,
            creature_life=10,
            creature_attack=1
        )

    def test_check_game_status(self):
        # Simulando a derrota do usuário
        self.game.user_life = 0  
        self.game.creature_life = 10  
        self.game.check_game_status()  

        # Verifica se o status muda para 'L' (derrota)
        self.assertEqual(self.game.status, 'L')  # O status deve ser 'L' para derrota

        # Simulando a vitória
        self.game.user_life = 3  
        self.game.creature_life = 0  
        self.game.check_game_status()  

        # Verifica se o status muda para 'W' (vitória)
        self.assertEqual(self.game.status, 'W')  # O status deve ser 'W' para vitória
        
    def test_initialize_game(self):
        self.game.initialize_game()
    
        self.assertEqual(self.game.user_life, 3)
        self.assertEqual(self.game.user_attack, 1)
        self.assertEqual(self.game.creature_life, 10)
        self.assertEqual(self.game.creature_attack, 1)


class CreatureTestCase(TestCase):
    def setUp(self):
        """Configura uma instância de Creature chamada 'Dragon' para os testes."""
        self.creature = Creature(name='Dragon')

    def test_get_image_path_with_image(self):
        """Testa o método get_image_path quando uma imagem está definida."""
        self.creature.image = 'creatures/dragon.png'
        expected_path = 'creatures/dragon.png'
        self.assertEqual(self.creature.get_image_path(), expected_path)

class PlanetTestCase(TestCase):
    def setUp(self):
        """Configura uma instância de Planet chamada 'Terra' para os testes."""
        self.planet = Planet(name='Terra')

    def test_str_method(self):
        """Testa o método __str__ para retornar o nome do planeta."""
        self.assertEqual(str(self.planet), 'Terra')

class PhaseTestCase(TestCase):
    def setUp(self):
        """Configura uma instância de Phase chamada 'Primeira Fase' para os testes."""
        self.phase = Phase(name='Primeira Fase')

    def test_str_method(self):
        """Testa o método __str__ para retornar o nome da fase."""
        self.assertEqual(str(self.phase), 'Primeira Fase')

class HintTestCase(TestCase):
    def setUp(self):
        """Configura uma instância de Hint com um texto de dica para os testes."""
        self.hint = Hint(hintText='Esta é uma dica.')

    def test_str_method(self):
        """Testa o método __str__ para retornar o texto da dica."""
        self.assertEqual(str(self.hint), 'Esta é uma dica.')

class QuestionTestCase(TestCase):
    def setUp(self):
        """Configura uma instância de Question com um texto de pergunta para os testes."""
        self.question = Question(questionText='Qual é a capital da França?')

    def test_str_method(self):
        """Testa o método __str__ para retornar o texto da pergunta."""
        self.assertEqual(str(self.question), 'Qual é a capital da França?')

class AlternativeTestCase(TestCase):
    def setUp(self):
        """Configura uma instância de Alternative com um texto de alternativa para os testes."""
        self.alternativa = Alternative(alternativeText='Paris', is_correct=True)

    def test_str_method(self):
        """Testa o método __str__ para retornar o texto da alternativa."""
        self.assertEqual(str(self.alternativa), 'Paris')
        
class UserModelTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            name="Wiry",
            email="wiry@example.com",
            password="wiry123"
        )
        self.user.attributes = Attribute.objects.create(life=3, attack=1)
        self.user.save()

    def test_create_user(self):
        # Testa se o usuário é criado corretamente
        user = User.objects.get(email="wiry@example.com")
        self.assertEqual(user.name, "Wiry")
        self.assertEqual(user.email, "wiry@example.com")
        self.assertEqual(user.attributes.life, 3)

    def test_points_distribution(self):
        # Atribuir pontos ao usuário antes da distribuição
        self.user.points = 5  # Defina um valor total de pontos
        
        # Criar uma distribuição de pontos
        points_distribution = PointsDistribution(user=self.user, life_points=2, attack_points=1)
        
        # Salvar a distribuição
        points_distribution.save()
        
        # Verificar se os atributos do usuário foram atualizados
        self.assertEqual(self.user.attributes.life, 5)  # 3 + 2
        self.assertEqual(self.user.attributes.attack, 2)  # 1 + 1
