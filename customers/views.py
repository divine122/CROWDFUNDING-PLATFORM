from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from . serializers import KYCSerializer
from . models import KYC
from rest_framework import views,status,permissions,request,response
from drf_yasg.utils import swagger_auto_schema




class KYCView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = KYCSerializer

    @swagger_auto_schema(request_body=KYCSerializer)
    def post(self, request):
        # Check if the user already has a KYC record
        kyc_instance = KYC.objects.filter(user=request.user).first()  # .first() ensures we get only one instance

        if kyc_instance:
            # If the KYC record exists, update it
            serializer = KYCSerializer(kyc_instance, data=request.data, partial=True)  # partial=True allows for partial updates
            if serializer.is_valid():
                serializer.save()  # Update the KYC record
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no record exists, create a new one
            data = request.data.copy()  # Copy the data to avoid modifying the original request data
            data['user'] = request.user.id  # Link the KYC record to the current authenticated user

            serializer = KYCSerializer(data=data)
            if serializer.is_valid():
                serializer.save()  # Create a new KYC record
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KYCDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = KYCSerializer

    def get(self, request):
        """
        Retrieve the current KYC details for the authenticated user.
        """
        try:
            kyc_record = KYC.objects.get(user=request.user)
        except KYC.DoesNotExist:
            return response.Response({"detail": "KYC record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the KYC data
        serializer = KYCSerializer(kyc_record)
        return response.Response(serializer.data, status=status.HTTP_200_OK) 



class KycUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = KYCSerializer


    def put(self, request):
        """
        Update the existing KYC details for the authenticated user.
        """
        try:
            kyc_record = KYC.objects.get(user=request.user)
        except KYC.DoesNotExist:
            return response.Response({"detail": "KYC record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the KYC data with the update
        serializer = KYCSerializer(kyc_record, data=request.data, partial=True)  # partial=True allows partial updates

        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
