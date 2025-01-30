from django.db import models
from pgvector.django import VectorField

class Word(models.Model):
    word = models.CharField(max_length=256)
    pos = models.CharField(max_length=32)
    embedding = VectorField(dimensions=768)
# Create your models here.
