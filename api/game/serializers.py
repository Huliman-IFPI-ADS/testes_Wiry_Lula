from rest_framework import serializers
from api.game.models import Game, GameQuestion, GameEnd
from api.planets.serializers import PhaseSerializer, CreatureSerializer, QuestionSerializer
from api.users.serializers import UserSerializer

class GameQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = GameQuestion
        fields = ['id', 'answered_correctly', 'question']

class GameSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    creature = CreatureSerializer()
    phase = PhaseSerializer()
    game_questions = GameQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'user', 'creature', 'phase', 'status',
            'user_life', 'user_attack', 'creature_life', 'creature_attack',
            'points_awarded', 'game_questions'
        ]

class GameEndSerializer(serializers.ModelSerializer):
    lost_creatures = CreatureSerializer(many=True, read_only=True)
    questions_answered = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = GameEnd
        fields = [
            'user', 'result', 'points_gained', 'lost_creatures',
            'questions_answered', 'total_correct_answers',
            'total_wrong_answers', 'created_at'
        ]