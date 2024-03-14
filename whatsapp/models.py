from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Attendant(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=10, choices=[('LIVRE', 'Livre'), ('OCUPADO', 'Ocupado')], default='LIVRE')

    def __str__(self):
        return self.name

class Conversation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    attendant = models.ForeignKey(Attendant, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation: {self.customer} - {self.attendant} ({self.started_at})"
