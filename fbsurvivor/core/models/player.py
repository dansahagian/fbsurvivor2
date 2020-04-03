from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    username = models.CharField(max_length=20, unique=True)
    link = models.CharField(max_length=44, unique=True)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=12, null=True)
    is_admin = models.BooleanField(default=False)
    is_email_confirmed = models.BooleanField(default=False)
    is_phone_confirmed = models.BooleanField(default=False)
    confirmation_code = models.IntegerField(
        null=True,
        default=None,
        validators=[MinValueValidator(111111), MaxValueValidator(999999)],
    )

    def __str__(self):
        return f"{self.username}"
