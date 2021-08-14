from django.db import models


class SignUpCode(models.Model):
    code = models.CharField(max_length=12)
