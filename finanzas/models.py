from django.db import models
from django.contrib.auth.models import User  # Para asociar transacciones a usuarios

class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[('income', 'Ingreso'), ('expense', 'Gasto')])

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Solo si usas autenticación
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.costo} - {self.fecha}"