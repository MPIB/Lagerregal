from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lageruser',
            name='expiration_date',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
