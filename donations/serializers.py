from rest_framework import serializers
from . models import Donation

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['campaign','donor','amount']


    def validate_amount(self,value):
        if value<=0:
            raise serializers.ValidationError('amount must be greated than zero')
        return value   




class UserUpdateDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['amount']


        