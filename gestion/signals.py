from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()

@receiver(post_save, sender=User)
def assign_prestamo_permission(instance, created, **kwargs):
    if created: 
        try:
            perm = Permission.objects.get(codename="gestionar_prestamos")
            instance.user_permissions.add(perm)
            instance.save()
            print("OK")
        except Permission.DoesNotExist:
            print("X") 

