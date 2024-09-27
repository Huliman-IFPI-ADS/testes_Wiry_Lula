from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.shortcuts import render
from django.http import HttpResponse
from .models import GameEnd, Creature, Question
from api.users.models import User
from .serializers import GameEndSerializer
from django.forms import ModelForm

class GameEndForm(ModelForm):
    class Meta:
        model = GameEnd
        fields = ['result', 'total_correct_answers', 'total_wrong_answers', 'lost_creatures', 'questions_answered']

class GameViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  # Permitir acesso a todos os usuários

    def create(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)  # Obter o usuário a partir do ID fornecido
        result = request.data.get('result')
        lost_creatures_ids = request.data.get('lost_creatures', [])
        questions_answered_ids = request.data.get('questions_answered', [])
        total_correct_answers = request.data.get('total_correct_answers', 0)
        total_wrong_answers = request.data.get('total_wrong_answers', 0)

        if result not in ['W', 'L']:
            return Response({'error': 'Invalid result value'}, status=status.HTTP_400_BAD_REQUEST)

        # Registrar o fim do jogo
        game_end = GameEnd.objects.create(
            user=user,
            result=result,
            total_correct_answers=total_correct_answers,
            total_wrong_answers=total_wrong_answers
        )

        if result == 'W':
            game_end.points_gained = 10  # Exemplo: 10 pontos para uma vitória
            user.points += game_end.points_gained
        elif result == 'L':
            game_end.points_gained = 0  # Sem perda de pontos em caso de derrota

            # Adicionar as criaturas perdidas
            for creature_id in lost_creatures_ids:
                creature = Creature.objects.get(id=creature_id)
                game_end.lost_creatures.add(creature)

        # Adicionar as perguntas respondidas
        for question_id in questions_answered_ids:
            question = Question.objects.get(id=question_id)
            game_end.questions_answered.add(question)

        # Atualiza o usuário com base nas respostas
        if total_correct_answers > total_wrong_answers:
            user.attributes.life += total_correct_answers  # Ganha vida com base nas respostas corretas
        else:
            user.attributes.life -= total_wrong_answers  # Perde vida com base nas respostas erradas

        user.save()
        game_end.save()

        serializer = GameEndSerializer(game_end)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        games = GameEnd.objects.all()  # Permitir listar todos os jogos
        serializer = GameEndSerializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def retrieve_game(self, request):
        user_id = request.query_params.get('id_user')
        phase_id = request.query_params.get('id_phase')

        # Verificar se os parâmetros foram fornecidos
        if user_id and phase_id:
            try:
                user_id = int(user_id)  # Converter para inteiro
                phase_id = int(phase_id)  # Converter para inteiro
                user = User.objects.get(id=user_id)
                game_end = GameEnd.objects.filter(user=user, id=phase_id).first()
                if game_end:
                    serializer = GameEndSerializer(game_end)
                    return Response(serializer.data)
                else:
                    return Response({'error': 'GameEnd not found'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({'error': 'Invalid id format'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET', 'POST'])
    def form(self, request):
        if request.method == 'POST':
            form = GameEndForm(request.POST)
            if form.is_valid():
                # Processa o formulário e cria o GameEnd
                game_end = form.save(commit=False)
                game_end.user = request.user
                game_end.save()
                return HttpResponse('Formulário enviado com sucesso!')
        else:
            form = GameEndForm()

        return render(request, 'game_end_form.html', {'form': form})
