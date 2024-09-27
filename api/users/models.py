from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


# Model para manipulação de user para a criação de conta
class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password=None, crew=None, **extra_fields):
        if not email:
            raise ValueError("O usuário precisa de um email!")
        
        if User.objects.filter(name__iexact=name).exists():
            raise ValueError("Já existe um usuário com este nome.")
        
        email = self.normalize_email(email)
        user = self.model(
            name=name,
            email=email,
            crew=crew,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        else:
            user.set_password(self.make_random_password())
        
        attribute = Attribute.objects.create(life=3, attack=1)
        user.attributes = attribute
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_admin") is not True:
            raise ValueError("O superusuário deve ter is_admin=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("O superusuário deve ter is_superuser=True.")

        return self.create_user(name, email, password, **extra_fields)
    
    def get_by_natural_key(self, identifier):
        try:
            return self.get(email=identifier)
        except self.model.DoesNotExist:
            pass
        try:
            return self.get(name__iexact=identifier)
        except self.model.DoesNotExist:
            pass
        raise self.model.DoesNotExist(f'Usuário ou E-mail "{identifier}" não foi encontrado!')

# Model dos atributos que o usuário possui
class Attribute(models.Model):
    life = models.IntegerField(
        verbose_name=_('life'),
        default=3,
        
    )
    attack = models.IntegerField(
        verbose_name=_('attack'),
        default=1,
    )

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')
    def __str__(self) -> str:
        return f'{self.life}/{self.attack}'

# Model de user que servirá para outras manipulações
class User(AbstractBaseUser, PermissionsMixin):
    CREWS = (
        ('halley', _('Halley')),
        ('bopp', _('Bopp')),
    )
    
    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
        unique=True,
    )
    def clean(self):
        if ' ' in self.name:
            raise ValidationError("Nome não deve conter espaços.")
        super().clean()
    
    points = models.IntegerField(
        verbose_name=_('points'),
        default=0,
    )
    
    crew = models.CharField(
        max_length=6,
        choices=CREWS,
        verbose_name=_('crew'),
        null= True,
        default='halley',
    )
    distributed_points = models.IntegerField(
        verbose_name=_('Total Distributed Points'),
        default=0,
    )
    @property
    def total_points(self):
        return self.points + self.distributed_points
    
    # Os atributos estão vinculados a apenas um usuário
    attributes = models.OneToOneField(
        'Attribute',
        verbose_name=_('attributes'),
        on_delete=models.CASCADE,
        related_name='user',
        blank=True, 
        null=True, 
    )
    
    is_admin = models.BooleanField(
        _("admin status"),
        default=False,
        help_text=_(
            "Designa se o usuário pode acessar este site de administração."
        ),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designa se este usuário deve ser tratado como ativo. "
            "Desmarque isso em vez de excluir contas."
        ),
    )

    date_joined = models.DateTimeField(
        _("date joined"),
        auto_now_add=True,
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('auth.User.groups'),
        blank=True,
        related_name='auth_user_groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='auth_user_permissions',
    )
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name'] 

    class Meta:
        ordering = ['-id']
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self) -> str:
        return self.name

    @property
    def is_staff(self):
        return self.is_admin

    # Metodo para modificar os atributos com base no que foi modificado em PointsDistribution
    def update_attributes_from_distribution(self):
        last_distribution = self.points_distributions.last()
        if last_distribution:
            # Garantir que a subtração dos pontos não torne o total negativo
            self.attributes.life += last_distribution.life_points
            self.attributes.attack += last_distribution.attack_points
            self.attributes.save()
            self.save()


    # Metodo para modificar o ranking do usuário
    def update_status_ranking(self):
        games_won = self.games.filter(is_win=True).count()
        ranking_instance, created = UserStatusRanking.objects.get_or_create(user=self)
        ranking_instance.games_won = games_won
        ranking_instance.save()
        ranking_instance.update_ranking()

# Model da distribuição de pontos
class PointsDistribution(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='points_distributions',
        verbose_name=_('User')
    )
    life_points = models.IntegerField(
        verbose_name=_('Life Points'),
        default=0,
    )
    attack_points = models.IntegerField(
        verbose_name=_('Attack Points'),
        default=0,
    )
    distributed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Distributed At')
    )

    def clean(self):
        # soma o total de pontos
        total_distributed_points = self.life_points + self.attack_points
        # vai ver se o o total distribuído é maior que o valor disponível
        if total_distributed_points > self.user.points:
            raise ValidationError('A soma de life_points e attack_points não pode ser maior que os pontos do usuário.')
        return total_distributed_points

    def save(self, *args, **kwargs):
        # Valida todos os campos e o modelo
        self.full_clean()
        total_distributed_points = self.life_points + self.attack_points
        
        # Atualiza a quantidade de pontos distribuídos
        self.user.points -= total_distributed_points
        self.user.distributed_points += total_distributed_points
        
        # Salva as mudanças nos modelos relacionados
        self.user.attributes.save()
        self.user.save()
        
        # Salva a distribuição de pontos
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = _('points distribution')
        verbose_name_plural = _('points distributions')

    def __str__(self) -> str:
        return f'{self.life_points}/{self.attack_points}'


# Model para mostrar a posição de ranking, mostrando os games ganhados
class UserStatusRanking(models.Model):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='status_ranking'
    )
    games_won = models.PositiveIntegerField(
        verbose_name=_('Games Won'),
        default=0
    )
    ranking = models.PositiveIntegerField(
        verbose_name=_('Ranking'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('user status ranking')
        verbose_name_plural = _('user status rankings')

    def update_ranking(self):
        all_users = UserStatusRanking.objects.order_by('-games_won')
        for rank, user_status in enumerate(all_users, start=1):
            user_status.ranking = rank
            user_status.save()

# Metodo que recebe os novos atributos do usuário
@receiver(post_save, sender=PointsDistribution)
def update_user_attributes(sender, instance, **kwargs):
    instance.user.update_attributes_from_distribution()
