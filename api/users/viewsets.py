from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny

from .models import User, PointsDistribution
from .serializers import UserSerializer, CustomAuthSerializer, PointsDistributionSerializer

# Viewset da criação de usuário
class CreateUser(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Crie uma nova conta"

# Viewset do Login do usuário
class LoginUser(TokenObtainPairView):
    serializer_class = CustomAuthSerializer
    permission_classes = [AllowAny]

    def get_view_name(self):
        return "Acesse o HULIMAN"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # Retorna o token e o usuário
        user_serializer = UserSerializer(user)
        return Response({
            'token': token,
            'user': user_serializer.data,
        }, status=status.HTTP_200_OK)

# RETORNA TODOS OS USUÁRIOS NA TELA PRINCIPAL DA API
@api_view(['GET'])
def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()  # Devolve um QUERRYSET
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

# Viewset para distribuição de pontos
class PointsDistributionViewSet(viewsets.ModelViewSet):
    queryset = PointsDistribution.objects.all()
    serializer_class = PointsDistributionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return PointsDistribution.objects.filter(user__id=user_id)

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['user_id'])
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)

        # Criação da distribuição de pontos
        distribution = PointsDistribution.objects.create(
            user=user,
            life_points=serializer.validated_data['life_points'],
            attack_points=serializer.validated_data['attack_points']
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)