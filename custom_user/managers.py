from django.contrib.auth.models import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Email must be valid')

    def create_user(self, email, password, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('A valid email must be provided for this account')

        email = self.normalize_email(email)
        self.email_validator(email)  # Validate email

        # Default fields for user
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        # Create the user instance and save
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return a superuser with an email, password, and extra fields."""
        # Set required fields for a superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Ensure the superuser flags are True
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser fmust have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        # Create the superuser using create_user
        return self.create_user(email, password, **extra_fields)
