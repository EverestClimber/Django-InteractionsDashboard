import datetime
import os
import uuid
from django.utils import timezone
from django.db import models as m
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.utils.translation import ugettext_lazy as _

from interactions.helpers import ChoiceEnum

# Core Business Logic Models
#####################################################################

RESOURCES_DIR = 'resources'


class TimestampedModel(m.Model):
    class Meta:
        abstract = True

    created_at = m.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)


class AffiliateGroup(TimestampedModel):
    name = m.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__, self.name)


class Comment(TimestampedModel):
    user = m.ForeignKey('User', on_delete=m.SET_NULL, null=True, blank=True)
    engagement_plan = m.ForeignKey('EngagementPlan', on_delete=m.CASCADE)
    hcp_objective = m.ForeignKey('HCPObjective', on_delete=m.CASCADE)
    message = m.TextField()

    def __str__(self):
        return '{by} {on} @ {at}'.format(
            by=('by {}'.format(self.user.email) if self.user else ''),
            on=('EP #{}'.format(self.engagement_plan.id) if self.engagement_plan else (
                ('HCPObjective #{}'.format(self.hcp_objective.id) if self.hcp_objective else '')
            )),
            at=self.created_at
        )

    def __repr__(self):
        return '{}(user_id={}, engagement_plan_id={}, hcp_objective_id={})'.format(
            self.__class__.__name__,
            self.user_id, self.engagement_plan_id, self.hcp_objective_id)


class EngagementPlanPerms(ChoiceEnum):
    list_all_ep = 'Can list all EPs'
    list_own_ag_ep = 'Can list EPs of own AGs'
    change_own_current_ep = 'Can change own current EP'
    approve_all_ep = 'Can approve all EPs'
    approve_own_ag_ep = 'Can approve EPs of own AGs'


class EngagementPlan(TimestampedModel):
    class Meta:
        permissions = EngagementPlanPerms.choices()

    user = m.ForeignKey('User', on_delete=m.SET_NULL, null=True, blank=True)

    approved = m.BooleanField(default=False, blank=True)
    year = m.DateField(blank=True, default=datetime.date.today)

    approved_at = m.DateTimeField(null=True, blank=True)

    def approve(self):
        self.approved = True
        self.approved_at = timezone.now()
        self.save()

    def unapprove(self):
        self.approved = False
        self.save()


class EngagementListItem(TimestampedModel):
    engagement_plan = m.ForeignKey(EngagementPlan, on_delete=m.CASCADE)
    hcp = m.ForeignKey('HCP', on_delete=m.CASCADE)


class HCPObjective(TimestampedModel):
    engagement_plan = m.ForeignKey(EngagementPlan, on_delete=m.CASCADE)
    hcp = m.ForeignKey('HCP', on_delete=m.CASCADE)


class HCPDeliverable(TimestampedModel):
    class Meta:
        unique_together = (('quarter', 'hcp_objective'),)

    class Status(ChoiceEnum):
        on_track = 'On Track'
        slightly_behind = 'Slightly Behind'
        major_issue = 'Major Issue'

    QUARTERS_CHOICES = (
        (1, 'Q1'),
        (2, 'Q2'),
        (3, 'Q3'),
    )

    hcp_objective = m.ForeignKey(HCPObjective, on_delete=m.CASCADE)
    status = m.CharField(max_length=255, null=True, blank=True,
                         choices=Status.choices())
    quarter = m.PositiveSmallIntegerField(choices=QUARTERS_CHOICES,
                                          default=1)


class HCP(TimestampedModel):
    class ContactPreference(ChoiceEnum):
        email = 'Email'
        phone = 'Phone'

    affiliate_groups = m.ManyToManyField(AffiliateGroup, blank=True, related_name='hcps')
    tas = m.ManyToManyField('TherapeuticArea', blank=True, related_name='hcps')

    first_name = m.CharField(max_length=255, blank=True)
    last_name = m.CharField(max_length=255, blank=True)
    email = m.EmailField(max_length=255, blank=True)
    institution_name = m.CharField(max_length=255, blank=True)
    institution_address = m.TextField(blank=True)
    contact_preference = m.CharField(max_length=255, null=True, blank=True,
                                     choices=ContactPreference.choices())


class Interaction(TimestampedModel):
    user = m.ForeignKey('User', on_delete=m.SET_NULL, null=True, blank=True)
    hcp = m.ForeignKey('HCP', on_delete=m.SET_NULL, null=True, blank=True)
    hcp_objective = m.ForeignKey('HCPObjective', on_delete=m.SET_NULL, null=True, blank=True)
    project = m.ForeignKey('Project', on_delete=m.SET_NULL, null=True, blank=True)
    resources = m.ManyToManyField('Resource', blank=True, related_name='interactions')


class Project(TimestampedModel):
    name = m.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__, self.name)


def make_resource_filepath(instance, filename):
    path, ext = os.path.splitext(filename)
    now = timezone.datetime.now()
    current_month = '{}-{}'.format(now.year, now.month)
    return os.path.join(RESOURCES_DIR,
                        current_month,
                        uuid.uuid4().hex + ext)


class Resource(TimestampedModel):
    user = m.ForeignKey('User', on_delete=m.SET_NULL, null=True, blank=True)

    url = m.URLField(max_length=255, blank=True)
    file = m.FileField(upload_to=make_resource_filepath, null=True, blank=True)


class TherapeuticArea(TimestampedModel):
    name = m.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__, self.name)


# Users/Auth Models
#####################################################################


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
    business_title = m.CharField(max_length=255, blank=True,
                                 help_text='Business position title, eg. "Medical Manager"')
    affiliate_groups = m.ManyToManyField(AffiliateGroup, blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
