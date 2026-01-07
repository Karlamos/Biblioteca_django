from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

@receiver(post_save, sender=User)
def assign_group_permissions(instance, created, **kwargs):
    if created:

        if instance.is_superuser or 'admin' in instance.username.lower():
            grupo, _ = Group.objects.get_or_create(name='Admin')
            permisos = [
                'view_libro', 'change_libro', 'add_libro'
                'view_autor', 'change_autor',
                'Ver_prestamo', 'gestionar_prestamo',
                'view_multa', 'add_multa'
            ]
            _asignar_permisos_a_grupo(grupo, permisos)
            instance.groups.add(grupo)
        elif 'bibliotecario' in instance.username.lower():
            grupo, _ = Group.objects.get_or_create(name='Bibliotecario')
            permisos = [
                'view_libro', 'change_libro',
                'view_autor', 'change_autor',
                'view_prestamo', 'add_prestamo', 'change_prestamo',
                'view_multa', 'add_multa', 'change_multa'
            ]
            _asignar_permisos_a_grupo(grupo, permisos)
            instance.groups.add(grupo)

        elif 'bodeguero' in instance.username.lower():
            grupo, _ = Group.objects.get_or_create(name='Bodeguero')
            permisos = [
                'view_libro', 'change_libro', 'add_libro'
                'view_autor', 'change_autor', 'add_autor'
                'view_prestamo', 'add_prestamo', 'change_prestamo',
                'view_multa', 'add_multa', 'change_multa'
            ]
            _asignar_permisos_a_grupo(grupo, permisos)
            instance.groups.add(grupo)


        elif 'usuario' in instance.username.lower():
            grupo, _ = Group.objects.get_or_create(name='Usuario')
            permisos = [
                'view_libro', 
                'view_prestamo', 'add_prestamo', 
                'view_multa',
            ]
            _asignar_permisos_a_grupo(grupo, permisos)
            instance.groups.add(grupo)

        instance.save()
        print(f"Permisos de grupo configurados para {instance.username}")

def _asignar_permisos_a_grupo(grupo, lista_codenames):
    """Función auxiliar para buscar y añadir permisos al grupo"""
    for codename in lista_codenames:
        try:
            perm = Permission.objects.get(codename=codename)
            grupo.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Aviso: El permiso {codename} no existe en la base de datos.")