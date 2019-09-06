from django.db import models


class Bidon(models.Model):
    name = models.CharField(max_length=255)
