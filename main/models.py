from django.db import models

class UzWord(models.Model):
    text = models.CharField(max_length=100)  # Asl so'z
    pred_segmentation = models.CharField(max_length=200, blank=True, null=True)  # Ajratilgan shakl

    def __str__(self):
        return self.text
    
class OT(models.Model):

    word = models.CharField(max_length=300)

    def __str__(self):
        return self.word
    
class SIFAT(models.Model):

    word = models.CharField(max_length=300)

    def __str__(self):
        return self.word
    
class GIVENTEXT(models.Model):

    text = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
class UmumiyTurkum(models.Model):

    TURKUM = (
        ('1', 'OT'),
        ('2', 'SIFAT'),
        ('3', 'SON'),
        ('4', "FE'L"),
        ('5', 'RAVISH'),
        ('6', 'OLMOSH')
    )
    word = models.CharField(max_length = 100)
    type_is = models.CharField(max_length=1,choices=TURKUM, null=True, blank=True)

    def __str__(self):
        return self.word