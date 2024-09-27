from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Attribute, PointsDistribution
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

# DEFINIÇÃO DOS ATRIBUTOS PARA MODIFICAR DEPOIS
class AttributesOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['life','attack']

# TRANSFORMANDO OS DADOS EM QUERRY
class UserSerializer(serializers.ModelSerializer):
    attributes = AttributesOutputSerializer(read_only=True)
    points = serializers.CharField(read_only=True)
    distributed_points = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'crew', 'password', 'attributes', 'points', 'distributed_points', 'total_points']

    def validate_name(self, value):
        # Remove espaços em branco e converte para minúsculas
        name = value.replace(" ", "").lower()
        if not name.isalnum():
            raise serializers.ValidationError("O nome deve conter apenas caracteres alfanuméricos e não pode conter espaços.")
        return name

    def create(self, validated_data):
        # Garantir que o name seja salvo sem espaços e em minúsculas
        validated_data['name'] = validated_data['name'].replace(" ", "").lower()
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data, password=password)
        return user

# SERIALIZER PARA A AUTENTICAÇÃO DE USUÁRIO
class CustomAuthSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')

        user = authenticate(email=username_or_email, password=password)

        if user is None:
            try:
                user = User.objects.get(name__iexact=username_or_email)
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None

        if user is None:
            raise AuthenticationFailed('Invalid credentials.')

        # Gera o token JWT
        refresh = RefreshToken.for_user(user)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return {
            'user': user,
            'token': token_data,
        }
        
        

class PointsDistributionSerializer(serializers.ModelSerializer):
    available_points = serializers.SerializerMethodField()

    class Meta:
        model = PointsDistribution
        fields = ['life_points', 'attack_points', 'available_points']

    def get_available_points(self, obj):
        user = self.context['user']
        return user.points
