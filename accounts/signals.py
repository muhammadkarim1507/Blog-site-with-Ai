from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Yangi User yaratilganda avtomatik Profile yaratadi.
    Signal: post_save — User saqlanganidan KEYIN ishga tushadi.
    """
    if created:
        Profile.objects.create(user=instance)
        print(f"✅ {instance.username} uchun profil yaratildi!")


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    User yangilanganda profilni ham saqlaydi.
    """
    instance.profile.save()