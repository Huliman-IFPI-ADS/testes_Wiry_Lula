from django.test import TestCase
from api.users.models import User, PointsDistribution, UserStatusRanking
from api.galaxies.models import Galaxy
from api.planets.models import Creature, Planet, Phase, Hint, Question, Alternative
from api.game.models import Game, GameEnd
from django.templatetags.static import static
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch

class GalaxyModelTest(TestCase):

    def setUp(self):
        # Criação de uma galáxia para os testes
        self.galaxy = Galaxy.objects.create(
            name='Via Lactea',
            image='galaxies/galaxyTest.jpg'
        )

    def test_galaxy_creation(self):
        """Testa se a galáxia foi criada corretamente."""
        self.assertEqual(self.galaxy.name, 'Via Lactea')
        self.assertEqual(self.galaxy.image, 'galaxies/galaxyTest.jpg')
        self.assertIsNotNone(self.galaxy.uploaded_at)

    def test_galaxy_str_method(self):
        """Testa o método de string da galáxia."""
        self.assertEqual(str(self.galaxy), 'Via Lactea')

    def test_unique_name_constraint(self):
        """Testa a restrição de unicidade do campo name."""
        Galaxy.objects.create(name='Andromeda', image='galaxies/andromeda.jpg')
        with self.assertRaises(IntegrityError):
            Galaxy.objects.create(name='Andromeda', image='galaxies/another_andromeda.jpg')

    def test_galaxy_default_image(self):
        """Testa se a imagem padrão é atribuída corretamente."""
        galaxy_with_default_image = Galaxy.objects.create(name='Test Galaxy')
        self.assertEqual(galaxy_with_default_image.image, 'galaxies/galaxyTest.jpg')

    def test_verbose_name(self):
        """Testa os nomes descritivos do modelo."""
        self.assertEqual(str(Galaxy._meta.verbose_name), 'galaxy')
        self.assertEqual(str(Galaxy._meta.verbose_name_plural), 'galaxies')

    def test_uploaded_at_field(self):
        """Testa se o campo uploaded_at é preenchido automaticamente."""
        self.assertIsNotNone(self.galaxy.uploaded_at)

    def test_max_length_name(self):
        """Testa a limitação do tamanho máximo do campo name."""
        long_name = 'A' * 101  
        with self.assertRaises(ValidationError):
            galaxy = Galaxy(name=long_name, image='galaxies/long_name.jpg')
            galaxy.full_clean()  # Chama a validação antes de salvar
            
class PlanetModelTest(TestCase):
    """Testes para o modelo Planet."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando uma galáxia e dois planetas."""
        self.galaxy = Galaxy.objects.create(name='Via Lactea')
        self.planet_terra = Planet.objects.create(
            name='Terra',
            description='Planeta natal',
            galaxy=self.galaxy
        )
        self.planet_mars = Planet.objects.create(name='Mars', galaxy=self.galaxy)

    def test_create_planet_terra(self):
        """Testa a criação do planeta Terra."""
        planet = self.planet_terra
        self.assertEqual(planet.name, 'Terra')
        self.assertEqual(planet.description, 'Planeta natal')
        self.assertEqual(planet.galaxy, self.galaxy)

    def test_create_planet_mars(self):
        """Testa a criação do planeta Mars."""
        planet = self.planet_mars
        self.assertEqual(planet.name, 'Mars')
        self.assertEqual(planet.galaxy, self.galaxy)

    def test_planet_str_terra(self):
        """Testa o método __str__ do planeta Terra."""
        self.assertEqual(str(self.planet_terra), 'Terra')

    def test_planet_str_mars(self):
        """Testa o método __str__ do planeta Mars."""
        self.assertEqual(str(self.planet_mars), 'Mars')


class PhaseModelTest(TestCase):
    """Testes para o modelo Phase."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando uma criatura e uma fase."""
        self.creature = Creature.objects.create(name='Dragon')
        self.planet = Planet.objects.create(name='Earth')
        self.phase = Phase.objects.create(
            name='Growth',
            description='The phase of growth.',
            creatures=self.creature,
            planet=self.planet
        )

    def test_str_method(self):
        """Testa o método __str__ da fase."""
        self.assertEqual(str(self.phase), 'Growth')

    def test_foreign_key_relationship(self):
        """Testa as relações de chave estrangeira da fase com criaturas e planetas."""
        self.assertEqual(self.phase.creatures.name, 'Dragon')
        self.assertEqual(self.phase.planet.name, 'Earth')


class HintModelTest(TestCase):
    """Testes para o modelo Hint."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando uma dica."""
        self.hint = Hint.objects.create(hintText='Try again!')

    def test_str_method(self):
        """Testa o método __str__ da dica."""
        self.assertEqual(str(self.hint), 'Try again!')


