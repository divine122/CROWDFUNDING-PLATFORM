from django.shortcuts import render

# Create your views here.
from rest_framework import permissions,response,status,views
from rest_framework.exceptions import NotFound,ValidationError
from . models import Wallet
from . serializers import WalletSerializer,WalletDepositSerializer
from drf_yasg.utils import swagger_auto_schema
from decimal import Decimal


class WalletDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer


    @swagger_auto_schema(operation_description="Retrieve the wallet details for the authenticated user.")
    def get(self, request, *args, **kwargs):
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            raise NotFound('Wallet not found')
        
        serializer = WalletSerializer(wallet)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    

class WalletDepositView(views.APIView):
    permission_classes= [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    @swagger_auto_schema(
        operation_description="Deposit an amount into the authenticated user's wallet.",
        request_body=WalletDepositSerializer,
        responses={status.HTTP_200_OK: 'Deposit successful', status.HTTP_400_BAD_REQUEST: 'Invalid deposit amount'}
    )
    def post(self, request, *args, **kwargs):
        serializer = WalletDepositSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            wallet = request.user.wallet

            # Logic for depositing money into the wallet
            wallet.balance += amount
            wallet.save()

            return response.Response({"detail": "Deposit successful", "new_balance": wallet.balance}, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WalletWithdrawalView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    @swagger_auto_schema(
        request_body=WalletSerializer,  # Specifies the expected request body schema
        responses={
            200: 'Successful withdrawal response',
            400: 'Bad request due to validation or other issues',
        }
    )
    def post(self, request, *args, **kwargs):
        # Validate the input using the serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Extract the validated amount
            amount = serializer.validated_data['amount']
            print(f"Requested withdrawal amount: {amount}")

            try:
                wallet = request.user.wallet  # Assuming a one-to-one relationship with User

                # Print the current balance for debugging
                print(f"User wallet balance before withdrawal: {wallet.balance}")

                # Check if the user has sufficient balance
                if wallet.balance < amount:
                    print(f"Insufficient balance. Current balance: {wallet.balance}, Requested amount: {amount}")
                    return response.Response({"detail": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

                # Withdraw the amount
                wallet.balance -= amount
                wallet.save()

                # Return the success message and updated balance
                print(f"User wallet balance after withdrawal: {wallet.balance}")
                return response.Response(
                    {"detail": f"Withdrawn {amount} successfully.", "balance": str(wallet.balance)},
                    status=status.HTTP_200_OK
                )
            except Wallet.DoesNotExist:
                return response.Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Return validation errors if the serializer is not valid
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)