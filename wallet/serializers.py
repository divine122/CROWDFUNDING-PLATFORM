from rest_framework import serializers
from. models import Wallet
from decimal import Decimal, InvalidOperation


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id','amount',]



class WalletDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['amount']            

    def validate_amount(self, value):
        try:
            value = Decimal(value)
        except (ValueError, InvalidOperation):
            raise serializers.ValidationError("Amount must be a valid decimal.")
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value    
    

