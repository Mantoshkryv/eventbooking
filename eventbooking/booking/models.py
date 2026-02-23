from django.db import models

# Create your models here.

class Seat(models.Model):
    row = models.CharField(max_length=1)
    number = models.IntegerField()
    seat_id = models.CharField(max_length=5, unique=True, blank=True)
    booked = models.BooleanField(default=False)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.seat_id = f"{self.row}{self.number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.seat_id