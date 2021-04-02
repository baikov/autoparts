from django.db import models


class Part(models.Model):
    vin = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=300)

    def __str__(self) -> str:
        return self.code
