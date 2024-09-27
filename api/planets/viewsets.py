from rest_framework import viewsets
from api.planets.models import Hint, Creature
from api.planets.serializers import HintSerializer, CreatureSerializer

class HintViewSet(viewsets.ModelViewSet):
    queryset = Hint.objects.all()
    serializer_class = HintSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        id_user = self.request.query_params.get('id_user')
        if id_user:
            context['id_user'] = id_user
        return context
    
class CreatureViewSet(viewsets.ModelViewSet):
    queryset = Creature.objects.all()
    serializer_class = CreatureSerializer
    
