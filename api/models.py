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
    email = models.EmailField(_("email address"))
    company_id = models.UUIDField(default=uuid.uuid4)
    timezone = models.TextField(choices=ALL_TIMEZONES, default=settings.TIME_ZONE)


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.TextField()
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.manager})"


class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="meetings",
        editable=False,
    )
    event_name = models.TextField()
    meeting_agenda = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    participant_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="participate"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.event_name} ({self.owner})"
