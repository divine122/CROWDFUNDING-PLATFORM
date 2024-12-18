from rest_framework import serializers
from . models import KYC

class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = ['first_name','last_name','dob','address','verification_status']


    def create(self, validated_data):
        user = validated_data('user')
        return super().create(validated_data)