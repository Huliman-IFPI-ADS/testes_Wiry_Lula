from django.contrib import admin
from api.users.models import User, Attribute, PointsDistribution

admin.site.register(User)
admin.site.register(Attribute)
admin.site.register(PointsDistribution)