from django.db import migrations


def rewrite_group_view_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    rels = Group.permissions.through.objects
    for read_perm in Permission.objects.filter(codename__startswith='read_'):
        codename = read_perm.codename.replace('read_', 'view_')
        if read_perm.codename == 'read_user':
            codename = 'view_lageruser'
        view_perm = Permission.objects.get(
            codename=codename,
            content_type=read_perm.content_type,
        )
        rels.filter(permission=read_perm).update(permission=view_perm)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0015_auto_20190524_1050'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.RunPython(rewrite_group_view_permissions),
    ]
