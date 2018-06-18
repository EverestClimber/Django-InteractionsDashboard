from django.db import models as m
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.utils.translation import ugettext_lazy as _


class AffiliateGroup(m.Model):
    name = m.CharField(max_length=255, unique=True)
    created_at = m.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__,
                                      self.name)


class EngagementPlan(m.Model):
    user = m.ForeignKey('User', on_delete=m.SET_NULL, null=True, blank=True)
    approved = m.BooleanField(default=False, blank=True)



class UserManager(DefaultUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()

    # changed fields:
    username = None  # remove it as we login with email
    email = m.EmailField(_('email address'), unique=True)  # enforce unique

    # extra fields
    affiliate_groups = m.ManyToManyField(AffiliateGroup, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

