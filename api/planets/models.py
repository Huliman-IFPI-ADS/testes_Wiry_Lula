from django.db import models
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static


# Modelo Creature
class Creature(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name=_('Image'),
        blank=True,
        null=True,
    )

    def get_image_path(self):
        if self.image:
            return self.image
        image_name = f'{self.name.lower().replace(" ", "_")}_info.png'
        return static(f'creatures/self.name.lower().replace(" ", "_")/{image_name}')

    class Meta:
        verbose_name = _('creature')
        verbose_name_plural = _('creatures')
        
    def __str__(self) -> str:
        return self.name

# Modelo Planet
class Planet(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True,
    )
    planetImage = models.ImageField(
         upload_to='planets/',
         verbose_name=_('Planet Image'),
         blank=True,
         null=True,
    )
    mapImage = models.ImageField(
         upload_to='planets/',
         verbose_name=_('Map Image'),
         blank=True,
         null=True,
    )
    galaxy = models.ForeignKey(
        'galaxies.Galaxy',
        on_delete=models.CASCADE,
        verbose_name=_('Galaxy'),
        related_name='planet_galaxy',
        blank=True,
        null=True,
    )
    
    class Meta:
        verbose_name = _('planet')
        verbose_name_plural = _('planets')
    def __str__(self) -> str:
        return self.name

# Modelo Phase
class Phase(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to='phases/',
        verbose_name=_('Image'),
        blank=True,
        null=True,
    )
    creatures = models.ForeignKey(
        'Creature',
        verbose_name=_('Creatures'),
        on_delete=models.CASCADE,
        related_name='phases',
        blank=True,
        null=True,
    )
    planet = models.ForeignKey(
        'Planet',
        on_delete=models.CASCADE,
        verbose_name=_('Planet'),
        related_name='phases',
        blank=True,
        null=True,
    )
    
    class Meta:
        verbose_name = _('phase')
        verbose_name_plural = _('phases')
    def __str__(self) -> str:
        return self.name

# Modelo Hint
class Hint(models.Model):
    hintText = models.TextField(
        verbose_name=_('Hint Text'),
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='hints', 
        verbose_name=_('User'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('hint')
        verbose_name_plural = _('hints')
    def __str__(self) -> str:
        return self.hintText

# Modelo Question
class Question(models.Model):
    questionText = models.TextField(
        verbose_name=_('Question Text'),
    )
    phase = models.ForeignKey(
        'planets.Phase',
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Phase'),
         blank=True,
         null=True,
    )
    hint = models.OneToOneField(
        'planets.Hint',
        on_delete=models.CASCADE,
        related_name='question',
        verbose_name=_('Hint'),
        blank=True,
        null=True,
    )
    
    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
    def __str__(self) -> str:
        return self.questionText

# Modelo Alternative
class Alternative(models.Model):
    alternativeText = models.TextField(
        verbose_name=_('Alternative Text')
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name=_('Is Correct')
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='alternatives',
        verbose_name=_('Question'),
         blank=True,
         null=True,
    )
    
    class Meta:
        verbose_name = _('alternative')
        verbose_name_plural = _('alternatives')
    def __str__(self) -> str:
        return self.alternativeText
