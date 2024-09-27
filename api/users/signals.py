# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import PointsDistribution

# @receiver(post_save, sender=PointsDistribution)
# def update_user_attributes(sender, instance, created, **kwargs):
#     if created or kwargs.get('update_fields'):
#         instance.User.update_attributes_from_distribution()