class QuestionModelTest(TestCase):
    """Testes para o modelo Question."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando uma fase, uma dica e uma pergunta."""
        self.hint = Hint.objects.create(hintText='Try again!')
        self.phase = Phase.objects.create(
            name='Growth',
            description='Growth phase description',
            creatures=Creature.objects.create(name='Dragon'),
            planet=Planet.objects.create(name='Earth')
        )
        self.question = Question.objects.create(
            questionText='What is the growth phase?',
            phase=self.phase,
            hint=self.hint
        )

    def test_str_method(self):
        """Testa o método __str__ da pergunta."""
        self.assertEqual(str(self.question), 'What is the growth phase?')

    def test_foreign_key_relationship(self):
        """Testa as relações de chave estrangeira da pergunta com fase e dica."""
        self.assertEqual(self.question.phase.name, 'Growth')
        self.assertEqual(self.question.hint.hintText, 'Try again!')


class AlternativeModelTest(TestCase):
    """Testes para o modelo Alternative."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando uma fase, uma dica, uma pergunta e alternativas."""
        self.phase = Phase.objects.create(
            name='Growth',
            description='Growth phase description',
            creatures=Creature.objects.create(name='Dragon'),
            planet=Planet.objects.create(name='Earth')
        )
        self.hint = Hint.objects.create(hintText='Try again!')
        self.question = Question.objects.create(
            questionText='Is it alive?',
            phase=self.phase,
            hint=self.hint
        )
        self.alternative_yes = Alternative.objects.create(
            alternativeText='Yes',
            is_correct=True,
            question=self.question
        )
        self.alternative_no = Alternative.objects.create(
            alternativeText='No',
            is_correct=False,
            question=self.question
        )

    def test_str_method_yes(self):
        """Testa o método __str__ da alternativa 'Yes'."""
        self.assertEqual(str(self.alternative_yes), 'Yes')

    def test_str_method_no(self):
        """Testa o método __str__ da alternativa 'No'."""
        self.assertEqual(str(self.alternative_no), 'No')

    def test_foreign_key_relationship_yes(self):
        """Testa a relação de chave estrangeira da alternativa 'Yes' com a pergunta."""
        self.assertEqual(self.alternative_yes.question.questionText, 'Is it alive?')

    def test_foreign_key_relationship_no(self):
        """Testa a relação de chave estrangeira da alternativa 'No' com a pergunta."""
        self.assertEqual(self.alternative_no.question.questionText, 'Is it alive?')


class GameModelTest(TestCase):
    """Testes para o modelo Game."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando um usuário, uma fase e um jogo."""
        self.user = User.objects.create_user(email='wiryssongomes@gmail.com', name='Wiry Gomes', password='wiry123')
        self.phase = Phase.objects.create(name='Phase 1', description='Initial Phase')
        self.game = Game.objects.create(user=self.user, phase=self.phase)

    def test_game_initialization(self):
        """Testa a inicialização do jogo."""
        game = Game.objects.create(user=self.user, phase=self.phase)
        game.initialize_game()
        self.assertEqual(game.creature_life, 10)
        self.assertEqual(game.creature_attack, 1)

    def test_game_status(self):
        """Testa a lógica de status do jogo."""
        self.assertEqual(self.game.status, 'S')  # Status inicial
        self.game.creature_life = 0  # Define vida da criatura como 0
        self.game.user_life = 3  # Vida do usuário
        self.game.check_game_status()  # Verifica o status do jogo
        self.assertEqual(self.game.status, 'W')  

    def test_game_str(self):
        """Testa o método __str__ do jogo."""
        self.assertEqual(str(self.game), 'Wiry Gomes - (Iniciado)')

    def test_assign_questions(self):
        """Testa a atribuição de perguntas ao jogo."""
        question1 = Question.objects.create(questionText='Quem descobriu o Brasil?', phase=self.phase)
        question2 = Question.objects.create(questionText='Quem foi Martin Luther King?', phase=self.phase)
        self.game.assign_questions()  # Atribui perguntas ao jogo
        self.assertEqual(self.game.game_questions.count(), 2)  # Verifica se 2 perguntas foram atribuídas
    
    def test_initial_status(self):
        """Verifica se o status inicial do jogo é 'Iniciado'."""
        self.assertEqual(self.game.status, 'S')  # Status inicial esperado

    def test_creature_initial_attributes(self):
        """Verifica se os atributos da criatura são inicializados corretamente."""
        self.assertEqual(self.game.creature_life, 10)  # Vida da criatura
        self.assertEqual(self.game.creature_attack, 1)  # Ataque da criatura

    def test_user_life_initialization(self):
        """Verifica se a vida do usuário é inicializada corretamente."""
        self.game.initialize_game()  # Inicializa o jogo
        self.assertEqual(self.game.user_life, 3)  # Vida do usuário inicializada

    def test_check_game_status_loss(self):
        """Verifica se o status do jogo é atualizado corretamente para derrota."""
        self.game.user_life = 0  # Define vida do usuário como 0
        self.game.check_game_status()  # Verifica o status do jogo
        self.assertEqual(self.game.status, 'L')  # Status deve ser 'Derrota'


