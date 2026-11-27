from django.db import models

class Ejemplo(models.Model):
    nombre = models.CharField(max_length=200)

class Empleado(models.Model):
    nombre = models.CharField(max_length=200)
    edad = models.IntegerField()