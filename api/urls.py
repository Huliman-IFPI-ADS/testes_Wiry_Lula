from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .users.viewsets import get_users
from .planets.viewsets import HintViewSet, CreatureViewSet
from api.users.viewsets import LoginUser, CreateUser, PointsDistributionViewSet
from api.game.viewsets import GameViewSet

router = DefaultRouter()
router.register(r'hints', HintViewSet)
router.register(r'creatures', CreatureViewSet)
router.register(r'game', GameViewSet, basename='game')


urlpatterns = [
    path('users/', get_users, name='get_users'),  
    path('login/', LoginUser.as_view(), name='token_obtain_pair'),
    path('signin/', CreateUser.as_view({'post': 'create'}), name='cadastro'),
    path('distribute/<int:user_id>/', PointsDistributionViewSet.as_view({'post': 'create'}), name='points_distribute'),
    path('', include(router.urls)),  
]
