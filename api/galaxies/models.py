from django.db import models
from django.utils.translation import gettext_lazy as _

class Galaxy(models.Model):
    name = models.CharField(
        max_length=100,
        unique= True,
    )
    image = models.ImageField(
        upload_to='galaxies/', 
        verbose_name=_('Galaxy'),
        default='galaxies/galaxyTest.jpg'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )

    class Meta:
        verbose_name = _("galaxy")
        verbose_name_plural = _("galaxies")
        
    def __str__(self) -> str:
        return self.name