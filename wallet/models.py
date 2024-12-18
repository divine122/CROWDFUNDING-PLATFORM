from django.db import models

# Create your models here.
from django.db import models
import uuid
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()
# Create your models here.

# TRANSACTION_STATUS_CHOICES = [
#     ("SUCCESSFUL", "SUCCESSFUL"),
#     ("FAILED", "FAILED"),
#     ("PENDING", "PENDING"),
# ]


# TRANSACT_TYPES = [
#     ('DEPOSIT', 'DEPOSIT'),
#     ('WITHDRAWAL', 'WITHDRAWAL'),
#     ('TRANSFER', 'TRANSFER'),
# ]

CURRENCY_CHOICES = [
    ('USDD','USD'),
    ('NGN','NGN')
]

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=23, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def deposit(self,amount):
        if amount <= 0:
            raise ValueError('Deposit amount must be positive')
        self.balance += Decimal(amount)
        self.save()

    def withdrawal(self,amount):
        if amount <= 0:
            raise ValueError('Withdrawal amount must be positive')
        if self.balance < Decimal(amount):
            raise ValueError('Insufficient balance')
        self.balance -= Decimal(amount)
        self.save()
    

    def __str__(self):
        return f"{self.user.first_name}'s wallet"
    
    


