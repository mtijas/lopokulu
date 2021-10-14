from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _


class PersonManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_staff(self, email, password=None):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user


class Vehicle(models.Model):
    register_number = models.CharField("Register number", max_length=32)
    name = models.TextField("Name of the vehicle")

    def __str__(self):
        return f'({self.register_number}) {self.name}'


class Person(AbstractBaseUser, PermissionsMixin):
    vehicles = models.ManyToManyField(Vehicle, through='VehicleUser')

    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = PersonManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class VehicleUser(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Role(models.TextChoices):
        READ_ONLY = 'RO', _('Read only')
        DRIVER = 'DR', _('Driver')
        OWNER = 'OW', _('Owner')
    role = models.CharField(
        max_length=2, choices=Role.choices, default=Role.READ_ONLY)

    def __str__(self):
        return f'{self.vehicle.name} has {self.role} person {self.person}'
