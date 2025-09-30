from django.db import models

class UzWord(models.Model):
    text = models.CharField(max_length=100)  # Asl so'z
    pred_segmentation = models.CharField(max_length=200, blank=True, null=True)  # Ajratilgan shakl

    def __str__(self):
        return self.text