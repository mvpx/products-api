from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class User(AbstractUser):
    pass


class Product(TimeStampedModel):
    name = models.CharField(unique=True, blank=True, null=True, max_length=255)
    price = models.DecimalField(null=True, max_digits=19, decimal_places=2)
    rating = models.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    users_rated = models.ManyToManyField(User)

    @property
    def average_rating(self):
        rating_average = Product.objects.aggregate(models.Avg("rating"))["rating__avg"]
        if rating_average:
            return round(rating_average, 1)

    def __str__(self):
        return f"{self.name}"