class GameEndModelTest(TestCase):
    """Testes para o modelo GameEnd."""

    def setUp(self):
        """Configura o ambiente de testes inicial, criando um usuário, uma criatura e uma instância de GameEnd."""
        self.user = User.objects.create_user(email='wiryssongomes@gmail.com', name='Wiry Gomes', password='wiry123')
        self.creature = Creature.objects.create(name='Dragon', description='A fierce creature')
        self.game_end = GameEnd.objects.create(
            user=self.user,
            result='W',
            points_gained=100
        )

    def test_game_end_creation(self):
        """Testa a criação do fim de jogo."""
        self.assertEqual(self.game_end.result, 'W')  # Verifica o resultado
        self.assertEqual(self.game_end.points_gained, 100)  # Verifica os pontos ganhos
        self.assertEqual(self.game_end.total_correct_answers, 0)  # Verifica se inicializa como 0  

    def test_game_end_user_relationship(self):
        """Verifica se o GameEnd está corretamente associado ao usuário."""
        self.assertEqual(self.game_end.user, self.user)  # Verifica a relação com o usuário

    def test_lost_creatures_relationship(self):
        """Verifica se as criaturas que perderam estão corretamente associadas ao GameEnd."""
        self.game_end.lost_creatures.add(self.creature) 
        self.assertIn(self.creature, self.game_end.lost_creatures.all())  # Verifica a relação com criaturas que perderam

    def test_default_total_correct_answers(self):
        """Verifica se o total de respostas corretas é inicializado como 0.""" 
        self.assertEqual(self.game_end.total_correct_answers, 0)  # Verifica se inicializa como 0

class UserTestCase(TestCase):
    # CRIA UM USUÁRIO HIPOTÉTICO PARA SER UTILIZADO AO LONGO DO CÓDIGO
    def setUp(self):
        self.persona = User.objects.create_user(email="wiryssongomes@gmail.com", name="Wiry Gomes", password="wiry123", crew="bopp", points=10)
    
    # TESTA A CRIAÇÃO DE UM USUÁRIO
    def test_user_creation(self):
        user = User.objects.create_user(email="user@exemplo.com", name="usuario1", password="12345678", crew="halley")
        self.assertIsInstance(user, User)
        
    # VERIFICA A ESCOLHA DO USUÁRIO DENTRO DAS OPÇÕES
    def test_crew_choice(self):
        user = self.persona
        crew_choices = [choice[0] for choice in user.CREWS] 
        self.assertIn(user.crew, crew_choices)
        
    # TESTA SE OS PONTOS ESTÃO SENDO DEDUZIDOS
    def test_points_distribuited(self):
        # Atualiza os atributos
        distribuition = PointsDistribution(user=self.persona, life_points=2, attack_points=3)
        distribuition.clean()
        distribuition.save()
        self.assertEqual(self.persona.points, 5)
        
    # TESTA SE OS ATRIBUTOS FORAM ATUALIZADOS
    def test_update_attributes(self):
        # Distribuição dos pontos de atributos
        distribution = PointsDistribution(user=self.persona, life_points=4, attack_points=6)
        distribution.clean()
        distribution.save()    
        
        # Verifica se os pontos e atributos foram atualizados corretamente
        self.assertEqual(self.persona.attributes.life, 7)  
        self.assertEqual(self.persona.attributes.attack, 7)  

        
class UserModelTestCase(TestCase):
    
    def setUp(self):
        # Cria um usuário e atributos para testes
        self.user = User.objects.create_user(
            email="wiryssongomes@gmail.com",
            name="Wiry Gomes",
            password="wiry123",
            crew="halley"
        )

    def test_user_creation_with_attributes(self):
        # Verifica se o usuário foi criado com atributos corretamente
        self.assertEqual(self.user.attributes.life, 3)
        self.assertEqual(self.user.attributes.attack, 1)

    def test_user_total_points_initial(self):
        # Verifica se os pontos totais iniciais estão corretos
        self.assertEqual(self.user.total_points, 0)

    def test_invalid_distribution_exceeds_points(self):
        # Testa se a validação funciona quando a soma dos pontos distribuídos excede os disponíveis
        self.user.points = 2  # Define os pontos do usuário para 2
        self.user.save()

        with self.assertRaises(ValidationError):
            distribution = PointsDistribution(
                user=self.user,
                life_points=3,  # 3 + 0 (pontos do usuário)
                attack_points=1
            )
            distribution.clean()  # Deve levantar uma ValidationError

    def update_status_ranking(self):
        games_won = self.games.filter(status='win').count()  # Substitua 'status' por como você está armazenando resultados de jogo
        ranking_instance, created = UserStatusRanking.objects.get_or_create(user=self)
        ranking_instance.games_won = games_won
        ranking_instance.save()
        ranking_instance.update_ranking()

    def test_user_unique_name_constraint(self):
        # Testa a restrição de unicidade para o nome do usuário
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="duplicate@example.com",
                name="Wiry Gomes",  # Nome já existente
                password="anotherpassword",
                crew="bopp"
            )