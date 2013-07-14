from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Lageruser(AbstractUser):
    

    def __unicode__(self):
        if self.first_name != "" and self.last_name != "":
            return "{0} {1}".format(self.first_name, self.last_name)
        else:
            return self.username