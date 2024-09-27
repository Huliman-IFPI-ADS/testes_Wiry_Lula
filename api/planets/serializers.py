from rest_framework import serializers
from django.templatetags.static import static
from api.planets.models import Hint, Phase, Creature, Question, Alternative
from api.users.models import User

class HintSerializer(serializers.ModelSerializer):
    hint_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Hint
        fields = ['id', 'hintText', 'hint_image_url']

    def get_hint_image_url(self, obj):
        id_user = self.context.get('id_user')
        if id_user:
            try:
                user = User.objects.get(id=id_user)
                if user.crew == 'halley':
                    return static('crews/bopp/bopp_popup.png')
                elif user.crew == 'bopp':
                    return static('crews/halley/halley_popup.png')
            except User.DoesNotExist:
                return None
        return None

class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ['id', 'name', 'description']

class CreatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creature
        fields = ['id', 'name', 'description', 'image']

class AlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ['id', 'alternativeText']

class QuestionSerializer(serializers.ModelSerializer):
    alternatives = AlternativeSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'questionText', 'alternatives']
