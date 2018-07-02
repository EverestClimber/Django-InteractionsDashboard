import datetime
import os
import uuid
from django.utils import timezone
from django.db import models as m
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.utils.translation import ugettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE

from interactions.helpers import ChoiceEnum

# Core Business Logic Models
#####################################################################

RESOURCES_DIR = 'resources'


class TimestampedModel(m.Model):
    class Meta:
        abstract = True

    created_at = m.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)


class ApprovableModel(m.Model):
    class Meta:
        abstract = True

    approved = m.BooleanField(default=False, blank=True)
    approved_at = m.DateTimeField(null=True, blank=True)

    def approve(self):
        self.approved = True
        self.approved_at = timezone.now()
        self.save()

    def unapprove(self):
        self.approved = False
        self.save()


class AffiliateGroup(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    name = m.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__, self.name)


class Comment(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    user = m.ForeignKey('User', on_delete=m.CASCADE, null=True, blank=True)
    engagement_plan = m.ForeignKey('EngagementPlan', on_delete=m.CASCADE,
                                   null=True, blank=True,
                                   related_name='comments')
    engagement_plan_hcp_item = m.ForeignKey('EngagementPlanHCPItem', on_delete=m.CASCADE,
                                            null=True, blank=True,
                                            related_name='comments')
    engagement_plan_project_item = m.ForeignKey('EngagementPlanProjectItem', on_delete=m.CASCADE,
                                                null=True, blank=True,
                                                related_name='comments')
    message = m.TextField()

    def __str__(self):
        return '{by} {on} @ {at}'.format(
            by=('by {}'.format(self.user.email) if self.user else ''),
            on=('on ELItem #{}'.format(self.engagement_list_item.id) if self.engagement_list_item else (
                ('on HCPObjective #{}'.format(self.hcp_objective.id) if self.hcp_objective else '')
            )),
            at=self.created_at
        )

    def __repr__(self):
        return '{}(user_id={}, engagement_list_item_id={}, hcp_objective_id={})'.format(
            self.__class__.__name__,
            self.user_id, self.engagement_list_item_id, self.hcp_objective_id)


class EngagementPlanPerms(ChoiceEnum):
    list_all_ep = 'Can list all EPs'
    list_own_ag_ep = 'Can list EPs of own AGs'
    change_own_current_ep = 'Can change own current EP'
    approve_all_ep = 'Can approve all EPs'
    approve_own_ag_ep = 'Can approve EPs of own AGs'


class EngagementPlan(TimestampedModel, ApprovableModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        permissions = EngagementPlanPerms.choices()

    user = m.ForeignKey('User', on_delete=m.CASCADE,
                        related_name='engagement_plans')

    year = m.IntegerField()

    def __str__(self):
        return "{} / {}".format(self.user.email if self.user else '',
                                self.year)


class EngagementPlanHCPItem(TimestampedModel, ApprovableModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    engagement_plan = m.ForeignKey(EngagementPlan, on_delete=m.CASCADE,
                                   related_name='hcp_items')
    hcp = m.ForeignKey('HCP', on_delete=m.CASCADE)


class EngagementPlanProjectItem(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    engagement_plan = m.ForeignKey(EngagementPlan, on_delete=m.CASCADE,
                                   related_name='project_items')
    project = m.ForeignKey('Project', on_delete=m.CASCADE)


class HCPObjective(TimestampedModel, ApprovableModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    engagement_plan_item = m.ForeignKey(EngagementPlanHCPItem, on_delete=m.CASCADE,
                                        related_name='objectives')
    hcp = m.ForeignKey('HCP', on_delete=m.CASCADE)

    description = m.TextField()


class ProjectObjective(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    engagement_plan_item = m.ForeignKey(EngagementPlanProjectItem, on_delete=m.CASCADE,
                                        related_name='objectives')
    project = m.ForeignKey('Project', on_delete=m.CASCADE)

    description = m.TextField()


QUARTERS_CHOICES = (
    (1, 'Q1'),
    (2, 'Q2'),
    (3, 'Q3'),
    (4, 'Q4'),
)


class HCPDeliverable(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    class Meta:
        unique_together = (('quarter', 'objective'),)

    objective = m.ForeignKey(HCPObjective, on_delete=m.CASCADE,
                             related_name='deliverables')

    quarter = m.PositiveSmallIntegerField(choices=QUARTERS_CHOICES)
    description = m.CharField(max_length=255, blank=True)

    class Status(ChoiceEnum):
        on_track = 'On Track'
        slightly_behind = 'Slightly Behind'
        major_issue = 'Major Issue'

    status = m.CharField(max_length=255, null=True, blank=True,
                         choices=Status.choices())


class ProjectDeliverable(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    class Meta:
        unique_together = (('quarter', 'objective'),)

    objective = m.ForeignKey(ProjectObjective, on_delete=m.CASCADE,
                             related_name='deliverables')

    quarter = m.PositiveSmallIntegerField(choices=QUARTERS_CHOICES)
    description = m.CharField(max_length=255, blank=True)

    class Status(ChoiceEnum):
        on_track = 'On Track'
        slightly_behind = 'Slightly Behind'
        major_issue = 'Major Issue'

    status = m.CharField(max_length=255, null=True, blank=True,
                         choices=Status.choices())


class HCP(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    class ContactPreference(ChoiceEnum):
        email = 'Email'
        phone = 'Phone'

    affiliate_groups = m.ManyToManyField(AffiliateGroup, blank=True, related_name='hcps')
    tas = m.ManyToManyField('TherapeuticArea', blank=True, related_name='hcps')

    first_name = m.CharField(max_length=255, blank=True)
    last_name = m.CharField(max_length=255, blank=True)
    email = m.EmailField(max_length=255, blank=True)
    phone = m.CharField(max_length=255, blank=True)
    contact_person_first_name = m.CharField(max_length=255, blank=True)
    contact_person_last_name = m.CharField(max_length=255, blank=True)
    contact_person_email = m.EmailField(max_length=255, blank=True)
    contact_person_phone = m.CharField(max_length=255, blank=True)
    time_availability = m.CharField(max_length=255, blank=True)
    institution_name = m.CharField(max_length=255, blank=True)
    institution_address = m.TextField(blank=True)
    contact_preference = m.CharField(max_length=255, null=True, blank=True,
                                     choices=ContactPreference.choices())

    city = m.CharField(max_length=255, blank=True)
    country = m.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __repr__(self):
        return '{}(first_name="{}", last_name="{}")'.format(self.__class__.__name__,
                                                            self.first_name,
                                                            self.last_name)


class InteractionPerms(ChoiceEnum):
    list_all_interaction = 'Can list all Interactions'
    list_own_ag_interaction = 'Can list Interactions of own AGs'


class Interaction(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        permissions = InteractionPerms.choices()

    # TODO: investigate behavior on soft-deleting User and HCP
    # (also considering that HCP does not have safe delete set to be cascading)

    user = m.ForeignKey('User', on_delete=m.CASCADE,
                        # limit_choices_to={'groups__name': 'Role MSL'},
                        verbose_name='MSL')
    hcp = m.ForeignKey('HCP', on_delete=m.CASCADE)
    hcp_objective = m.ForeignKey('HCPObjective', on_delete=m.SET_NULL, null=True)
    project = m.ForeignKey('Project', on_delete=m.SET_NULL, null=True)
    resources = m.ManyToManyField('Resource', blank=True, related_name='interactions')
    outcomes = m.ManyToManyField('InteractionOutcome', blank=True, related_name='interactions')

    description = m.TextField()
    purpose = m.TextField()

    is_joint_visit = m.BooleanField(default=False, verbose_name='Joint visit')
    joint_visit_with = m.TextField(blank=True)  # when is_joint_visit=True

    class OriginOfInteraction(ChoiceEnum):
        medinfo_enquiry = 'MedInfo enquiry'
        engagement_plan = 'Engagement Plan'
        other = 'Other'

    origin_of_interaction = m.CharField(max_length=255,
                                        choices=OriginOfInteraction.choices())
    origin_of_interaction_other = m.CharField(max_length=255, blank=True)  # when origin_of_interaction="other"

    class TypeOfInteraction(ChoiceEnum):
        phone = 'Phone'
        face_to_face = 'Face-to-face'
        other = 'Email'

    type_of_interaction = m.CharField(max_length=255,
                                      choices=TypeOfInteraction.choices())

    is_adverse_event = m.BooleanField(default=False, verbose_name='Adverse event')
    appropriate_pv_procedures_followed = m.NullBooleanField(default=False, null=True)  # when is_adverse_event=True
    is_follow_up_required = m.BooleanField(default=False, verbose_name='Follow up required')


class InteractionOutcome(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    name = m.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__, self.name)


class Project(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    user = m.ForeignKey('User', on_delete=m.CASCADE, null=True, blank=True,
                        related_name='projects')
    affiliate_groups = m.ManyToManyField(AffiliateGroup, blank=True, related_name='projects')
    tas = m.ManyToManyField('TherapeuticArea', blank=True, related_name='projects')

    title = m.CharField(max_length=255, unique=True)

    class Type(ChoiceEnum):
        personal_project = 'Personal'
        country_project = 'Country'
        global_project = 'Global'

    type = m.CharField(max_length=255,
                       choices=Type.choices())

    def __str__(self):
        return self.title

    def __repr__(self):
        return '{}(title="{}")'.format(self.__class__.__name__, self.name)


def make_resource_filepath(instance, filename):
    path, ext = os.path.splitext(filename)
    now = timezone.datetime.now()
    current_month = '{}-{}'.format(now.year, now.month)
    return os.path.join(RESOURCES_DIR,
                        current_month,
                        uuid.uuid4().hex + ext)


class Resource(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    user = m.ForeignKey('User', on_delete=m.SET_NULL, null=True, blank=True)
    affiliate_groups = m.ManyToManyField(AffiliateGroup, blank=True, related_name='resources')
    tas = m.ManyToManyField('TherapeuticArea', blank=True, related_name='resources')

    title = m.CharField(max_length=255)
    description = m.CharField(max_length=255, blank=True)
    zinc_number_global = m.CharField(max_length=255, blank=True)
    zinc_number_country = m.CharField(max_length=255, blank=True)

    url = m.URLField(max_length=255, blank=True)
    file = m.FileField(upload_to=make_resource_filepath, null=True, blank=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        return '{}(title="{}")'.format(self.__class__.__name__, self.name)


class TherapeuticArea(TimestampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    name = m.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{}(name="{}")'.format(self.__class__.__name__, self.name)


# Users/Auth Models
#####################################################################


class UserManager(SafeDeleteManager, DefaultUserManager):
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


class User(AbstractUser, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    objects = UserManager()

    # changed fields:
    username = None  # remove it as we login with email
    email = m.EmailField(_('email address'), unique=True)  # enforce unique

    # extra fields
    business_title = m.CharField(max_length=255, blank=True,
                                 help_text='Business position title, eg. "Medical Manager"')
    affiliate_groups = m.ManyToManyField(AffiliateGroup, blank=True, related_name='users')
    tas = m.ManyToManyField(TherapeuticArea, blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def has_interactions_perm(self, perm):
        """Helper to check our custom perms more succinctly.

        """
        return self.has_perm('interactionscore.' +
                             (perm if type(perm) is str else perm.name))
