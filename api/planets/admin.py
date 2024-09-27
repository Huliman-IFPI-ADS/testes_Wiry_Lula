from django.contrib import admin
from .models import Planet, Phase, Creature, Question, Alternative, Hint
# , HintImage

admin.site.register(Planet)
admin.site.register(Phase)
admin.site.register(Creature)
admin.site.register(Question)
admin.site.register(Alternative)
admin.site.register(Hint)
