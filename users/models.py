from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator

# Create your models here.
class Lageruser(AbstractUser):
    language = models.CharField(max_length=3, null=True)
    pagelength = models.IntegerField(validators=[
            MaxValueValidator(250)
        ], default=30)
    def __unicode__(self):
        if self.first_name != "" and self.last_name != "":
            return "{0} {1}".format(self.first_name, self.last_name)
        else:
            return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')