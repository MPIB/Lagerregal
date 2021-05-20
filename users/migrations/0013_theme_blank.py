from django.db import migrations
from django.db import models


def theme_default_blank(apps, schema_editor):
    Lageruser = apps.get_model('users', 'Lageruser')
    for user in Lageruser.objects.all():
        if user.theme == 'default':
            user.theme = ''
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20181006_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lageruser',
            name='theme',
            field=models.CharField(blank=True, choices=[('flatly', 'flatly'), ('darkly', 'darkly'), ('simplex', 'simplex'), ('superhero', 'superhero'), ('united', 'united'), ('paper', 'paper')], max_length=50),
        ),
        migrations.RunPython(theme_default_blank),
    ]
