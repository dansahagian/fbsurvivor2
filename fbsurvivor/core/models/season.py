from django.db import models


class Season(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)
    is_locked = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.year}"

    class Meta:
        ordering = ["-year"]
        indexes = [models.Index(fields=["year"])]
