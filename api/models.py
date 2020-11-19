import uuid
from pytz import all_timezones
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class APIUser(AbstractUser):
    """Custom user class"""
    ALL_TIMEZONES = ((name, name) for name in all_timezones)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'))
    company_id = models.UUIDField(default=uuid.uuid4)
    timezone = models.TextField(choices=ALL_TIMEZONES, default=settings.TIME_ZONE)
