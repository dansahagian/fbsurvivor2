from django.db import models


class Lock(models.Model):
    week = models.ForeignKey("core.Week", on_delete=models.CASCADE)
    team = models.ForeignKey("core.Team", on_delete=models.CASCADE)
    lock_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.week} | {self.team}"

    class Meta:
        models.UniqueConstraint(fields=["week", "team"], name="unique_lock")
