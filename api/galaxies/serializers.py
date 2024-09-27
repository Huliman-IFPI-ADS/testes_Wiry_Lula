from rest_framework import serializers
from .models import Galaxy

class GalaxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Galaxy
        fields = ['id','name',]