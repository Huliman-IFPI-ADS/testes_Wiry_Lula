from django.db import models
from django.utils.translation import gettext_lazy as _
from api.planets.models import Question, Phase, Creature
from django.templatetags.static import static
import random
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from api.planets.models import Question, Phase, Creature
from django.templatetags.static import static
import random
import math

class Game(models.Model):
    STATUS_CHOICES = [
        ('S', _('Iniciado')),
        ('F', _('Finalizado')),
        ('W', _('Vitória')),
        ('L', _('Derrota')),
    ]
    user = models.ForeignKey(
        'users.User',
        on_delete=models.RESTRICT,
        verbose_name=_('User'),
        related_name='games'
    )
    phase = models.ForeignKey(
        Phase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Phase'),
        related_name='games'
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='S',
        verbose_name=_('Status')
    )
    creature_life = models.PositiveIntegerField(
        verbose_name=_('Creature Life'),
        default=10 
    )
    creature_attack = models.PositiveIntegerField(
        verbose_name=_('Creature Attack'),
        default=1
    )

    def __str__(self):
        return f"{self.user} - ({self.get_status_display()})"

    def initialize_game(self):
        self.user_life = 3
        self.user_attack = 1
        self.creature_life = 10
        self.creature_attack = 1
        self.save()

    def update_life_and_attack(self):
        # Atualiza a vida e o ataque da criatura com base na fase do jogo
        if self.phase and self.phase.creature:
            base_life = self.phase.creature.life
            base_attack = self.phase.creature.attack
        else:
            base_life = 10
            base_attack = 1

        # Escala a vida da criatura com base no total de pontos do usuário
        total_points = self.user.total_points
        # Fórmula para ajustar a vida da criatura
        # Aqui, usamos uma fórmula exponencial moderada: base_life * (1 + log(total_points + 1))
        self.creature_life = int(base_life * (1 + math.log(total_points + 1)))
        self.creature_attack = base_attack

        # Atualiza a vida e o ataque do usuário com base nos atributos distribuídos
        if self.user.attributes:
            self.user_life = self.user.attributes.life
            self.user_attack = self.user.attributes.attack
        else:
            self.user_life = 3
            self.user_attack = 1

        self.save()

    def check_game_status(self):
        if self.user_life <= 0:
            self.status = 'L'
        elif self.creature_life <= 0:
            self.status = 'W'
        else:
            self.status = 'S'
        self.save()

    def handle_answer(self, correct):
        if correct:
            self.creature_life -= self.user_attack
        else:
            self.user_life -= self.creature_attack
        
        self.check_game_status()
        self.update_life_and_attack()

        self.user.save()
        self.creature.save()

    def assign_questions(self):
        if not self.phase:
            raise ValueError("A fase do jogo não está definida.")
        
        # Seleciona perguntas com base na fase
        questions = list(Question.objects.filter(phase=self.phase))  # Filtra perguntas pela fase
        if not questions:
            raise ValueError("Nenhuma pergunta encontrada para a fase atual.")

        random.shuffle(questions)  # Embaralha as perguntas
        num_questions = min(5, len(questions))  # Limita o número de perguntas se necessário
        selected_questions = questions[:num_questions]  # Seleciona o número desejado de perguntas

        for question in selected_questions:
            GameQuestion.objects.create(game=self, question=question)

    class Meta:
        verbose_name = _('game')
        verbose_name_plural = _('games')




class GameQuestion(models.Model):
    answered_correctly = models.BooleanField(
        verbose_name=_('Answered Correctly'),
        default=False,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_('Question'),
        related_name='game_questions',
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name=_('Game'),
        related_name='game_questions',
    )
    
    def __str__(self):
        return f"{self.game} - {self.question.questionText}"

    def get_alternatives(self):
        return self.question.alternatives.all()

    class Meta:
        verbose_name = _('game question')
        verbose_name_plural = _('game questions')

class GameEnd(models.Model):
    RESULT_CHOICES = [
        ('W', 'Win'),
        ('L', 'Lose'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=19)  # Substitua 1 pelo ID padrão do usuário
    result = models.CharField(max_length=1, choices=RESULT_CHOICES, null=False, default='W')
    points_gained = models.IntegerField(default=0)
    lost_creatures = models.ManyToManyField(Creature, blank=True)
    questions_answered = models.ManyToManyField(Question, blank=True)
    total_correct_answers = models.IntegerField(default=0)
    total_wrong_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"End of game {self.game} at {self.end_time}"

    def determine_images_and_messages(self):
        if self.game.status == 'W':
            # Puxar a imagem de vitória com base na escolha do crew
            if self.game.user.crew == 'halley':
                return static('crews/halley/halley_victory.png')
            elif self.game.user.crew == 'bopp':
                return static('crews/bopp/bopp_victory.png')
            self.defeat_image = None

            # Atualiza os pontos do usuário
            self.game.user.points += self.points_awarded
            self.game.user.save()
            
            # Mensagem personalizada de vitória
            self.victory_message = (
                f"Parabéns, {self.game.user.name}! Você ganhou o jogo e conquistou {self.points_awarded} pontos."
            )
            self.defeat_message = None
        elif self.game.status == 'L':
            # Puxar a imagem da criatura em caso de derrota
            self.defeat_image = self.game.creature.image_url
            self.victory_image = None

            # Mensagem personalizada de derrota
            self.defeat_message = (
                f"Você perdeu, {self.game.user.name}. A criatura {self.game.creature.name} venceu o jogo."
            )

        self.save()
